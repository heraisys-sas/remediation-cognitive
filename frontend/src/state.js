"use strict";
function createSessionState() {
  return {
  autoDictee: null,
  dicteeActive: null,
  dicteeAutoAutorisee: false,
  theme: null,
  session: null,
  indexItem: 0,
  repondu: false,
  debutQuestion: 0,
  confirmationFin: false,
  minuterieConfirmation: null,
  minuteriesMemo: [],
  indicesReveles: 0,
  optionChoisie: null,
  reponseSoumise: "",
  grille: null,
  jetonChoisi: null,
  enonceCourant: "",
  consignesVues: new Set(),
  consignesMemoVues: new Set(),
  consignesAudioVues: new Set(),
  seanceTerminee: false,
  reprisesAfficher: new Set(),
  reponsesAttendues: {},
  sequence: {},
  };
}
const etat = {
  memoGeneration: 0,
  actionEnCours: false,
  reessai: null,
  missions: [],
  missionActive: null,
  themesParId: new Map(),
  seance: createSessionState(),
};
// Façade maintenue pour les callbacks existants ; stockage de séance séparé.
for (const cle of Object.keys(etat.seance)) {
  Object.defineProperty(etat, cle, {
    get() { return etat.seance[cle]; },
    set(valeur) { etat.seance[cle] = valeur; },
  });
}
function resetSessionState() {
  etat.seance = createSessionState();
}
