/* Capacités du poste, côté client : dictée et synthèse vocale.
 *
 * On utilise ce que le système fournit — l'API du navigateur, qui s'appuie sur
 * les moteurs de l'OS (Siri sur Apple, moteur système sur Android/Windows).
 * Repli silencieux : si la capacité manque, on rend `false` et l'interface
 * masque le bouton — la saisie au clavier reste toujours possible.
 *
 * Portable : ce module ne dépend d'aucune bibliothèque ; une enveloppe native
 * (tablette) pourra le remplacer sans toucher au reste de l'interface.
 */
const Capacites = (() => {
  const Reconnaissance = window.SpeechRecognition || window.webkitSpeechRecognition || null;

  const voixDisponible = () => Boolean(Reconnaissance);
  const syntheseDisponible = () => typeof window.speechSynthesis !== "undefined"
    && typeof window.SpeechSynthesisUtterance !== "undefined";

  /** Écoute le micro et transcrit au fur et à mesure.
   *  `onPartiel(texte)` est appelé pendant la parole (texte provisoire),
   *  `onResultat(texte)` à la fin de la phrase (texte définitif). */
  function dicter({ onPartiel, onResultat, onDebut, onFin, onErreur } = {}) {
    if (!Reconnaissance) return null;
    const ecoute = new Reconnaissance();
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
    try {
      ecoute.start();
      if (onDebut) onDebut();
    } catch {
      if (onErreur) onErreur("indisponible");
      return null;
    }
    return ecoute;
  }

  // Garder une référence jusqu’à la fin : certains moteurs collectent sinon l’énoncé.
  let enonceActif = null;
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
  function textePourSynthese(texte) {
    return String(texte)
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
  function lire(texte, { onFin, onErreur } = {}) {
    if (!syntheseDisponible() || !texte) return false;
    const locales = voixLocales();
    const voix = locales.find(v => v.voiceURI === voixChoisie)
      || locales.find(v => v.native) || locales.find(v => v.default) || locales[0];
    if (!voix) { if (onErreur) onErreur("voix_locale_indisponible"); return false; }
    arreter();
    if (voix.native) {
      const generation = generationAudio;
      fetch('/api/capacites/synthese', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({texte:textePourSynthese(texte), voix:voix.native}),
      }).then(async r => {
        if (!r.ok) throw new Error('synthese');
        const audio = await r.json();
        if (generation === generationAudio) lireFichier(`data:${audio.mime};base64,${audio.audio_base64}`, {onFin,onErreur});
      }).catch(() => { if (generation === generationAudio && onErreur) onErreur('synthese'); });
      return true;
    }
    window.speechSynthesis.cancel();
    const enonce = new SpeechSynthesisUtterance(textePourSynthese(texte));
    enonce.lang = "fr-FR";
    enonce.rate = 0.95;
    enonceActif = enonce;
    enonce.voice = voix;
    enonce.onend = () => { if (enonceActif === enonce) enonceActif = null; if (onFin) onFin(); };
    enonce.onerror = (event) => { if (enonceActif === enonce) enonceActif = null; if (onErreur) onErreur(event.error); };
    window.speechSynthesis.speak(enonce);
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
    lecteurAudio.src = url;
    lecteurAudio.onended = () => { if (generation === generationAudio && onFin) onFin(); };
    lecteurAudio.onerror = () => { if (generation === generationAudio && onErreur) onErreur("audio"); };
    lecteurAudio.play().catch(() => { if (generation === generationAudio && onErreur) onErreur("lecture"); });
    return true;
  }

  const arreter = () => {
    generationAudio++;
    if (lecteurAudio) {
      lecteurAudio.onended = null;
      lecteurAudio.onerror = null;
      lecteurAudio.pause();
    }
    if (syntheseDisponible()) window.speechSynthesis.cancel();
  };

  return { voixDisponible, syntheseDisponible, dicter, lire, lireFichier, arreter,
    voixLocales, choisirVoix, choixVoix, chargerVoixLocales };
})();
