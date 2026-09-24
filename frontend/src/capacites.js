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

  /** Lit un texte à voix haute avec la voix du système. */
  function lire(texte) {
    if (!syntheseDisponible() || !texte) return false;
    window.speechSynthesis.cancel();
    const enonce = new SpeechSynthesisUtterance(String(texte));
    enonce.lang = "fr-FR";
    enonce.rate = 0.95;
    window.speechSynthesis.speak(enonce);
    return true;
  }

  const arreter = () => { if (syntheseDisponible()) window.speechSynthesis.cancel(); };

  return { voixDisponible, syntheseDisponible, dicter, lire, arreter };
})();
