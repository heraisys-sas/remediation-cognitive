/* Capacités du poste, côté client : dictée et synthèse vocale.
 *
 * La dictée privilégie le moteur Apple via le serveur loopback. Le repli
 * navigateur exige un moteur local et le pack français déjà disponible.
 * Aucun repli distant ni téléchargement automatique.
 *
 * Portable : ce module ne dépend d'aucune bibliothèque ; une enveloppe native
 * (tablette) pourra le remplacer sans toucher au reste de l'interface.
 */
const Capacites = (() => {
  const Reconnaissance = window.SpeechRecognition || window.webkitSpeechRecognition || null;

  const voixDisponible = () => (typeof DicteeNative !== "undefined" && DicteeNative.disponible()) || Boolean(Reconnaissance);
  const syntheseDisponible = () => typeof window.speechSynthesis !== "undefined"
    && typeof window.SpeechSynthesisUtterance !== "undefined";

  /** Écoute le micro et transcrit au fur et à mesure.
   *  `onPartiel(texte)` est appelé pendant la parole (texte provisoire),
   *  `onResultat(texte)` à la fin de la phrase (texte définitif). */
  function dicter({ onPartiel, onResultat, onDebut, onFin, onErreur, onTraitement } = {}) {
    if (typeof DicteeNative !== "undefined" && DicteeNative.disponible()) {
      return DicteeNative.demarrer({onPartiel,onResultat,onDebut,onFin,onErreur,onTraitement});
    }
    if (!Reconnaissance) { if (onErreur) onErreur("dictee_locale_indisponible"); return null; }
    const ecoute = new Reconnaissance();
    // Ne jamais démarrer un moteur qui ne sait pas garantir le mode local.
    if (!("processLocally" in ecoute) || typeof Reconnaissance.available !== "function") {
      if (onErreur) onErreur("dictee_locale_indisponible");
      return null;
    }
    ecoute.processLocally = true;
    ecoute.lang = "fr-FR";
    ecoute.interimResults = true;   // transcription au fur et à mesure
    ecoute.continuous = false;
    ecoute.maxAlternatives = 1;
    let definitif = "";
    ecoute.onresult = (evenement) => {
      let provisoire = "";
      for (let i = evenement.resultIndex; i < evenement.results.length; i++) {
        const morceau = evenement.results[i][0]?.transcript || "";
        if (evenement.results[i].isFinal) definitif += morceau;
        else provisoire += morceau;
      }
      const texte = (definitif + provisoire).trim();
      if (provisoire && onPartiel) onPartiel(texte);
      if (definitif.trim() && onResultat) onResultat(definitif.trim());
    };
    ecoute.onerror = (evenement) => { if (onErreur) onErreur(evenement.error || "erreur"); };
    ecoute.onend = () => { if (onFin) onFin(); };
    let annule = false;
    let minuterie;
    const controle = {
      abort() { annule = true; clearTimeout(minuterie); ecoute.abort(); },
      stop() { annule = true; clearTimeout(minuterie); ecoute.stop(); },
    };
    (async () => {
      try {
        const disponibilite = await Promise.race([
          Reconnaissance.available({ langs: ["fr-FR"], processLocally: true }),
          new Promise((_, rejet) => { minuterie = setTimeout(() => rejet(new Error("delai")), 3000); }),
        ]);
        if (annule) return;
        if (disponibilite !== "available" || ecoute.processLocally !== true) {
          if (onErreur) onErreur("dictee_locale_indisponible");
          return;
        }
        ecoute.start();
        if (onDebut) onDebut();
      } catch {
        if (!annule && onErreur) onErreur("dictee_locale_indisponible");
      } finally { clearTimeout(minuterie); }
    })();
    return controle;
  }

  async function autoriserDictee() {
    return typeof DicteeNative !== "undefined" && await DicteeNative.autoriser();
  }
  function libererPreparationDictee() {
    if (typeof DicteeNative !== "undefined") DicteeNative.libererPreparation();
  }

  // Préparer le matériel pendant la question, sans enregistrer sa lecture.
  function preparerDictee(options) {
    if (typeof DicteeNative !== "undefined" && DicteeNative.disponible()) {
      return DicteeNative.demarrer({ ...options, enAttente: true });
    }
    return null;
  }

  // Garder une référence jusqu’à la fin : certains moteurs collectent sinon l’énoncé.
  let enonceActif = null;
  let lectureActive = false;
  const abonnesLecture = new Set();
  function notifierLecture(active) {
    lectureActive = active;
    for (const abonne of abonnesLecture) abonne(active);
  }
  function observerLecture(abonne) {
    abonnesLecture.add(abonne);
    abonne(lectureActive);
    return () => abonnesLecture.delete(abonne);
  }
  const CLE_VOIX = "remediation.voixLocale";
  let voixChoisie = "";
  let voixNatives = [];
  try { voixChoisie = window.localStorage.getItem(CLE_VOIX) || ""; } catch {}
  const voixLocales = () => [...voixNatives, ...(syntheseDisponible()
    ? window.speechSynthesis.getVoices().filter(v => /^fr(?:[-_]|$)/i.test(v.lang) && v.localService
      && !/^(Eddy|Flo|Grandma|Grandpa|Reed|Rocko|Sandy|Shelley)\b/i.test(v.name || ""))
    : [])];
  async function chargerVoixLocales() {
    try {
      const r = await fetch('/api/capacites/voix');
      if (!r.ok) return;
      const donnees = await r.json();
      voixNatives = donnees.voix.map(v => ({name:v.nom, voiceURI:`macos:${v.id}`, lang:'fr-FR', localService:true, native:v.id}));
    } catch { /* Ancien serveur : les voix du navigateur restent disponibles. */ }
  }
  function choisirVoix(uri) {
    voixChoisie = uri;
    try { window.localStorage.setItem(CLE_VOIX, uri); } catch {}
  }
  const choixVoix = () => voixChoisie;

  /** Prépare une formulation orale sans modifier le texte affiché.
   *
   * Les moteurs Web Speech ne prononcent pas tous les opérateurs de la même
   * manière. On explicite uniquement les signes mathématiques ; un trait
   * d'union interne à un mot (``rendez-vous``) reste intact.
   */
  function textePourSynthese(texte, francais = false) {
    // Correction orale uniquement : certaines voix lisent cet homographe à l'anglaise.
    // Le découpage syllabique est limité au mot entier, jamais aux textes mixtes.
    const oral = francais
      ? String(texte).replace(/\btriangles?\b/gi, mot => mot.length === 9 ? "tri-angles" : "tri-angle")
      : String(texte);
    return oral
      .replace(/\?\s*(?=[+\-−×xX*÷=])/g, "quel nombre ")
      .replace(/([+\-−×xX*÷=])\s*\?/g, "$1 quel nombre")
      .replace(/\s*−\s*/g, " moins ")
      .replace(/\s+-\s+/g, " moins ")
      .replace(/\s*×\s*/g, " multiplié par ")
      .replace(/\s+[xX*]\s+/g, " multiplié par ")
      .replace(/\s*\+\s*/g, " plus ")
      .replace(/\s*=\s*/g, " égale ")
      .replace(/\s*÷\s*/g, " divisé par ")
      .replace(/\s+/g, " ")
      .trim();
  }

  /** Lit un texte à voix haute avec la voix du système. */
  function lire(texte, { onFin, onErreur, francais = false } = {}) {
    if (!syntheseDisponible() || !texte) return false;
    const locales = voixLocales();
    const voix = locales.find(v => v.voiceURI === voixChoisie)
      || locales.find(v => v.native) || locales.find(v => v.default) || locales[0];
    if (!voix) { if (onErreur) onErreur("voix_locale_indisponible"); return false; }
    arreter();
    notifierLecture(true);
    if (voix.native) {
      const generation = generationAudio;
      fetch('/api/capacites/synthese', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({texte:textePourSynthese(texte, francais), voix:voix.native}),
      }).then(async r => {
        if (!r.ok) throw new Error('synthese');
        const audio = await r.json();
        if (generation === generationAudio) lireFichier(`data:${audio.mime};base64,${audio.audio_base64}`, {onFin,onErreur});
      }).catch(() => { if (generation === generationAudio) { notifierLecture(false); if (onErreur) onErreur('synthese'); } });
      return true;
    }
    window.speechSynthesis.cancel();
    const enonce = new SpeechSynthesisUtterance(textePourSynthese(texte, francais));
    enonce.lang = "fr-FR";
    enonce.rate = 0.95;
    enonceActif = enonce;
    enonce.voice = voix;
    enonce.onend = () => { if (enonceActif !== enonce) return; enonceActif = null; notifierLecture(false); if (onFin) onFin(); };
    enonce.onerror = (event) => { if (enonceActif !== enonce) return; enonceActif = null; notifierLecture(false); if (onErreur) onErreur(event.error); };
    try { window.speechSynthesis.speak(enonce); }
    catch { enonceActif = null; notifierLecture(false); if (onErreur) onErreur("lecture"); return false; }
    return true;
  }

  let lecteurAudio = null;
  let generationAudio = 0;
  /** Lecture des mots préparés : même voix locale, sans dépendre de Web Speech. */
  function lireFichier(url, { onFin, onErreur } = {}) {
    if (typeof window.Audio === "undefined") return false;
    arreter();
    const generation = generationAudio;
    lecteurAudio ??= new window.Audio();
    notifierLecture(true);
    lecteurAudio.src = url;
    lecteurAudio.onended = () => { if (generation === generationAudio) { notifierLecture(false); if (onFin) onFin(); } };
    lecteurAudio.onerror = () => { if (generation === generationAudio) { notifierLecture(false); if (onErreur) onErreur("audio"); } };
    lecteurAudio.play().catch(() => { if (generation === generationAudio) { notifierLecture(false); if (onErreur) onErreur("lecture"); } });
    return true;
  }

  const arreter = () => {
    generationAudio++;
    enonceActif = null;
    notifierLecture(false);
    if (lecteurAudio) {
      lecteurAudio.onended = null;
      lecteurAudio.onerror = null;
      lecteurAudio.pause();
    }
    if (syntheseDisponible()) window.speechSynthesis.cancel();
  };

  return { voixDisponible, syntheseDisponible, dicter, preparerDictee, autoriserDictee, libererPreparationDictee, lire, lireFichier, arreter,
    voixLocales, choisirVoix, choixVoix, chargerVoixLocales, observerLecture,
    lectureEnCours: () => lectureActive };
})();
