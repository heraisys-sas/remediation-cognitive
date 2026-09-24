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

  /** Écoute le micro et appelle `onResultat(texte)` à la fin de la phrase. */
  function dicter({ onResultat, onDebut, onFin, onErreur } = {}) {
    if (!Reconnaissance) return null;
    const ecoute = new Reconnaissance();
    ecoute.lang = "fr-FR";
    ecoute.interimResults = false;
    ecoute.maxAlternatives = 1;
    ecoute.onresult = (evenement) => {
      const texte = evenement.results?.[0]?.[0]?.transcript || "";
      if (texte && onResultat) onResultat(texte.trim());
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
