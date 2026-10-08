"use strict";

function renderSequenceExercise(item) {
    rendreSequence(item);
    refs.carteFeedback.hidden = true;
    refs.boutonSuivant.hidden = true;
    etat.debutQuestion = Date.now();
    reglerEtatBoutons();
    // Les champs de la séquence remplacent entièrement la réponse générique.
    // Ne pas réafficher plus bas « Ta réponse » ni sa dictée.
    return true;

}

function renderFunctionalExercise(item) {
    refs.formulaire.hidden = true;
    refs.carteFeedback.hidden = true;
    refs.boutonSuivant.hidden = true;
    CAPACITES.arreter();
    refs.ligneAudio.hidden = true;
    rendreFonctionnel(item);
    etat.debutQuestion = Date.now();
    reglerEtatBoutons();
    return true;

}

function renderDeductionExercise(item) {
    refs.formulaire.hidden = true;
    refs.zoneChoix.hidden = true;
    refs.zoneIndices.hidden = true;
    refs.carteFeedback.hidden = true;
    refs.boutonSuivant.hidden = true;
    rendreGrille(item);
    reglerEtatBoutons();
    etat.debutQuestion = Date.now();
    const premier = refs.zoneGrille.querySelector(".jeton");
    if (premier) premier.focus();
    return true;

}

const defaultHandler = {
  readAnswer: (brut) => normaliserReponse(brut, etat.theme),
  renderFeedback: (resultat) => rendreFeedback(resultat),
};
const sequenceHandler = {
  render: renderSequenceExercise,
  readAnswer: (brut) => brut,
  renderFeedback: (resultat) => rendreFeedback(resultat),
};
const functionalHandler = { ...sequenceHandler, render: renderFunctionalExercise };
const deductionHandler = {
  render: renderDeductionExercise,
  readAnswer: () => etat.grille.join(";"),
  renderFeedback: (resultat) => rendreFeedbackGrille(resultat),
};
const EXERCISE_HANDLERS = {
  "grille-deduction": deductionHandler,
  "pqrst-mise-en-oeuvre": sequenceHandler,
  "rappel-libre": defaultHandler,
  "actualiser-consigne": functionalHandler,
  "comparer-documents": functionalHandler,
  "reperer-essentiel": functionalHandler,
  "reprise-interrompue": functionalHandler,
};
function handlerPour(item) {
  return EXERCISE_HANDLERS[item.type] || defaultHandler;
}
