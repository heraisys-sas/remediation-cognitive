"use strict";

/* =====================================================================
   Application — module Entraînement (Sprint 1)
   SPA vanilla sans build, servie par FastAPI sur /ui (même origine).
   Référence contractuelle : docs/30-technique/api-contract.md
   - endpoints : GET /themes · POST /{theme}/sessions
                 POST /{theme}/sessions/{sid}/reponses
                 POST /{theme}/sessions/{sid}/fin
   - la réponse attendue n'arrive jamais avant la soumission
     (correction côté serveur).
   Convention dépôt : identifiants en anglais, commentaires en français.
   Vocabulaire utilisateur : neutre, chaleureux, jamais clinique.
   ===================================================================== */

const API_BASE = "/api/entrainement";
const API_MISSIONS = "/api/missions";
const API_PROGRAMME = "/api/programme";

//: Types dont la réponse se choisit parmi des propositions (contenu.options).
const TYPES_A_CHOIX = new Set([
  "reconnaissance",
  "rappel-source",
  "emotion-vignette",
  "reponse-adaptee",
  "lecture-intention",
  "pqrst",
  "but-etapes",
  "auto-instruction",
  "plan-a-verifier",
  "etape-suivante",
  "si-alors",
  "par-ou-commencer",
  "meilleure-solution",
  "reperer-info",
  "gestion-du-temps",
  "aide-externe",
]);

//: Une consigne peut aussi être une stratégie lorsque son texte décrit une
//: démarche stable, et pas seulement l'action demandée sur l'item courant.
const TYPES_CONSIGNE_COMME_METHODE = new Set([
  "auto-instruction",
  "but-etapes",
  "plan-a-verifier",
  "reperer-info",
  "pqrst",
  "estimation-temps",
  "etape-suivante",
  "si-alors",
  "gestion-du-temps",
  "par-ou-commencer",
  "aide-externe",
  "meilleure-solution",
  "prise-message",
]);

//: Stratégies stables pour les familles où les items ne portent pas encore un
//: champ ``methode``. Aucun repli générique : une famille absente masque le panneau.
const METHODES_PAR_TYPE = Object.freeze({
  "grille-deduction": "Commence par les placements certains. Croise ensuite plusieurs indices et vérifie que chaque phrase reste respectée.",
  "empan": "Regroupe mentalement les chiffres par deux ou trois. Pour l’ordre inverse, repars du dernier groupe.",
  "empan-mots": "Relie les mots par une petite scène mentale en gardant leur ordre. Pour l’ordre inverse, reparcours la scène depuis la fin.",
  "n-back": "Garde une place mentale pour chaque élément. À la fin, remonte du nombre de positions demandé.",
  "paires-associatives": "Crée pour chaque mot et son nombre une image ou un lien inhabituel, puis retrouve ce lien au rappel.",
  "rappel-libre": "Pendant la présentation, regroupe les mots qui peuvent former une image ou une histoire. Au rappel, reparcours ces groupes.",
  "rappel-indice": "Cherche d’abord la catégorie et un contexte où tu emploies ce mot. Si nécessaire, révèle les indices un par un.",
  "rappel-source": "Associe l’information à un détail distinctif de son contexte, puis reconstruis ce contexte au moment du rappel.",
});

//: Thèmes d'appoint regroupés dans la section « Extra » de l'écran d'accueil.
const THEMES_EXTRA = new Set(["python", "anglais"]);

//: Capacités du poste (voix, synthèse) — repli neutre si le module est absent.
const CAPACITES = (typeof Capacites !== "undefined")
  ? Capacites
  : { voixDisponible: () => false, syntheseDisponible: () => false,
      dicter: () => null, lire: () => false, arreter: () => {} };

//: Lecture automatique : activée par défaut, désactivable, et gardée d'une séance à l'autre.
const CLE_LECTURE_AUTO = "remediation.lectureAuto";
function lectureAutoActivee() {
  try { return window.localStorage.getItem(CLE_LECTURE_AUTO) !== "off"; }
  catch { return true; }
}
function definirLectureAuto(active) {
  try { window.localStorage.setItem(CLE_LECTURE_AUTO, active ? "on" : "off"); } catch { /* stockage indisponible */ }
}
/** Lit le texte seulement si la lecture automatique est active. */
function lireSiLectureAuto(texte) {
  if (texte && lectureAutoActivee() && CAPACITES.syntheseDisponible()) CAPACITES.lire(texte);
}

//: Dérogation explicite au plafond de séances du jour (entraînements — ADR-021).
//: Désactivée par défaut ; conservée d'une visite à l'autre, comme la lecture automatique.
const CLE_SANS_LIMITE = "remediation.sansLimiteSessions";
function sansLimiteActivee() {
  try { return window.localStorage.getItem(CLE_SANS_LIMITE) === "on"; }
  catch { return false; }
}
function definirSansLimite(active) {
  try { window.localStorage.setItem(CLE_SANS_LIMITE, active ? "on" : "off"); } catch { /* stockage indisponible */ }
}

//: Valeur de repli pour toute séquence à mémoriser. Le contenu explicite aussi
//: cette pause ; le repli évite qu'un ancien item soit présenté trop vite.
const BLANC_INTER_ITEM_MS = 2000;

/* ---------------------------------------------------------------------
   Raccourcis DOM (l'HTML statique porte toutes les vues)
   --------------------------------------------------------------------- */

const $ = (id) => document.getElementById(id);

const refs = {
  vues: {
    themes: $("vue-themes"),
    seance: $("vue-seance"),
    resume: $("vue-resume"),
    missions: $("vue-missions"),
    programme: $("vue-programme"),
    reperes: $("vue-reperes"),
  },
  titres: {
    themes: $("titre-themes"),
    seance: $("titre-seance"),
    resume: $("titre-resume"),
    missions: $("titre-missions"),
    programme: $("titre-programme"),
    reperes: $("titre-reperes"),
  },
  bandeau: $("bandeau-erreur"),
  bandeauMessage: $("bandeau-message"),
  boutonReessayer: $("bouton-reessayer"),
  boutonRetourThemes: $("bouton-retour-themes"),
  noticeThemes: $("notice-themes"),
  caseSansLimite: $("case-sans-limite"),
  noteSansLimite: $("note-sans-limite"),
  listeThemes: $("liste-themes"),
  sectionEvaluation: $("section-evaluation"),
  listeThemesEvaluation: $("liste-themes-evaluation"),
  sectionExtra: $("section-extra"),
  listeThemesExtra: $("liste-themes-extra"),
  progressionTexte: $("progression-texte"),
  barreProgression: $("barre-progression"),
  barreRemplie: $("barre-remplie"),
  enonce: $("enonce"),
  zoneMemo: $("zone-memo"),
  zoneChoix: $("zone-choix"),
  zoneIndices: $("zone-indices"),
  zoneGrille: $("zone-grille"),
  zoneGeneration: $("zone-generation"),
  zoneAide: $("zone-aide"),
  texteAide: $("texte-aide"),
  formulaire: $("formulaire-reponse"),
  champReponse: $("champ-reponse"),
  indiceReponse: $("indice-reponse"),
  boutonValider: $("bouton-valider"),
  carteFeedback: $("carte-feedback"),
  boutonSuivant: $("bouton-suivant"),
  boutonTerminer: $("bouton-terminer"),
  carteArret: $("carte-arret"),
  statsResume: $("stats-resume"),
  ligneSeancesRestantes: $("ligne-seances-restantes"),
  boutonNouvelleSeance: $("bouton-nouvelle-seance"),
  boutonMissions: $("bouton-missions"),
  listeMissions: $("liste-missions"),
  zoneNoteMission: $("zone-note-mission"),
  titreNote: $("titre-note"),
  champNote: $("champ-note"),
  champRessenti: $("champ-ressenti"),
  boutonEnregistrerNote: $("bouton-enregistrer-note"),
  messageNote: $("message-note"),
  journalMissions: $("journal-missions"),
  boutonRetourJournal: $("bouton-retour-journal"),
  boutonProgramme: $("bouton-programme"),
  planJour: $("plan-jour"),
  semainesProgramme: $("semaines-programme"),
  reglesProgramme: $("regles-programme"),
  boutonRetourProgramme: $("bouton-retour-programme"),
  boutonReperes: $("bouton-reperes"),
  boutonRetourReperes: $("bouton-retour-reperes"),
  boutonDicter: $("bouton-dicter"),
  boutonEcouter: $("bouton-ecouter"),
  ligneAudio: $("ligne-audio"),
  caseLectureAuto: $("case-lecture-auto"),
  rappelConsigne: $("rappel-consigne"),
  noteReprise: $("note-reprise"),
  zoneSequence: $("zone-sequence"),
  methodeExercice: $("methode-exercice"),
  panneauMethode: $("panneau-methode"),
  titreMethode: $("titre-methode"),
};

/* ---------------------------------------------------------------------
   État applicatif (une seule page, trois écrans)
   --------------------------------------------------------------------- */

const etat = {
  theme: null,             // thème courant : { id, nom, description }
  session: null,           // réponse de POST /{theme}/sessions
  indexItem: 0,            // item actuellement affiché
  repondu: false,          // item courant déjà validé (attente de « Suivant »)
  debutQuestion: 0,        // horodatage d'affichage → temps_ms
  actionEnCours: false,    // verrou anti double-soumission
  confirmationFin: false,  // « Terminer » en deux temps (évite les accidents)
  minuterieConfirmation: null,
  reessai: null,           // action à relancer après une erreur réseau
  minuteriesMemo: [],      // minuteries de la phase de mémorisation
  indicesReveles: 0,       // indices consultés sur l'item courant (0 = sans aide)
  optionChoisie: null,     // proposition choisie (types à choix)
  missions: [],            // missions hors écran chargées du serveur
  missionActive: null,     // mission en cours de notation
  reponseSoumise: "",      // dernière réponse envoyée (comparaison d'affichage)
  themesParId: new Map(),  // thèmes indexés par identifiant (écran programme)
  grille: null,            // grille de déduction : 9 cases (jeton « figure:couleur » ou null)
  jetonChoisi: null,       // jeton de la palette actuellement sélectionné
  enonceCourant: "",       // ce qui est affiché à l'écran (pour « Écouter »)
  consignesVues: new Set(), // rappels de méthode déjà affichés (une fois par type)
  consignesMemoVues: new Set(), // consignes de mémorisation déjà rencontrées (texte exact)
  consignesAudioVues: new Set(), // consignes déjà dites automatiquement (texte exact)
  seanceTerminee: false,   // séance clôturée par la durée maximale (aller au résumé)
  reprisesAfficher: new Set(), // exercices qui reviennent en reprise (réponse à montrer)
  reponsesAttendues: {},   // réponse attendue par item, retenue du retour serveur
  sequence: {},            // réponses en cours d'une séquence guidée (par étape)
};

/* ---------------------------------------------------------------------
   Utilitaires
   --------------------------------------------------------------------- */

/** Crée un élément avec classes / texte / attributs, enfants ajoutés après. */
function creerElement(balise, options = {}, ...enfants) {
  const element = document.createElement(balise);
  if (options.classe) element.className = options.classe;
  if (options.texte !== undefined) element.textContent = options.texte;
  if (options.attributs) {
    for (const [cle, valeur] of Object.entries(options.attributs)) {
      element.setAttribute(cle, valeur);
    }
  }
  for (const enfant of enfants) {
    if (enfant !== null && enfant !== undefined) element.append(enfant);
  }
  return element;
}

/** Défilement vers le haut, instantané si l'utilisateur refuse le mouvement. */
function revenirEnHaut() {
  const reduireMouvement = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  window.scrollTo({ top: 0, behavior: reduireMouvement ? "auto" : "smooth" });
}

/** Change d'écran, replace le focus sur le titre de la vue (accessibilité). */
function afficherVue(nom) {
  for (const [cle, section] of Object.entries(refs.vues)) {
    section.hidden = cle !== nom;
  }
  refs.titres[nom].focus({ preventScroll: true });
  revenirEnHaut();
}

/**
 * Règle l'état des boutons d'action d'après la situation :
 * - pendant un échange réseau : tout est désactivé ;
 * - question en cours : « Valider » et « Terminer » actifs ;
 * - réponse validée : « Suivant » et « Terminer » actifs.
 */
function reglerEtatBoutons() {
  const enVol = etat.actionEnCours;
  refs.boutonValider.disabled = enVol || etat.repondu;
  refs.boutonSuivant.disabled = enVol || !etat.repondu;
  refs.boutonTerminer.disabled = enVol;
}

/** Formate une durée en secondes → « 45 s » ou « 7 min 05 s ». */
function formaterDuree(secondes) {
  if (!Number.isFinite(secondes) || secondes < 0) return "—";
  const minutes = Math.floor(secondes / 60);
  const reste = Math.round(secondes % 60);
  if (minutes === 0) return `${reste} s`;
  return `${minutes} min ${String(reste).padStart(2, "0")} s`;
}

/** Formate un taux de réussite (0–1) → « 75 % », sans jugement. */
function formaterTaux(taux) {
  if (!Number.isFinite(taux)) return "—";
  return `${Math.round(taux * 100)} %`;
}

/** Clavier adapté au type d'item (numérique quand la réponse est un nombre). */
const TYPES_REPONSE_NUMERIQUE = new Set([
  "production",
  "empan", "paires-associatives", "estimation-temps",
]);

function inputmodePour(type) {
  return TYPES_REPONSE_NUMERIQUE.has(type) ? "numeric" : "text";
}

/** Clé de comparaison d'un mot : minuscules, sans accents (tolérance de saisie). */
function clefMot(texte) {
  return String(texte ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

/** Découpe une réponse libre en mots (virgules, espaces, points-virgules…). */
function motsDe(texte) {
  return String(texte ?? "")
    .split(/[^0-9A-Za-z\u00C0-\u024F']+/)
    .filter(Boolean)
    .map(clefMot);
}

/** Annule les minuteries de la phase de mémorisation et masque la zone. */
function annulerMemo() {
  etat.memoGeneration = (etat.memoGeneration || 0) + 1;
  CAPACITES.arreter();
  for (const minuterie of etat.minuteriesMemo) {
    // Les identifiants sont partagés entre timeouts et intervals : on nettoie
    // les deux (sinon un compte à rebours de rappel différé survivrait au
    // changement d'écran).
    clearTimeout(minuterie);
    clearInterval(minuterie);
  }
  etat.minuteriesMemo = [];
  refs.zoneMemo.hidden = true;
  refs.zoneMemo.replaceChildren();
}

/**
 * Normalise la saisie pour le corps de POST /reponses (contrat : str | number).
 * Thème calcul-mental : saisie numérique → nombre.
 * Sinon (anglais, mémoire, prédiction de sortie…) on envoie la chaîne brute.
 */
function normaliserReponse(brut, theme) {
  const texte = brut.trim();
  if (
    theme && theme.id === "calcul-mental"
    && /^-?\d+(?:[.,]\d+)?$/.test(texte)
  ) {
    const nombre = Number(texte.replace(",", "."));
    if (Number.isFinite(nombre)) return nombre;
  }
  return texte;
}

/* ---------------------------------------------------------------------
   Couche API — fetch relatif (même origine), erreurs typées
   --------------------------------------------------------------------- */

/**
 * Appelle l'API et renvoie le JSON décodé.
 * Lance une erreur typée : { type: "reseau" } ou { type: "api", status, donnees }.
 */
async function apiFetch(chemin, options = {}) {
  let reponse;
  try {
    const entetes = { "Accept": "application/json" };
    if (options.body !== undefined) entetes["Content-Type"] = "application/json";
    reponse = await fetch(API_BASE + chemin, { ...options, headers: entetes });
  } catch {
    const erreur = new Error("réseau indisponible");
    erreur.type = "reseau";
    throw erreur;
  }

  let donnees = null;
  try { donnees = await reponse.json(); } catch { /* corps non JSON toléré */ }

  if (!reponse.ok) {
    const erreur = new Error(`API ${reponse.status}`);
    erreur.type = "api";
    erreur.status = reponse.status;
    erreur.donnees = donnees;
    throw erreur;
  }
  return donnees;
}

/* ---------------------------------------------------------------------
   Bandeau d'incident + notices
   --------------------------------------------------------------------- */

function masquerBandeau() {
  refs.bandeau.hidden = true;
  refs.boutonReessayer.hidden = true;
  refs.boutonRetourThemes.hidden = true;
  refs.boutonReessayer.onclick = null;
  refs.boutonRetourThemes.onclick = null;
  etat.reessai = null;
}

/**
 * Affiche le bandeau discret et rechargeable.
 * - reessayer : fonction à relancer (bouton « Réessayer ») ;
 * - retour    : propose « Retour aux thèmes » quand réessayer est inutile.
 */
function afficherBandeau(message, { reessayer = null, retour = false } = {}) {
  etat.reessai = reessayer;
  refs.bandeauMessage.textContent = message;
  refs.boutonReessayer.hidden = !reessayer;
  refs.boutonReessayer.onclick = reessayer
    ? () => { masquerBandeau(); reessayer(); }
    : null;
  refs.boutonRetourThemes.hidden = !retour;
  refs.boutonRetourThemes.onclick = retour
    ? () => { masquerBandeau(); revenirAuxThemes(); }
    : null;
  refs.bandeau.hidden = false;
}

/** Message réseau standard, calme et rechargeable. */
function afficherErreurReseau(reessayer) {
  afficherBandeau(
    "Petit souci de connexion — vérifie le serveur, puis réessaie.",
    { reessayer }
  );
}

/** Notice calme sur l'écran des thèmes (limite de séances, séance vide…). */
function montrerNoticeThemes(message) {
  refs.noticeThemes.textContent = message;
  refs.noticeThemes.hidden = false;
}

function masquerNoticeThemes() {
  refs.noticeThemes.hidden = true;
  refs.noticeThemes.textContent = "";
}

/** Réglage d'accueil « dépasser la limite » : reflète l'état (texte d'accompagnement). */
function majReglageSansLimite() {
  if (!refs.noteSansLimite) return;
  refs.noteSansLimite.textContent = sansLimiteActivee()
    ? "Limite levée — tu décides quand t’arrêter."
    : "Tous les exercices.";
}

/** Réinitialise la confirmation en deux temps de « Terminer ». */
function reinitialiserConfirmationFin() {
  etat.confirmationFin = false;
  if (etat.minuterieConfirmation) {
    clearTimeout(etat.minuterieConfirmation);
    etat.minuterieConfirmation = null;
  }
  refs.boutonTerminer.textContent = "Terminer la séance";
}

/* ---------------------------------------------------------------------
   Écran 1 — choix du thème (GET /themes)
   --------------------------------------------------------------------- */

async function chargerThemes() {
  if (etat.actionEnCours) return;
  etat.actionEnCours = true;

  masquerNoticeThemes();
  refs.listeThemes.replaceChildren(
    creerElement("p", { classe: "ligne-discrete", texte: "Chargement…" })
  );
  refs.listeThemesEvaluation.replaceChildren();
  refs.listeThemesExtra.replaceChildren();
  refs.sectionEvaluation.hidden = true;
  refs.sectionExtra.hidden = true;

  try {
    const donnees = await apiFetch("/themes");
    masquerBandeau();
    rendreThemes(donnees.themes || []);
  } catch (erreur) {
    refs.listeThemes.replaceChildren();
    refs.listeThemesEvaluation.replaceChildren();
    refs.listeThemesExtra.replaceChildren();
    refs.sectionEvaluation.hidden = true;
    refs.sectionExtra.hidden = true;
    if (erreur.type === "reseau") {
      afficherErreurReseau(chargerThemes);
    } else {
      afficherBandeau("Impossible de charger les thèmes pour le moment.", {
        reessayer: chargerThemes,
      });
    }
  } finally {
    etat.actionEnCours = false;
  }
}

function rendreThemes(themes) {
  refs.listeThemes.replaceChildren();
  refs.listeThemesEvaluation.replaceChildren();
  refs.listeThemesExtra.replaceChildren();
  refs.sectionEvaluation.hidden = true;
  refs.sectionExtra.hidden = true;
  masquerNoticeThemes();

  if (!themes.length) {
    montrerNoticeThemes("Aucun thème disponible pour le moment — reviens bientôt.");
    return;
  }

  // Déduction et Calcul mental ouvrent la liste ; les autres gardent leur ordre.
  const prioritaires = ["deduction", "calcul-mental"];
  const themesOrdonnes = [
    ...prioritaires.flatMap(id => themes.filter(theme => theme.id === id)),
    ...themes.filter(theme => !prioritaires.includes(theme.id)),
  ];
  for (const theme of themesOrdonnes) {
    if (theme.id === "series-entendues") continue;
    let cible = refs.listeThemes;
    if (THEMES_EXTRA.has(theme.id)) cible = refs.listeThemesExtra;
    else if (["evaluation", "cible"].includes(theme.categorie)) cible = refs.listeThemesEvaluation;
    const carte = carteTheme(theme, theme.id === "rappel-series"
      ? themes.find(t => t.id === "series-entendues") : null);
    cible.append(carte);
  }
  refs.sectionEvaluation.hidden = !refs.listeThemesEvaluation.childElementCount;
  refs.sectionExtra.hidden = !refs.listeThemesExtra.childElementCount;
}

/** Carte cliquable d'un thème : nom, description, bouton « Commencer ». */
function carteTheme(theme, parcoursAudio = null) {
  const carte = creerElement("article", { classe: "carte-theme" },
    creerElement("h3", { texte: theme.nom }),
    creerElement("p", { texte: theme.description || "" })
  );

  let themeChoisi = theme;
  let parcoursChoisi = null;
  let selecteurParcours = null;
  let descriptionParcours = null;
  let choix = null;

  function majPaliers() {
    if (!choix) return;
    const definition = (themeChoisi.parcours || []).find(p => p.id === parcoursChoisi);
    const paliers = definition?.paliers || themeChoisi.paliers || [];
    choix.replaceChildren(creerElement("option", {
      texte: definition?.palier_depart > 1
        ? `Palier : auto — départ ${definition.palier_depart}`
        : "Palier : auto",
      attributs: { value: "" },
    }));
    for (const palier of paliers) choix.append(creerElement("option", {
      texte: `Essai — palier ${palier}`, attributs: { value: String(palier) },
    }));
    choix.hidden = paliers.length <= 1;
  }

  function majParcours() {
    if (!selecteurParcours) return;
    const parcours = themeChoisi.parcours || [];
    selecteurParcours.replaceChildren(...parcours.map(definition => creerElement("option", {
      texte: definition.nom, attributs: { value: definition.id },
    })));
    parcoursChoisi = parcours[0]?.id || null;
    selecteurParcours.hidden = parcours.length <= 1;
    const definition = parcours[0];
    descriptionParcours.textContent = definition?.description || "Chaque parcours a sa propre progression.";
    majPaliers();
  }

  if (parcoursAudio) {
    const selecteur = creerElement("select", { classe: "selecteur-palier",
      attributs: { "aria-label": "Parcours de mémorisation" } });
    selecteur.append(creerElement("option", { texte: "Mots lus", attributs: { value: theme.id } }),
      creerElement("option", { texte: "Mots entendus", attributs: { value: parcoursAudio.id } }));
    selecteur.addEventListener("change", () => {
      themeChoisi = selecteur.value === parcoursAudio.id ? parcoursAudio : theme;
      majParcours();
    });
    carte.append(selecteur, creerElement("p", { classe: "ligne-discrete",
      texte: "La progression est distincte dans chaque parcours." }));
  }

  if ((theme.parcours || []).length || (parcoursAudio?.parcours || []).length) {
    selecteurParcours = creerElement("select", { classe: "selecteur-palier",
      attributs: { "aria-label": `Parcours pour ${theme.nom}` } });
    descriptionParcours = creerElement("p", { classe: "ligne-discrete" });
    selecteurParcours.addEventListener("change", () => {
      parcoursChoisi = selecteurParcours.value || null;
      const definition = (themeChoisi.parcours || []).find(p => p.id === parcoursChoisi);
      descriptionParcours.textContent = definition?.description || "Progression indépendante.";
      majPaliers();
    });
    carte.append(selecteurParcours, descriptionParcours);
  }

  // Sélecteur de palier — **outil d'essai**. « auto » suit la progression : c'est le
  // fonctionnement normal. Choisir un palier ne fait jamais reculer la progression.
  choix = creerElement("select", {
    classe: "selecteur-palier",
    attributs: { "aria-label": `Palier d'essai pour ${theme.nom}` },
  });
  carte.append(choix);
  majParcours();
  majPaliers();

  const bouton = creerElement("button", {
    classe: "bouton bouton-primaire",
    texte: "Commencer",
    attributs: { type: "button" },
  });
  bouton.addEventListener("click", () => demarrerSession(
    themeChoisi, choix && choix.value ? Number(choix.value) : null, parcoursChoisi
  ));
  carte.append(bouton);
  return carte;
}

/** Repli sûr vers l'écran des thèmes (après incident ou fin de séance). */
function revenirAuxThemes() {
  annulerMemo();
  etat.theme = null;
  etat.session = null;
  etat.repondu = false;
  reinitialiserConfirmationFin();
  afficherVue("themes");
  chargerThemes();
}

/* ---------------------------------------------------------------------
   Démarrage de séance (POST /{theme}/sessions)
   --------------------------------------------------------------------- */

async function demarrerSession(theme, palier = null, parcours = null) {
  if (etat.actionEnCours) return;
  etat.actionEnCours = true;
  reglerEtatBoutons();

  try {
    // Essai sur un palier précis : le choix part dans le corps JSON (contrat
    // « DemarrageOptionnel » du serveur). En mode auto (palier null), rien n'est
    // envoyé pour le palier : le serveur suit la progression, comportement inchangé.
    // Dérogation « dépasser la limite » (si activée en accueil) : même corps — le
    // serveur ne l'accorde qu'aux thèmes d'entraînement (ADR-021).
    const corps = {};
    if (palier !== null) corps.palier = palier;
    if (parcours !== null) corps.parcours = parcours;
    if (sansLimiteActivee()) corps.sans_limite_sessions = true;
    const options = { method: "POST" };
    if (Object.keys(corps).length > 0) {
      options.body = JSON.stringify(corps);
    }
    const donnees = await apiFetch(
      `/${encodeURIComponent(theme.id)}/sessions`,
      options
    );
    masquerBandeau();

    if (!donnees.items || donnees.items.length === 0) {
      // Séance vide : on clôture proprement en tâche de fond (la séance
      // a été créée côté serveur) puis on informe calmement.
      cloreSessionSilencieusement(theme, donnees.session_id);
      montrerNoticeThemes("Rien à réviser pour l’instant — ta prochaine séance arrive au bon moment.");
      return;
    }

    etat.theme = theme;
    etat.session = donnees;
    etat.seanceTerminee = false;
    etat.reprisesAfficher = new Set();
    etat.reponsesAttendues = {};
    etat.consignesMemoVues = new Set();
    etat.consignesAudioVues = new Set();
    etat.indexItem = 0;
    etat.repondu = false;
    reinitialiserConfirmationFin();
    masquerNoticeThemes();
    preparerEcranSeance();
    afficherVue("seance");
    montrerItem();
  } catch (erreur) {
    if (erreur.type === "api" && erreur.status === 429) {
      // Limite de séances atteinte : message calme, le repos fait partie du plan.
      // L'évaluation est plafonnée à une mesure par semaine (la dérogation la lève — ADR-021).
      montrerNoticeThemes(
        theme.categorie === "evaluation"
          ? "Le nombre de séances prévu cette semaine est atteint."
          : "Trois séances déjà faites aujourd’hui — le repos fait partie de l’entraînement."
      );
    } else if (erreur.type === "reseau") {
      afficherErreurReseau(() => demarrerSession(theme, palier, parcours));
    } else {
      afficherBandeau("Impossible de démarrer la séance pour le moment.", {
        reessayer: () => demarrerSession(theme, palier, parcours),
      });
    }
  } finally {
    etat.actionEnCours = false;
    reglerEtatBoutons();
  }
}

/** POST /fin sans attendre (séance vide) — les erreurs sont ignorées. */
function cloreSessionSilencieusement(theme, sessionId) {
  if (!sessionId) return;
  apiFetch(`/${encodeURIComponent(theme.id)}/sessions/${encodeURIComponent(sessionId)}/fin`, {
    method: "POST",
  }).catch(() => { /* rien à signaler : l'utilisateur n'a rien à faire */ });
}

/* ---------------------------------------------------------------------
   Écran 2 — séance, une question à la fois
   --------------------------------------------------------------------- */

function preparerEcranSeance() {
  refs.titres.seance.textContent = etat.theme.nom;
  refs.carteFeedback.hidden = true;
  refs.boutonSuivant.hidden = true;
  masquerBandeau();
}

/** Affiche l'item courant : progression, puis phase mémo ou question directe. */
function methodePourItem(item) {
  const contenu = item.contenu || {};
  if (item.type === "analyse-mot") return String(contenu.consigne || "").trim();
  if (typeof contenu.methode === "string" && contenu.methode.trim()) {
    return contenu.methode.trim();
  }
  if (TYPES_CONSIGNE_COMME_METHODE.has(item.type)) {
    return String(contenu.consigne || "").trim();
  }
  return METHODES_PAR_TYPE[item.type] || "";
}

/** Le coup de pouce général est inutile sur une grille : la méthode et l'aide
 * graduée propre aux indices couvrent déjà le besoin sans ajouter un panneau. */
function aideGeneriquePourItem(item) {
  if (item.type === "grille-deduction") return "";
  return typeof item.contenu?.aide === "string" ? item.contenu.aide.trim() : "";
}

/** Texte complet envoyé à la synthèse pour une grille dont l'énoncé visible est
 * construit à partir d'indices structurés plutôt que de ``contenu.enonce``. */
function textePourLectureDeduction(
  contenu,
  inclureConsigne = true,
  formateur = formaterEnonce,
) {
  const n = Array.isArray(contenu.figures) ? contenu.figures.length : 3;
  const indices = Array.isArray(contenu.enonces)
    ? contenu.enonces.map((indice) => formateur(indice, n)).filter(Boolean)
    : [];
  return [inclureConsigne ? contenu.consigne : "", indices.length ? "Indices." : "", ...indices]
    .filter(Boolean)
    .join(" ");
}

/** Pour l'enchaînement automatique, ne répète pas une consigne déjà entendue
 * dans la séance. Une action explicite sur « Écouter » utilise toujours le
 * texte complet conservé dans ``etat.enonceCourant``. */
function texteAutomatiquePourDeduction(
  contenu,
  consignesLues = etat.consignesAudioVues,
  formateur = formaterEnonce,
) {
  const consigne = String(contenu.consigne || "").trim();
  const dejaLue = Boolean(consigne && consignesLues.has(consigne));
  if (consigne) consignesLues.add(consigne);
  return textePourLectureDeduction(contenu, !dejaLue, formateur);
}

function montrerItem() {
  const items = etat.session.items;
  const item = items[etat.indexItem];
  const total = items.length;
  etat.repondu = false;
  etat.indicesReveles = 0;
  etat.optionChoisie = null;
  if (etat.indexItem === 0) etat.consignesVues = new Set();  // rappels par séance
  refs.rappelConsigne.hidden = true;
  refs.noteReprise.hidden = true;
  // Une méthode n'est affichée que si elle apporte une démarche propre à la
  // tâche. Une consigne générique permanente ajouterait de la charge sans guider.
  const methode = methodePourItem(item);
  refs.panneauMethode.open = false;
  refs.panneauMethode.hidden = !methode;
  refs.titreMethode.textContent = "Une méthode possible";
  refs.methodeExercice.textContent = methode || "";
  refs.methodeExercice.hidden = !methode;
  annulerMemo();

  // Progression discrète : « Question n sur max » + fine barre.
  refs.progressionTexte.textContent = `Question ${etat.indexItem + 1} sur ${total}`;
  refs.barreProgression.setAttribute("aria-valuemax", String(total));
  refs.barreProgression.setAttribute("aria-valuenow", String(etat.indexItem + 1));
  refs.barreRemplie.style.width = `${((etat.indexItem + 1) / total) * 100}%`;

  const contenu = item.contenu || {};
  // Reprise errorless : l'exercice revient une fois, la réponse est fournie avant le
  // nouvel essai (on ré-encode la bonne réponse, on ne ré-encode pas l'erreur).
  if (etat.reprisesAfficher.has(item.id)) {
    etat.reprisesAfficher.delete(item.id);
    const attendue = etat.reponsesAttendues[item.id];
    refs.noteReprise.textContent = attendue
      ? `Reprise — la réponse est « ${attendue} ». Il s'agit de la réancrer, pas de la deviner.`
      : "Reprise — cet exercice revient une fois, avec la réponse.";
    refs.noteReprise.hidden = false;
  }
  if (contenu.affichage) {
    // Exercices de mémorisation : consigne → stimulus temporisé → question.
    afficherPhaseMemo(item);
    return;
  }
  afficherQuestion(item);
}

/** Phase de mémorisation : la consigne est posée, le stimulus attend le signal. */
/** Vide toutes les zones de réponse : aucune trace du test précédent ne doit
 *  rester visible, pas même pendant la phase de mémorisation où l'on ne répond
 *  pas encore. Régression constatée : en changeant de rubrique, les propositions
 *  du test précédent restaient affichées sous le nouveau test. */
function viderZonesReponse() {
  for (const zone of [refs.zoneChoix, refs.zoneIndices, refs.zoneGeneration, refs.zoneGrille,
                      refs.zoneSequence]) {
    zone.replaceChildren();
    zone.hidden = true;
  }
}

function afficherPhaseMemo(item) {
  viderZonesReponse();
  const contenu = item.contenu || {};
  const affichage = contenu.affichage;
  const estSequence = affichage.mode === "sequence";
  const estSeries = affichage.mode === "series";
  const audio = affichage.modalite === "auditive";
  const parElement = (affichage.duree_par_item_ms + (affichage.pause_item_ms ?? BLANC_INTER_ITEM_MS)) / 1000;
  const nbElements = estSeries
    ? affichage.series.reduce((total, serie) => total + serie.length, 0)
    : affichage.elements.length;
  const mention = audio ? `${nbElements} mots · 2 s de pause après chaque mot entendu` : estSequence || estSeries
    ? `${nbElements} éléments · un toutes les ${parElement.toFixed(2).replace(".", ",")} s`
    : `${affichage.elements.length} paires · environ ${Math.round(affichage.duree_totale_ms / 1000)} s`;

  // Consigne dans la carte énoncé ; le stimulus reste masqué jusqu'au signal
  // de l'utilisateur (set attentionnel : on sait quoi chercher avant de voir).
  // La consigne de méthode n'est affichée qu'UNE fois par type dans la séance :
  // ensuite une phrase courte suffit (la répétition serait rébarbative).
  const consigneComplete = String(contenu.consigne || "").trim();
  const cleConsigne = consigneComplete || (audio
    ? "Mémorise les mots entendus."
    : "Mémorise le contenu affiché.");
  const consigneDejaVue = etat.consignesMemoVues.has(cleConsigne);
  const consigneAffichee = (consigneComplete && !consigneDejaVue)
    ? consigneComplete
    : audio ? "Mémorise les mots entendus." : "Mémorise le contenu affiché.";
  etat.consignesMemoVues.add(cleConsigne);
  refs.enonce.textContent = consigneAffichee;
  refs.enonce.className = "enonce";
  // « Écouter » lit ce qui est affiché à ce stade : la consigne, pas la question.
  etat.enonceCourant = consigneAffichee;
  refs.ligneAudio.hidden = !CAPACITES.syntheseDisponible();
  refs.rappelConsigne.hidden = true;
  // Le texte reste visible à chaque item, mais une consigne identique n'est lue
  // automatiquement qu'à sa première occurrence dans la séance. Le bouton
  // « Écouter » reste disponible si la personne souhaite l'entendre à nouveau.
  if (!consigneDejaVue) lireSiLectureAuto(consigneAffichee);
  refs.zoneAide.hidden = true;
  refs.carteFeedback.hidden = true;
  refs.boutonSuivant.hidden = true;
  refs.formulaire.hidden = true;

  const boutonAfficher = creerElement("button", {
    classe: "bouton bouton-primaire bouton-large",
    texte: audio ? "Écouter la série" : "Afficher",
    attributs: { type: "button" },
  });
  boutonAfficher.addEventListener("click", () => jouerAffichage(item));
  if (audio && !affichage.audio && !CAPACITES.syntheseDisponible()) {
    boutonAfficher.disabled = true;
    refs.enonce.textContent = "La synthèse vocale est indisponible sur ce navigateur. Choisis le parcours Mots lus depuis l’accueil.";
  }
  refs.zoneMemo.replaceChildren(
    creerElement("div", { classe: "memo-actions" },
      boutonAfficher,
      creerElement("span", { classe: "memo-mention", texte: mention })
    )
  );
  refs.zoneMemo.hidden = false;
  reglerEtatBoutons();
}

/** Lecture temporisée du stimulus (séquence élément par élément, ou liste). */
function jouerAffichage(item) {
  CAPACITES.arreter();
  refs.ligneAudio.hidden = true;
  const affichage = item.contenu.affichage;
  const plateau = creerElement("div", { classe: "memo-plateau" });
  const indicateur = creerElement("p", { classe: "memo-points" });
  const boutonPasser = creerElement("button", {
    classe: "bouton bouton-secondaire",
    texte: "Passer",
    attributs: { type: "button" },
  });
  boutonPasser.addEventListener("click", () => afficherQuestion(item));
  refs.zoneMemo.replaceChildren(plateau, indicateur, boutonPasser);

  if (affichage.modalite === "auditive") {
    jouerSeriesAudio(item, plateau, indicateur);
    return;
  }
  if (affichage.mode === "texte") {
    // Texte à lire (méthode PQRST) : affiché pendant la durée prévue, puis masqué.
    plateau.replaceChildren(
      creerElement("div", { classe: "memo-texte" },
        ...affichage.elements.map((paragraphe) => creerElement("p", { texte: paragraphe }))
      )
    );
    // Le stimulus devient « ce qui est affiché » : le bouton Écouter le relit à la
    // demande, et la lecture automatique le dit d'elle-même si elle est active.
    etat.enonceCourant = affichage.elements.join(". ");
    lireSiLectureAuto(etat.enonceCourant);
    etat.minuteriesMemo.push(
      setTimeout(() => jouerDelaiOuQuestion(item), affichage.duree_totale_ms)
    );
    return;
  }

  if (affichage.mode === "liste") {
    const liste = creerElement("ul", { classe: "memo-liste" });
    for (const [gauche, droite] of affichage.elements) {
      liste.append(
        creerElement("li", { classe: "memo-paire" },
          creerElement("span", { texte: gauche }),
          creerElement("span", { texte: droite })
        )
      );
    }
    plateau.append(liste);
    // Le stimulus (paires, fiche) devient « ce qui est affiché ».
    etat.enonceCourant = affichage.elements
      .map(([gauche, droite]) => (droite ? `${gauche} : ${droite}` : gauche))
      .join(". ");
    lireSiLectureAuto(etat.enonceCourant);
    etat.minuteriesMemo.push(
      setTimeout(() => jouerDelaiOuQuestion(item), affichage.duree_totale_ms)
    );
    return;
  }

  // Séquence de chiffres/mots/lettres ou séries de mots : un élément à la fois,
  // suivi d'un blanc de deux secondes avant le suivant.
  const groupes = affichage.mode === "series" ? affichage.series : [affichage.elements];
  const blancMemoMs = affichage.pause_item_ms ?? BLANC_INTER_ITEM_MS;
  let delai = 0;
  groupes.forEach((groupe, indexGroupe) => {
    groupe.forEach((element, index) => {
      etat.minuteriesMemo.push(setTimeout(() => {
        if (affichage.mode === "series" && index === 0) {
          plateau.append(creerElement("p", {
            classe: "memo-serie-titre",
            texte: `Série ${indexGroupe + 1} / ${groupes.length}`,
          }));
        }
        plateau.append(creerElement("span", { classe: "memo-element", texte: element }));
        indicateur.textContent = affichage.mode === "series"
          ? `Série ${indexGroupe + 1} / ${groupes.length}`
          : `${index + 1} / ${groupe.length}`;
      }, delai));
      delai += affichage.duree_par_item_ms;
      if (index < groupe.length - 1) {
        etat.minuteriesMemo.push(setTimeout(() => {
          for (const noeud of plateau.querySelectorAll(".memo-element")) noeud.remove();
        }, delai));
        delai += blancMemoMs;
      }
    });
    if (indexGroupe < groupes.length - 1) {
      etat.minuteriesMemo.push(setTimeout(() => { plateau.replaceChildren(); }, delai));
      delai += Number(affichage.pause_serie_ms || 1500);
    }
  });
  if (affichage.pause_item_ms) {
    etat.minuteriesMemo.push(setTimeout(() => plateau.replaceChildren(), delai));
    delai += affichage.pause_item_ms;
  }
  etat.minuteriesMemo.push(setTimeout(() => jouerDelaiOuQuestion(item), delai));
}

/** Réponses produites ou choix par point, sans réponse attendue côté client. */
function rendreFonctionnel(item) {
  if (item.type === "reprise-interrompue") {
    rendreRepriseInterrompue(item);
    return;
  }
  const c = item.contenu;
  const zone = refs.zoneSequence;
  zone.hidden = false;
  zone.replaceChildren();
  const reponses = {};
  const bouton = (texte, action) => {
    const b = creerElement("button", { texte, classe: "bouton bouton-secondaire",
      attributs: { type: "button" } });
    b.addEventListener("click", action); return b;
  };
  function soumettre() { soumettreValeur({ ...reponses }, 0); }
  function formulaire() {
    const valider = bouton("Valider", soumettre);
    valider.disabled = true;
    const verifier = () => { valider.disabled = !c.champs.every(champ => String(reponses[champ.id] || "").trim()); };
    for (const champ of c.champs) {
      const ligne = creerElement("label", { classe: "champ-fonctionnel" },
        creerElement("span", { texte: champ.label }));
      if (item.type === "actualiser-consigne") {
        const saisie = creerElement("input", { attributs: { type: "text", autocomplete: "off" } });
        saisie.addEventListener("input", () => { reponses[champ.id] = saisie.value; verifier(); });
        ligne.append(saisie);
      } else {
        const choix = creerElement("select", { attributs: { "aria-label": champ.label } });
        for (const [value, texte] of [["", "À vérifier"], ["conforme", "Conforme"], ["ecart", "Écart à corriger"]]) {
          choix.append(creerElement("option", { texte, attributs: { value } }));
        }
        choix.addEventListener("change", () => { reponses[champ.id] = choix.value; verifier(); });
        ligne.append(choix);
      }
      zone.append(ligne);
    }
    zone.append(valider);
  }
  if (item.type === "actualiser-consigne") {
    let index = 0;
    function montrer() {
      zone.replaceChildren();
      const etape = c.etapes[index];
      if (!etape) {
        zone.append(creerElement("p", { texte: "Écris la consigne finale. Les éléments non modifiés restent valables." }));
        formulaire(); return;
      }
      zone.append(creerElement("p", { classe: "ligne-discrete", texte: `${etape.titre} — ${index + 1}/${c.etapes.length}` }),
        creerElement("p", { classe: "document-source", texte: etape.texte }),
        bouton(index === c.etapes.length - 1 ? "Restituer la consigne" : "Message suivant", () => { index++; montrer(); }));
    }
    montrer(); return;
  }
  if (item.type === "comparer-documents") {
    const documents = creerElement("div", { classe: "documents-comparaison" });
    for (const doc of c.documents) {
      const bloc = creerElement("section", { classe: "document-source" }, creerElement("h3", { texte: doc.titre }));
      for (const ligne of doc.lignes) bloc.append(creerElement("p", { texte: `${ligne.label} : ${ligne.texte}` }));
      documents.append(bloc);
    }
    zone.append(documents); formulaire(); return;
  }
  let index = 0;
  const objectif = creerElement("section", { classe: "document-source" },
    creerElement("p", { texte: c.objectif }), creerElement("p", { texte: `À retenir : ${c.critere}` }));
  const message = creerElement("div");
  zone.append(objectif, message);
  function prochain() {
    message.replaceChildren();
    const courant = c.messages[index];
    if (!courant) { message.append(bouton("Vérifier mes choix", soumettre)); return; }
    message.append(creerElement("p", { classe: "ligne-discrete", texte: `Message ${index + 1}/${c.messages.length}` }),
      creerElement("p", { classe: "document-source", texte: courant.texte }));
    let reponseDonnee = false;
    for (const [valeur, libelle] of [["oui", "À prendre en compte"], ["non", "Sans conséquence selon les critères"]]) {
      message.append(bouton(libelle, () => {
        if (reponseDonnee) return;
        reponseDonnee = true;
        reponses[courant.id] = valeur;
        index++;
        prochain();
      }));
    }
  }
  prochain();
}

/** Tâche commencée, bref détour réellement affiché, puis récupération du point de reprise. */
function rendreRepriseInterrompue(item) {
  const c = item.contenu;
  const zone = refs.zoneSequence;
  const reponses = { points: {}, reprise: "", interruption: "" };
  let index = 0;
  let interruptionFaite = false;
  zone.hidden = false;

  const bouton = (texte, action, classe = "bouton bouton-secondaire") => {
    const element = creerElement("button", { texte, classe, attributs: { type: "button" } });
    element.addEventListener("click", action);
    return element;
  };
  const cadreBut = () => creerElement("section", { classe: "document-source" },
    creerElement("h3", { texte: c.enonce }), creerElement("p", { texte: c.but }));

  function montrerPoint() {
    if (!interruptionFaite && index === c.interruption_apres) {
      montrerInterruption();
      return;
    }
    if (index >= c.points.length) {
      zone.replaceChildren(cadreBut(),
        creerElement("p", { texte: "Le contrôle est terminé." }),
        bouton("Valider le contrôle", () => soumettreValeur({ ...reponses,
          points: { ...reponses.points } }, 0), "bouton bouton-primaire"));
      return;
    }
    const point = c.points[index];
    let choixFait = false;
    const actions = point.options.map((libelle, position) => bouton(libelle, () => {
      if (choixFait) return;
      choixFait = true;
      reponses.points[point.id] = position === 0 ? "valide" : "reprendre";
      index += 1;
      montrerPoint();
    }));
    zone.replaceChildren(cadreBut(),
      creerElement("p", { classe: "ligne-discrete", texte: `Point ${index + 1}/${c.points.length} — ${point.label}` }),
      creerElement("p", { classe: "document-source", texte: point.etat }),
      creerElement("div", { classe: "grille-options" }, ...actions));
  }

  function montrerInterruption() {
    interruptionFaite = true;
    const interruption = c.interruption;
    let choixFait = false;
    const actions = interruption.options.map(option => bouton(option, () => {
      if (choixFait) return;
      choixFait = true;
      reponses.interruption = option;
      montrerReprise();
    }));
    zone.replaceChildren(
      creerElement("p", { classe: "ligne-discrete", texte: "Interruption" }),
      creerElement("p", { texte: "Réponds à ce bref message avant de revenir au contrôle." }),
      creerElement("p", { classe: "document-source", texte: interruption.enonce }),
      creerElement("div", { classe: "grille-options" }, ...actions));
  }

  function montrerReprise() {
    let choixFait = false;
    const actions = c.points.map(point => bouton(point.label, () => {
      if (choixFait) return;
      choixFait = true;
      reponses.reprise = point.id;
      montrerPoint();
    }));
    zone.replaceChildren(
      creerElement("p", { classe: "ligne-discrete", texte: "Retrouve le fil" }),
      creerElement("p", { texte: "Le dossier est momentanément masqué. Quel point dois-tu traiter maintenant ?" }),
      creerElement("div", { classe: "grille-options" }, ...actions));
  }

  montrerPoint();
}

/** Les mots auditifs ne sont jamais écrits dans le DOM. La voix pilote l'avancement. */
function jouerSeriesAudio(item, plateau, indicateur) {
  const generation = etat.memoGeneration;
  const a = item.contenu.affichage;
  const mots = a.series.flatMap((serie, groupe) => serie.map((mot, index) => ({
    mot, groupe, dernier: index === serie.length - 1,
  })));
  const actif = () => generation === etat.memoGeneration;
  function jouer(index) {
    if (!actif()) return;
    if (index === mots.length) { jouerDelaiOuQuestion(item); return; }
    const { mot, groupe, dernier } = mots[index];
    plateau.textContent = "Écoute…";
    indicateur.textContent = `Série ${groupe + 1} / ${a.series.length}`;
    let termine = false;
    function erreur() {
      if (!actif() || termine) return;
      termine = true;
      CAPACITES.arreter();
      plateau.textContent = "Lecture interrompue. Tu peux réécouter la série depuis le début.";
      const reprendre = creerElement("button", { texte: "Réécouter depuis le début",
        classe: "bouton bouton-secondaire", attributs: { type: "button" } });
      reprendre.addEventListener("click", () => { annulerMemo(); afficherPhaseMemo(item); });
      plateau.append(reprendre);
    }
    const lireMot = a.audio?.[mot] ? CAPACITES.lireFichier : CAPACITES.lire;
    const disponible = lireMot(a.audio?.[mot] || mot, {
      onFin() {
        if (!actif() || termine) return;
        termine = true;
        plateau.textContent = "…";
        const pause = dernier && index < mots.length - 1 ? a.pause_serie_ms : a.pause_item_ms;
        etat.minuteriesMemo.push(setTimeout(() => jouer(index + 1), pause));
      },
      onErreur: erreur,
    });
    if (!disponible) erreur();
    // Un moteur muet ne doit pas laisser la séance bloquée indéfiniment.
    etat.minuteriesMemo.push(setTimeout(erreur, 15000));
  }
  jouer(0);
}

/** Après le stimulus : attente volontaire (rappel différé) puis question. */
function jouerDelaiOuQuestion(item) {
  const delai = Number((item.contenu && item.contenu.delai_s) || 0);
  if (!delai) {
    afficherQuestion(item);
    return;
  }
  // Rappel différé : l'attente est affichée, pas cachée — et l'utilisateur
  // peut toujours passer (aucune contrainte de temps imposée).
  const restant = creerElement("p", { classe: "memo-attente" });
  const boutonPasser = creerElement("button", {
    classe: "bouton bouton-secondaire",
    texte: "Passer l'attente",
    attributs: { type: "button" },
  });
  boutonPasser.addEventListener("click", () => afficherQuestion(item));
  let secondes = Math.round(delai);
  const majTexte = () => { restant.textContent = `Encore ${secondes} s avant la question…`; };
  majTexte();
  refs.zoneMemo.replaceChildren(restant, boutonPasser);
  refs.zoneMemo.hidden = false;
  const intervalle = setInterval(() => {
    secondes -= 1;
    majTexte();
    if (secondes <= 0) afficherQuestion(item);
  }, 1000);
  etat.minuteriesMemo.push(intervalle);
}

/** Phase question : le stimulus a disparu — énoncé, saisie, focus. */
/** Séquence guidée « PQRST mis en œuvre » (ADR-015) : les cinq étapes en une page.
 *  La personne applique la méthode d'un bout à l'autre, puis reçoit la correction étape
 *  par étape (la question écrite n'est pas notée : son modèle est montré). */
function rendreSequence(item) {
  const contenu = item.contenu || {};
  const etapes = new Map((contenu.etapes || []).map((etape) => [etape.etape, etape]));
  etat.sequence = {};
  refs.formulaire.hidden = true;
  refs.zoneChoix.hidden = true;
  refs.zoneIndices.hidden = true;
  refs.zoneGeneration.hidden = true;

  const zone = refs.zoneSequence;
  zone.replaceChildren();
  zone.hidden = false;
  zone.append(creerElement("p", { classe: "sequence-titre", texte: contenu.titre_texte || "" }));

  const boutonValider = creerElement("button", {
    classe: "bouton-principal", texte: "Valider la séquence",
    attributs: { type: "button" },
  });
  boutonValider.addEventListener("click", () => soumettreValeur(etat.sequence, 0));

  const majBouton = () => {
    const test = etat.sequence["5"] || [];
    boutonValider.disabled = etat.actionEnCours
      || !etat.sequence["1"] || !etat.sequence["4"]
      || test.filter(Boolean).length !== 2;
  };

  // Étape 1 — Parcours : le sujet du texte, avant de lire.
  const parcours = etapes.get(1) || {};
  zone.append(creerElement("h3", {
    classe: "sequence-etape", texte: `1. Parcours — ${parcours.enonce || ""}`,
  }));
  const choixParcours = creerElement("div", { classe: "sequence-choix" });
  for (const option of parcours.options || []) {
    const bouton = creerElement("button", {
      classe: "sequence-option", texte: option, attributs: { type: "button" },
    });
    bouton.addEventListener("click", () => {
      etat.sequence["1"] = option;
      for (const autre of choixParcours.children) autre.classList.remove("sequence-option-active");
      bouton.classList.add("sequence-option-active");
      majBouton();
    });
    choixParcours.append(bouton);
  }
  zone.append(choixParcours);

  // Étape 2 — Question : production libre, non notée.
  zone.append(creerElement("h3", {
    classe: "sequence-etape",
    texte: "2. Question — écris la question que tu te poses sur ce texte",
  }));
  const champQuestion = creerElement("input", {
    classe: "sequence-champ",
    attributs: { type: "text", placeholder: "Ta question…", "aria-label": "Ta question" },
  });
  champQuestion.addEventListener("input", () => {
    etat.sequence["2"] = champQuestion.value;
    majBouton();
  });
  zone.append(champQuestion);

  // Étape 3 — Lecture : le texte entier, au rythme de la personne (aucun chronomètre).
  zone.append(creerElement("h3", {
    classe: "sequence-etape", texte: "3. Lecture — lis le texte à ton rythme",
  }));
  zone.append(creerElement("p", { classe: "sequence-texte", texte: contenu.texte || "" }));

  // Étape 4 — Reformulation : production libre, jugée sur 4 idées-clés sur 5.
  const reformulation = etapes.get(4) || {};
  zone.append(creerElement("h3", {
    classe: "sequence-etape", texte: `4. Reformulation — ${reformulation.enonce || ""}`,
  }));
  const champReformulation = creerElement("input", {
    classe: "sequence-champ",
    attributs: { type: "text", placeholder: "En une phrase, avec tes mots…",
                 "aria-label": "Ta reformulation" },
  });
  champReformulation.addEventListener("input", () => {
    etat.sequence["4"] = champReformulation.value;
    majBouton();
  });
  zone.append(champReformulation);

  // Étape 5 — Test : deux questions de mémoire.
  zone.append(creerElement("h3", {
    classe: "sequence-etape", texte: "5. Test — réponds de mémoire",
  }));
  const reponsesTest = [];
  (etapes.get(5)?.questions || []).forEach((question, rang) => {
    zone.append(creerElement("p", { classe: "sequence-question", texte: question.enonce }));
    const choix = creerElement("div", { classe: "sequence-choix" });
    for (const option of question.options || []) {
      const bouton = creerElement("button", {
        classe: "sequence-option", texte: option, attributs: { type: "button" },
      });
      bouton.addEventListener("click", () => {
        reponsesTest[rang] = option;
        etat.sequence["5"] = [...reponsesTest];
        for (const autre of choix.children) autre.classList.remove("sequence-option-active");
        bouton.classList.add("sequence-option-active");
        majBouton();
      });
      choix.append(bouton);
    }
    zone.append(choix);
  });

  zone.append(creerElement("div", { classe: "sequence-actions" }, boutonValider));
  majBouton();
}

/** Fiche méthode récapitulative, montrée au résumé de séance (à garder hors écran). */
function rendreFicheMethode() {
  const precedent = refs.statsResume.parentElement.querySelector(".fiche-methode");
  if (precedent) precedent.remove();
  const sequence = (etat.session?.items || []).find(
    (item) => item.type === "pqrst-mise-en-oeuvre"
  );
  const lignes = sequence?.contenu?.fiche_methode;
  if (!Array.isArray(lignes) || !lignes.length) return;
  const bloc = creerElement("section", { classe: "fiche-methode" },
    creerElement("h3", { texte: "Méthode PQRST — à garder" }),
    creerElement("ol", {}, ...lignes.map((ligne) => creerElement("li", { texte: ligne })))
  );
  refs.statsResume.parentElement.append(bloc);
}

/** Corrige une séquence : une ligne par étape (la question écrite n'est pas notée). */
function rendreFeedbackSequence(resultat) {
  const detail = resultat.sequence || {};
  const lignes = [
    { titre: "1. Parcours", correcte: detail["1"]?.correcte,
      texte: detail["1"]?.correcte ? "sujet du texte trouvé" : `attendu : ${detail["1"]?.attendue ?? "—"}` },
    { titre: "2. Ta question", correcte: true, nonNotee: true,
      texte: `non notée — une question possible : « ${detail["2"]?.modele ?? ""} »` },
    { titre: "4. Reformulation", correcte: detail["4"]?.correcte,
      texte: `${detail["4"]?.trouvees?.length ?? 0}/${(detail["4"]?.trouvees?.length ?? 0) + (detail["4"]?.manquantes?.length ?? 0) + (detail["4"]?.contredites?.length ?? 0)} idées retrouvées`
        + (detail["4"]?.contredites?.length ? ` — à corriger : ${detail["4"].contredites.join(", ")}` : "")
        + (detail["4"]?.manquantes?.length ? ` — manquaient : ${detail["4"].manquantes.join(", ")}` : "")
        + ` · modèle : « ${detail["4"]?.modele ?? ""} »` },
    { titre: "5. Test", correcte: detail["5"]?.correcte,
      texte: (detail["5"]?.questions || []).map((bonne, rang) =>
        `${rang + 1}. ${detail["5"]?.reussies?.[rang] ? "✓" : "✗"} ${bonne}`).join(" · ") },
  ];
  refs.carteFeedback.replaceChildren();
  refs.carteFeedback.className = "carte-feedback " + (resultat.correcte ? "feedback-correct" : "feedback-incorrect");
  refs.carteFeedback.append(creerElement("p", {
    classe: "feedback-titre",
    texte: resultat.correcte ? "✓ Séquence réussie" : "✓ Séquence terminée — à revoir",
  }));
  for (const ligne of lignes) {
    refs.carteFeedback.append(creerElement("p", {
      classe: "feedback-sequence-ligne",
      texte: `${ligne.titre} : ${ligne.texte}`,
    }));
  }
}

function afficherQuestion(item) {
  annulerMemo();
  const contenu = item.contenu || {};
  viderZonesReponse();
  // Capacités du poste : réinitialisées pour chaque question (la dictée ne
  // s'affiche que pour une réponse à saisir ; l'écoute suit la disponibilité).
  CAPACITES.arreter();
  refs.boutonDicter.hidden = true;
  refs.boutonDicter.textContent = "🎤 Répondre à voix haute";
  refs.ligneAudio.hidden = !CAPACITES.syntheseDisponible();

  // Énoncé : grand texte ; variante monospace pour la prédiction de sortie.
  refs.enonce.textContent = contenu.enonce ?? "";
  refs.enonce.className =
    "enonce" + (item.type === "prediction-sortie" ? " enonce-code" : "");
  // « Écouter » relit volontairement l'énoncé complet. En lecture automatique,
  // une consigne de déduction identique n'est dite qu'une fois dans la séance ;
  // les indices propres à chaque nouvelle grille restent toujours lus.
  if (item.type === "grille-deduction") {
    etat.enonceCourant = textePourLectureDeduction(contenu, true);
    lireSiLectureAuto(texteAutomatiquePourDeduction(contenu));
  } else {
    etat.enonceCourant = contenu.enonce ?? "";
    lireSiLectureAuto(etat.enonceCourant);
  }

  // Rappel de méthode : affiché une seule fois par type d'exercice dans la séance.
  // (Les items à stimulus le montrent déjà pendant la phase de mémorisation.)
  if (contenu.consigne && !contenu.affichage && !etat.consignesVues.has(item.type)) {
    etat.consignesVues.add(item.type);
    refs.rappelConsigne.textContent = contenu.consigne;
    refs.rappelConsigne.hidden = false;
  } else {
    refs.rappelConsigne.hidden = true;
  }

  // Aide optionnelle (contenu.aide) : repliée par défaut.
  const aideGenerique = aideGeneriquePourItem(item);
  if (aideGenerique) {
    refs.texteAide.textContent = aideGenerique;
    refs.zoneAide.hidden = false;
  } else {
    refs.texteAide.textContent = "";
    refs.zoneAide.hidden = true;
  }

  // Analyse du mot (SFA/PCA) : l'utilisateur génère ses attributs, puis nomme.
  if (item.type === "analyse-mot") {
    rendreGeneration(item);
  }

  // Séquence guidée « PQRST mis en œuvre » : les cinq étapes se répondent d'un bloc.
  if (item.type === "pqrst-mise-en-oeuvre") {
    rendreSequence(item);
  }

  if (["actualiser-consigne", "comparer-documents", "reperer-essentiel", "reprise-interrompue"].includes(item.type)) {
    refs.formulaire.hidden = true;
    refs.carteFeedback.hidden = true;
    refs.boutonSuivant.hidden = true;
    CAPACITES.arreter();
    refs.ligneAudio.hidden = true;
    rendreFonctionnel(item);
    etat.debutQuestion = Date.now();
    reglerEtatBoutons();
    return;
  }

  // Grille de déduction : placement de jetons, pas de saisie de texte.
  if (item.type === "grille-deduction") {
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
    return;
  }

  // Champ de saisie : remise à zéro OBLIGATOIRE à chaque nouvelle question
  // (la réponse précédente ne doit jamais rester affichée), clavier adapté.
  refs.champReponse.value = "";
  refs.champReponse.disabled = false;
  refs.champReponse.setAttribute("inputmode", inputmodePour(item.type));
  refs.indiceReponse.hidden = true;

  // Choix de réponse ou saisie libre selon le type d'exercice.
  const options = Array.isArray(contenu.options) ? contenu.options : null;
  const avecChoix = Boolean(options) && TYPES_A_CHOIX.has(item.type);
  refs.zoneChoix.replaceChildren();
  refs.zoneChoix.hidden = !avecChoix;
  refs.zoneIndices.replaceChildren();
  refs.zoneIndices.hidden = true;
  if (avecChoix) rendreOptions(options, item);
  refs.formulaire.hidden = avecChoix;
  // Réponse à dicter possible seulement quand on attend un texte libre — et jamais
  // pour du code (une dictée ne restitue ni indentation ni symboles).
  const dicteePossible = CAPACITES.voixDisponible() && !avecChoix
    && !THEMES_SANS_DICTEE.has(etat.theme.id);
  refs.boutonDicter.hidden = !dicteePossible;

  // Indices progressifs (accès au mot) : proposés, jamais imposés.
  if (Array.isArray(contenu.indices) && contenu.indices.length) rendreIndices(item);

  // On masque le feedback précédent et on redonne la main.
  refs.carteFeedback.hidden = true;
  refs.boutonSuivant.hidden = true;
  reglerEtatBoutons();

  etat.debutQuestion = Date.now();
  if (avecChoix) {
    const premier = refs.zoneChoix.querySelector("button");
    if (premier) premier.focus();
  } else {
    refs.champReponse.focus();
  }
}

/** Propositions cliquables : un clic vaut réponse soumise (pas de saisie). */
function rendreOptions(options, item) {
  const bac = creerElement("div", { classe: "grille-options" });
  // Recherche d'information : le document reste consultable pendant la réponse.
  // Il appartient à zoneChoix, vidée à chaque question (y compris avant une phase mémo).
  const documentSource = item?.contenu?.document;
  if (typeof documentSource === "string" && documentSource.trim()) {
    bac.append(creerElement("section", { classe: "document-source", attributs: { "aria-label": "Document à consulter" } },
      creerElement("h3", { texte: "Document à consulter" }),
      creerElement("p", { texte: documentSource })
    ));
  }

  // Certains items à choix (plan à vérifier) présentent d'abord un plan ordonné.
  const plan = item && item.contenu ? item.contenu.plan : null;
  if (Array.isArray(plan) && plan.length) {
    bac.append(creerElement("ol", { classe: "plan-propose" },
      ...plan.map((etape) => creerElement("li", { texte: etape }))
    ));
  }
  for (const option of options) {
    const bouton = creerElement("button", {
      classe: "bouton bouton-option",
      texte: option,
      attributs: { type: "button" },
    });
    bouton.addEventListener("click", () => {
      if (etat.repondu || etat.actionEnCours) return;
      etat.optionChoisie = option;
      soumettreValeur(option, null);
    });
    bac.append(bouton);
  }
  refs.zoneChoix.replaceChildren(bac);
}

/** Indices progressifs : révélés un par un ; le dernier cran affiche la réponse. */
function rendreIndices(item) {
  const indices = item.contenu.indices;
  const statut = creerElement("p", { classe: "indice-statut" });
  const liste = creerElement("ol", { classe: "liste-indices" });
  const bouton = creerElement("button", {
    classe: "bouton bouton-secondaire",
    texte: "Un indice",
    attributs: { type: "button" },
  });
  const majBouton = () => {
    const restants = indices.length - etat.indicesReveles;
    bouton.textContent = restants > 0 ? "Un indice" : "Voir la réponse";
    statut.textContent =
      etat.indicesReveles === 0
        ? "Aucun indice utilisé pour l’instant."
        : `${etat.indicesReveles} indice${etat.indicesReveles > 1 ? "s" : ""} utilisé${etat.indicesReveles > 1 ? "s" : ""}.`;
  };
  bouton.addEventListener("click", () => {
    if (etat.repondu || etat.actionEnCours) return;
    if (etat.indicesReveles < indices.length) {
      liste.append(
        creerElement("li", { classe: "indice-item", texte: indices[etat.indicesReveles].texte })
      );
      etat.indicesReveles += 1;
      majBouton();
      return;
    }
    // Tous les indices ont été consultés : la réponse s'affiche et l'essai est
    // clos SANS ERREUR (le moteur le compte comme non retrouvé).
    soumettreValeur("", indices.length + 1);
  });
  majBouton();
  refs.zoneIndices.replaceChildren(statut, liste, bouton);
  refs.zoneIndices.hidden = false;
}

/** Validation (Entrée ou bouton) → POST /reponses → feedback immédiat. */
async function validerReponse() {
  if (etat.actionEnCours || etat.repondu || !etat.session) return;

  const brut = refs.champReponse.value.trim();
  if (!brut) {
    // Saisie vide : simple indice, aucune pression.
    refs.indiceReponse.hidden = false;
    refs.champReponse.focus();
    return;
  }
  await soumettreValeur(brut, etat.indicesReveles);
}

/**
 * Soumet une réponse (saisie libre ou proposition choisie) et affiche le retour.
 * ``indiceUtilise`` : nombre d'indices consultés ; ``nbIndices + 1`` signale un
 * essai clos par affichage de la réponse (aucune erreur commise par l'utilisateur).
 */
async function soumettreValeur(brut, indiceUtilise) {
  if (etat.actionEnCours || etat.repondu || !etat.session) return;

  const item = etat.session.items[etat.indexItem];
  // Séquence guidée : le payload est déjà l'objet des réponses par étape.
  const sequence = ["pqrst-mise-en-oeuvre", "actualiser-consigne", "comparer-documents", "reperer-essentiel", "reprise-interrompue"].includes(item.type);
  const corps = {
    item_id: item.id,
    reponse: sequence ? brut : normaliserReponse(brut, etat.theme),
    temps_ms: Math.max(0, Date.now() - etat.debutQuestion),
  };
  if (Number.isInteger(indiceUtilise) && indiceUtilise > 0) {
    corps.indice_utilise = indiceUtilise;
  }
  etat.reponseSoumise = sequence ? "" : String(brut);

  etat.actionEnCours = true;
  reglerEtatBoutons();

  try {
    const resultat = await apiFetch(
      `/${encodeURIComponent(etat.theme.id)}/sessions/${encodeURIComponent(etat.session.session_id)}/reponses`,
      { method: "POST", body: JSON.stringify(corps) }
    );
    masquerBandeau();
    // Second essai (exercices de stratégie) : on ne révèle rien, l'exercice reste actif.
    if (resultat.essai_supplementaire === true) {
      rendreFeedback(resultat);
      etat.actionEnCours = false;
      reglerEtatBoutons();
      return;
    }
    etat.repondu = true;

    // Feedback : statut + réponse attendue (après coup) + commentaire serveur.
    rendreFeedback(resultat);
    etat.reponsesAttendues[item.id] = resultat.attendue;
    if (resultat.reprise === true && etat.session) {
      // Reprise errorless : l'exercice revient une fois, en fin de séance.
      etat.session.items.push(item);
      etat.reprisesAfficher.add(item.id);
      refs.carteFeedback.append(creerElement("p", {
        classe: "feedback-note-reprise",
        texte: "Cet exercice reviendra une fois en fin de séance, avec la réponse.",
      }));
    }

    for (const controle of refs.zoneSequence.querySelectorAll("input, select, button")) controle.disabled = true;

    // On masque la saisie pour laisser toute la place au retour.
    refs.formulaire.hidden = true;

    const dernier = etat.indexItem === etat.session.items.length - 1;
    if (resultat.seance_terminee === true) {
      // Durée maximale atteinte : la réponse est conservée et la séance s'arrête ici.
      etat.seanceTerminee = true;
      refs.carteFeedback.append(creerElement("p", {
        classe: "feedback-note-duree",
        texte: "Séance terminée : la durée maximale est atteinte. Ta réponse est enregistrée.",
      }));
    } else if (resultat.arret_propose === true && resultat.motif_arret === "duree") {
      // Durée **proposée** (déduction) : on invite à s'arrêter, la personne décide.
      refs.carteFeedback.append(creerElement("p", {
        classe: "feedback-note-duree",
        texte: "La séance dure depuis dix minutes. Tu peux t'arrêter là (bouton « Terminer la séance ») ou continuer — c'est toi qui vois.",
      }));
    }
    refs.boutonSuivant.textContent = dernier || etat.seanceTerminee ? "Voir le résumé" : "Suivant";
    refs.boutonSuivant.hidden = false;
    // Rendre la main AVANT de déplacer le focus : un bouton désactivé
    // ne peut pas le recevoir.
    etat.actionEnCours = false;
    reglerEtatBoutons();
    refs.boutonSuivant.focus();
  } catch (erreur) {
    if (erreur.type === "reseau") {
      // La saisie est conservée : on peut réessayer sans rien retaper.
      afficherErreurReseau(() => soumettreValeur(brut, indiceUtilise));
    } else if (erreur.type === "api" && (erreur.status === 404 || erreur.status === 409)) {
      refs.champReponse.disabled = true;
      afficherBandeau("Cette séance n’est plus disponible.", { retour: true });
    } else {
      afficherBandeau("La réponse n’a pas pu être vérifiée pour le moment.", {
        reessayer: () => soumettreValeur(brut, indiceUtilise),
      });
    }
  } finally {
    etat.actionEnCours = false;
    reglerEtatBoutons();
  }
}

/** Rend le feedback dans la carte aria-live="polite". */
function rendreFeedback(resultat) {
  if (etat.theme && etat.theme.id === "deduction") {
    rendreFeedbackGrille(resultat);
    return;
  }
  // Séquence guidée : correction étape par étape (parcours, question modèle, idées-clés, test).
  if (resultat.detail_fonctionnel) {
    const detail = resultat.detail_fonctionnel;
    refs.carteFeedback.hidden = false;
    refs.carteFeedback.replaceChildren(creerElement("p", {
      classe: "feedback-titre", texte: resultat.correcte ? "Tous les points sont retrouvés." : "Reprenons les points un à un."
    }));
    refs.carteFeedback.className = "carte-feedback";
    for (const ligne of detail.lignes) refs.carteFeedback.append(creerElement("p", {
      texte: `${ligne.correcte ? "✓" : "↻"} ${ligne.label} : ${ligne.attendue}. ${ligne.explication}`
    }));
    if (detail.type === "reperer-essentiel") refs.carteFeedback.append(creerElement("p", {
      texte: `Informations utiles omises : ${detail.omissions} · Sélections inutiles : ${detail.fausses_selections}`
    }));
    return;
  }
  if (resultat.sequence) {
    rendreFeedbackSequence(resultat);
    return;
  }
  // Second essai : on encourage à reprendre, sans donner la réponse (c'est l'essai qui
  // fait apprendre — pratique de récupération, ADR-014).
  if (resultat.essai_supplementaire === true) {
    refs.carteFeedback.replaceChildren();
    refs.carteFeedback.className = "carte-feedback feedback-essaie";
    refs.carteFeedback.append(creerElement("p", {
      classe: "feedback-titre",
      texte: "↻ On reprend",
    }));
    refs.carteFeedback.append(creerElement("p", {
      classe: "feedback-detail",
      texte: resultat.feedback || "Reprends : tu peux demander un indice.",
    }));
    return;
  }
  const correcte = Boolean(resultat.correcte);
  const assistee = Boolean(resultat.assistee);
  // Rappel libre : la réponse attendue est une LISTE de mots — on montre ce qui
  // a été retrouvé et ce qui manquait, plutôt qu'un « tout juste / tout faux ».
  const rappelLibre = Boolean(resultat.detail_rappel) || Array.isArray(resultat.attendue);
  refs.carteFeedback.replaceChildren();
  refs.carteFeedback.className =
    "carte-feedback " +
    (rappelLibre
      ? "feedback-rappel"
      : assistee
        ? "feedback-assiste"
        : correcte
          ? "feedback-correct"
          : "feedback-incorrect");

  refs.carteFeedback.append(
    creerElement("p", {
      classe: "feedback-titre",
      texte: rappelLibre
        ? "Rappel terminé"
        : assistee
          ? "Réponse affichée"
          : correcte
            ? "✓ Bonne réponse !"
            : "✕ Pas tout à fait",
    })
  );

  if (rappelLibre) {
    const detail = resultat.detail_rappel || {};
    const trouves = detail.retrouves || [];
    const attendue = Array.isArray(resultat.attendue) ? resultat.attendue : [];
    refs.carteFeedback.append(
      creerElement("p", {
        classe: "feedback-attendue",
        texte: `Retrouvés : ${trouves.length} sur ${attendue.length}`,
      })
    );
    const manques = detail.omis || attendue.filter((mot) => !trouves.includes(mot));
    if (manques.length) {
      refs.carteFeedback.append(
        creerElement("p", {
          classe: "feedback-commentaire",
          texte: `Il restait : ${manques.join(", ")}`,
        })
      );
    }
    if (detail.confusions_series?.length) refs.carteFeedback.append(
      creerElement("p", { classe: "feedback-commentaire",
        texte: `Mots d’une autre série : ${detail.confusions_series.join(", ")}` })
    );
    if (detail.intrusions?.length) refs.carteFeedback.append(
      creerElement("p", { classe: "feedback-commentaire",
        texte: `Mots non présentés : ${detail.intrusions.join(", ")}` })
    );
  } else if (resultat.attendue !== undefined && resultat.attendue !== null) {
    const ligne = creerElement("p", { classe: "feedback-attendue" });
    ligne.append(assistee ? "Réponse : " : "Réponse attendue : ");
    ligne.append(creerElement("strong", { texte: String(resultat.attendue) }));
    refs.carteFeedback.append(ligne);
  }

  if (resultat.feedback) {
    refs.carteFeedback.append(
      creerElement("p", { classe: "feedback-commentaire", texte: resultat.feedback })
    );
  }

  refs.carteFeedback.hidden = false;
}

/** « Suivant » / « Voir le résumé » : avance ou clôture la séance. */
function itemSuivant() {
  if (!etat.session || !etat.repondu) return;
  // La séance peut s'être clôturée d'elle-même (durée maximale atteinte) : dans
  // ce cas, on va au résumé même s'il reste des items livrés.
  if (!etat.seanceTerminee && etat.indexItem < etat.session.items.length - 1) {
    etat.indexItem += 1;
    montrerItem();
  } else {
    finirSeance();
  }
}

/* ---------------------------------------------------------------------
   Clôture (POST /{theme}/sessions/{sid}/fin) et écran résumé
   --------------------------------------------------------------------- */

async function finirSeance() {
  if (etat.actionEnCours || !etat.session) return;
  etat.actionEnCours = true;
  reglerEtatBoutons();
  annulerMemo();
  reinitialiserConfirmationFin();

  try {
    const donnees = await apiFetch(
      `/${encodeURIComponent(etat.theme.id)}/sessions/${encodeURIComponent(etat.session.session_id)}/fin`,
      { method: "POST" }
    );
    masquerBandeau();
    rendreResume(donnees);
    afficherVue("resume");
  } catch (erreur) {
    if (erreur.type === "reseau") {
      afficherErreurReseau(finirSeance);
    } else if (erreur.type === "api" && erreur.status === 409) {
      // Déjà terminée côté serveur : rien de grave, on ramène calmement.
      afficherBandeau("Cette séance est déjà terminée.", { retour: true });
    } else {
      afficherBandeau("La séance n’a pas pu être clôturée pour le moment.", {
        reessayer: finirSeance,
      });
    }
  } finally {
    etat.actionEnCours = false;
    reglerEtatBoutons();
  }
}

/** Rend le résumé : chiffres neutres, proposition d'arret bienveillante. */
function rendreResume(donnees) {
  const resume = donnees.resume || {};

  // Aucun jugement, aucune norme : de simples comptes personnels.
  const stats = [
    { label: "Questions", valeur: String(resume.items ?? "—") },
    { label: "Bonnes réponses", valeur: String(resume.correctes ?? "—") },
    { label: "Durée", valeur: formaterDuree(resume.duree_s) },
    { label: "Réussite", valeur: formaterTaux(resume.taux_reussite) },
  ];

  refs.statsResume.replaceChildren();
  for (const stat of stats) {
    refs.statsResume.append(
      creerElement("div", {},
        creerElement("dt", { texte: stat.label }),
        creerElement("dd", { texte: stat.valeur })
      )
    );
  }

  // Fiche méthode récapitulative, si la séance contenait une séquence « PQRST mis en œuvre ».
  rendreFicheMethode();

  // Proposition d'arrêt (arret_propose) : bienveillante, jamais forcée.
  refs.carteArret.hidden = !donnees.arret_propose;

  // Séances restantes : information douce, dans la fenêtre du thème (jour, ou
  // semaine pour l'évaluation — champ additif `fenetre_sessions`). Sous dérogation,
  // le compteur peut être à zéro : on parle de la limite levée, sans « reviens
  // demain » trompeur (ADR-021).
  const restantes = donnees.sessions_restantes_aujourdhui;
  const fenetre = donnees.fenetre_sessions === "semaine" ? "semaine" : "jour";
  let texteRestantes = "";
  if (sansLimiteActivee()) {
    texteRestantes = "Limite de séances levée — tu décides quand t’arrêter.";
  } else if (Number.isFinite(restantes)) {
    if (restantes <= 0) {
      texteRestantes = fenetre === "semaine"
        ? "C’était ta mesure de la semaine — à bientôt."
        : "C’était la dernière séance du jour — à bientôt.";
    } else if (restantes === 1) {
      texteRestantes = fenetre === "semaine"
        ? "Il te reste une mesure cette semaine, si tu en sens l’envie."
        : "Il te reste une séance aujourd’hui, si tu en sens l’envie.";
    } else {
      texteRestantes = `Il te reste ${restantes} séances aujourd’hui, si tu en sens l’envie.`;
    }
  }
  refs.ligneSeancesRestantes.textContent = texteRestantes;
}

/* ---------------------------------------------------------------------
   Missions hors écran et carnet (périmètre social, stockage séparé)
   --------------------------------------------------------------------- */

/** Ouvre l'écran des missions et charge la liste proposée par le serveur. */
async function ouvrirMissions() {
  etat.missionActive = null;
  refs.zoneNoteMission.hidden = true;
  refs.messageNote.hidden = true;
  refs.listeMissions.replaceChildren();
  refs.journalMissions.replaceChildren(
    creerElement("p", { classe: "ligne-discrete", texte: "Chargement…" })
  );
  afficherVue("missions");
  try {
    const donnees = await fetchMissions("");
    etat.missions = donnees.missions || [];
    rendreMissions(etat.missions, donnees.ressentis || []);
    masquerBandeau();
    await chargerJournal();
  } catch {
    refs.journalMissions.replaceChildren();
    afficherBandeau("Les missions n’ont pas pu être chargées pour le moment.", { retour: true });
  }
}

/** Rend les missions : préparation hors écran, aucune réponse attendue. */
function rendreMissions(missions, ressentis) {
  refs.champRessenti.replaceChildren(
    creerElement("option", { texte: "—", attributs: { value: "" } }),
    ...ressentis.map((ressenti) =>
      creerElement("option", { texte: ressenti, attributs: { value: ressenti } })
    )
  );
  refs.listeMissions.replaceChildren();
  if (!missions.length) {
    refs.listeMissions.append(
      creerElement("p", { classe: "ligne-discrete", texte: "Aucune mission proposée pour le moment." })
    );
    return;
  }
  for (const mission of missions) {
    const bouton = creerElement("button", {
      classe: "bouton bouton-secondaire",
      texte: "Mission faite — noter",
      attributs: { type: "button" },
    });
    bouton.addEventListener("click", () => ouvrirNoteMission(mission));
    refs.listeMissions.append(
      creerElement("article", { classe: "carte carte-mission" },
        creerElement("h3", { texte: mission.titre }),
        creerElement("p", { classe: "mission-pourquoi", texte: mission.pourquoi }),
        creerElement("ol", { classe: "mission-etapes" },
          ...mission.etapes.map((etape) => creerElement("li", { texte: etape }))
        ),
        creerElement("p", { classe: "mission-repere", texte: `Repère de réussite : ${mission.repere}` }),
        bouton
      )
    );
  }
}

/** Prépare la zone de note pour la mission choisie. */
function ouvrirNoteMission(mission) {
  etat.missionActive = mission;
  refs.titreNote.textContent = `Noter : ${mission.titre}`;
  refs.champNote.value = "";
  refs.champRessenti.value = "";
  refs.messageNote.hidden = true;
  refs.zoneNoteMission.hidden = false;
  refs.champNote.focus();
}

/** Enregistre une note de mission (aucun jugement, aucune comparaison). */
async function enregistrerNote() {
  if (etat.actionEnCours || !etat.missionActive) return;
  const texte = refs.champNote.value.trim();
  if (!texte) {
    refs.messageNote.hidden = false;
    refs.messageNote.textContent = "Écris quelques mots avant d’enregistrer.";
    return;
  }
  etat.actionEnCours = true;
  refs.boutonEnregistrerNote.disabled = true;
  try {
    await fetchMissions("/journal", {
      method: "POST",
      body: JSON.stringify({
        mission_id: etat.missionActive.id,
        texte,
        ressenti: refs.champRessenti.value || null,
      }),
    });
    masquerBandeau();
    refs.zoneNoteMission.hidden = true;
    refs.messageNote.hidden = false;
    refs.messageNote.textContent = "Note enregistrée — elle reste sur cet appareil.";
    etat.missionActive = null;
    await chargerJournal();
  } catch {
    afficherBandeau("La note n’a pas pu être enregistrée pour le moment.", {
      reessayer: enregistrerNote,
    });
  } finally {
    etat.actionEnCours = false;
    refs.boutonEnregistrerNote.disabled = false;
  }
}

/** Affiche les notes déjà écrites, la plus récente en premier. */
async function chargerJournal() {
  try {
    const donnees = await fetchMissions("/journal");
    const entrees = (donnees.entrees || []).slice().reverse();
    refs.journalMissions.replaceChildren();
    if (!entrees.length) {
      refs.journalMissions.append(
        creerElement("p", { classe: "ligne-discrete", texte: "Aucune note pour l’instant." })
      );
      return;
    }
    for (const entree of entrees) {
      const mission = etat.missions.find((m) => m.id === entree.mission_id);
      const details = [formaterDate(entree.date), entree.ressenti].filter(Boolean).join(" · ");
      refs.journalMissions.append(
        creerElement("article", { classe: "carte carte-note" },
          creerElement("p", { classe: "note-titre", texte: mission ? mission.titre : entree.mission_id }),
          creerElement("p", { classe: "note-texte", texte: entree.texte }),
          creerElement("p", { classe: "note-meta", texte: details })
        )
      );
    }
  } catch {
    refs.journalMissions.replaceChildren(
      creerElement("p", { classe: "ligne-discrete", texte: "Carnet indisponible pour le moment." })
    );
  }
}

/** Date lisible d'une note (français, sans heure). */
function formaterDate(iso) {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
}

/** Appel JSON d'un périmètre annexe (social, programme) — erreurs typées. */
async function fetchJson(base, chemin, options = {}) {
  const entetes = { "Accept": "application/json" };
  if (options.body !== undefined) entetes["Content-Type"] = "application/json";
  let reponse;
  try {
    reponse = await fetch(base + chemin, { ...options, headers: entetes });
  } catch {
    const erreur = new Error("réseau indisponible");
    erreur.type = "reseau";
    throw erreur;
  }
  if (!reponse.ok) {
    const erreur = new Error(`API ${reponse.status}`);
    erreur.type = "api";
    erreur.status = reponse.status;
    throw erreur;
  }
  return reponse.json();
}

/** Appel direct du périmètre missions (base /api/missions, hors sessions). */
function fetchMissions(chemin, options = {}) {
  return fetchJson(API_MISSIONS, chemin, options);
}

/* ---------------------------------------------------------------------
   Programme de 8 semaines : quoi faire aujourd'hui (le programme propose,
   la maîtrise décide — aucune progression forcée)
   --------------------------------------------------------------------- */

/** Libellés lisibles des règles du programme. */
const LIBELLES_REGLES = {
  progression: "Progression",
  fatigue: "Fatigue",
  jours_manques: "Journée manquée",
  alternance: "Alternance",
  duree: "Durée",
  recul: "Recul",
};

async function ouvrirProgramme() {
  refs.planJour.replaceChildren(creerElement("p", { classe: "ligne-discrete", texte: "Chargement…" }));
  refs.semainesProgramme.replaceChildren();
  refs.reglesProgramme.replaceChildren();
  afficherVue("programme");
  try {
    const [donnees, themes] = await Promise.all([
      fetchJson(API_PROGRAMME, ""),
      apiFetch("/themes"),
    ]);
    etat.themesParId = new Map((themes.themes || []).map((theme) => [theme.id, theme]));
    rendrePlanJour(donnees.aujourd_hui || {});
    rendreSemaines(donnees.programme || {});
    rendreRegles(donnees.regles || {});
    masquerBandeau();
  } catch {
    refs.planJour.replaceChildren();
    afficherBandeau("Le programme n’a pas pu être chargé pour le moment.", { retour: true });
  }
}

/** Plan du jour : séance proposée, journée légère, repos ou programme terminé. */
function rendrePlanJour(jour) {
  refs.planJour.replaceChildren();
  if (jour.type === "termine") {
    refs.planJour.append(
      creerElement("h3", { texte: "Programme terminé" }),
      creerElement("p", { texte: "Les huit semaines sont passées. Tu peux reprendre le programme quand tu veux, ou continuer librement." })
    );
    return;
  }
  if (jour.type === "a_venir") {
    refs.planJour.append(creerElement("p", { texte: "Le programme commencera à ta prochaine séance." }));
    return;
  }

  const type = jour.type === "repos"
    ? "Jour de repos"
    : jour.type === "legere" ? "Journée légère" : "Séance du jour";
  refs.planJour.append(
    creerElement("h3", { texte: `Semaine ${jour.semaine} · jour ${jour.jour}` }),
    creerElement("p", { classe: "jour-type", texte: `${type} — ${jour.duree_min} minutes` })
  );
  if (jour.type === "repos") {
    refs.planJour.append(
      creerElement("p", { texte: "Rien à faire aujourd’hui : le repos fait partie du programme." })
    );
    return;
  }

  const themes = jour.themes || [];
  if (themes.includes("au-choix")) {
    refs.planJour.append(
      creerElement("p", { texte: "Choisis ce qui te tente aujourd’hui — les thèmes Extra sont aussi possibles." })
    );
  }
  const plafonds = jour.plafond_palier || {};
  for (const identifiant of themes) {
    const theme = etat.themesParId.get(identifiant);
    if (!theme) continue;
    const plafond = plafonds[identifiant];
    let parcours = theme.parcours?.[0]?.id || null;
    const selecteurParcours = theme.parcours?.length > 1
      ? creerElement("select", { classe: "selecteur-palier",
          attributs: { "aria-label": `Parcours pour ${theme.nom}` } })
      : null;
    if (selecteurParcours) {
      for (const definition of theme.parcours) selecteurParcours.append(creerElement(
        "option", { texte: definition.nom, attributs: { value: definition.id } }
      ));
      selecteurParcours.addEventListener("change", () => { parcours = selecteurParcours.value; });
    }
    const bouton = creerElement("button", {
      classe: "bouton bouton-primaire",
      texte: "Commencer",
      attributs: { type: "button" },
    });
    bouton.addEventListener("click", () => demarrerSession(theme, null, parcours));
    refs.planJour.append(
      creerElement("div", { classe: "jour-theme" },
        creerElement("h4", { texte: theme.nom }),
        creerElement("p", {
          classe: "jour-detail",
          texte: `${jour.duree_min} min${plafond ? ` · palier ${plafond} au plus` : ""}`,
        }),
        selecteurParcours,
        bouton
      )
    );
  }
  refs.planJour.append(
    creerElement("p", {
      classe: "jour-note",
      texte: "Le palier indiqué est une borne de la semaine, jamais un objectif : c’est la maîtrise qui décide.",
    })
  );
}

/** Vue d'ensemble des 8 semaines (durée, rythme, plafonds). */
function rendreSemaines(programme) {
  refs.semainesProgramme.replaceChildren();
  for (const semaine of programme.semaines || []) {
    const compte = { seance: 0, legere: 0, repos: 0 };
    for (const jour of semaine.jours || []) {
      if (compte[jour.type] !== undefined) compte[jour.type] += 1;
    }
    const plafonds = Object.entries(semaine.plafond_palier || {})
      .map(([theme, palier]) => `${nomTheme(theme)} ≤ ${palier}`)
      .join(" · ");
    refs.semainesProgramme.append(
      creerElement("article", { classe: "carte carte-semaine" },
        creerElement("h4", { texte: `Semaine ${semaine.semaine} — ${semaine.duree_min} min` }),
        creerElement("p", {
          texte: `${compte.seance} séances · ${compte.legere} journée légère · ${compte.repos} repos`,
        }),
        creerElement("p", { classe: "semaine-plafonds", texte: plafonds })
      )
    );
  }
}

/** Règles du programme, en clair. */
function rendreRegles(regles) {
  refs.reglesProgramme.replaceChildren();
  const entrees = Object.entries(regles || {});
  if (!entrees.length) return;
  refs.reglesProgramme.append(creerElement("h3", { classe: "titre-note", texte: "Comment ça marche" }));
  const liste = creerElement("ul", { classe: "liste-regles" });
  for (const [cle, texte] of entrees) {
    liste.append(
      creerElement("li", {},
        creerElement("strong", { texte: `${LIBELLES_REGLES[cle] || cle} — ` }),
        document.createTextNode(texte)
      )
    );
  }
  refs.reglesProgramme.append(liste);
}

/** Nom d'un thème depuis son identifiant (secours : l'identifiant brut). */
function nomTheme(identifiant) {
  const theme = etat.themesParId.get(identifiant);
  return theme ? theme.nom : identifiant;
}

/* ---------------------------------------------------------------------
   Grille de déduction 3×3 : figures × couleurs, indices à recouper
   --------------------------------------------------------------------- */

const GLYPHES = { cercle: "●", carre: "■", triangle: "▲", losange: "◆" };
//: Thèmes où la dictée n'a pas de sens : la réponse est du code (indentation, symboles).
const THEMES_SANS_DICTEE = new Set(["python"]);
//: Libellés affichés des figures (les identifiants de contenu sont sans accent).
const LIBELLES_FIGURES = { cercle: "cercle", carre: "carré", triangle: "triangle", losange: "losange" };
const libelleFigure = (figure) => LIBELLES_FIGURES[figure] || figure;
const TEINTES = { rouge: "#e2574c", bleu: "#5b8dd9", vert: "#5aa469", jaune: "#d9b04a" };
const NOMS_CASES_3 = [
  "en haut à gauche", "en haut au centre", "en haut à droite",
  "au milieu à gauche", "au centre", "au milieu à droite",
  "en bas à gauche", "en bas au centre", "en bas à droite",
];
const NOMS_LIGNES_3 = ["du haut", "du milieu", "du bas"];
const NOMS_COLONNES_3 = ["de gauche", "du centre", "de droite"];
const NOMS_CASES_4 = [
  "en haut à gauche", "en haut, deuxième", "en haut, troisième", "en haut à droite",
  "deuxième ligne à gauche", "deuxième ligne, deuxième", "deuxième ligne, troisième", "deuxième ligne à droite",
  "troisième ligne à gauche", "troisième ligne, deuxième", "troisième ligne, troisième", "troisième ligne à droite",
  "en bas à gauche", "en bas, deuxième", "en bas, troisième", "en bas à droite",
];
const NOMS_LIGNES_4 = ["1", "2", "3", "4"];
const NOMS_COLONNES_4 = ["1", "2", "3", "4"];

function nomsPour(n) {
  return {
    cases: n === 4 ? NOMS_CASES_4 : NOMS_CASES_3,
    lignes: n === 4 ? NOMS_LIGNES_4 : NOMS_LIGNES_3,
    colonnes: n === 4 ? NOMS_COLONNES_4 : NOMS_COLONNES_3,
  };
}

/** Formule un indice structuré en français lisible (n = taille de la grille).
 *  Chaque indice porte deux informations : une figure colorée et sa place
 *  (ou sa relation à une autre figure colorée). */
/** Contrainte élémentaire de position : complément + forme négative. */
function predicatAtome(atome, n) {
  const noms = nomsPour(n);
  switch (atome.type) {
    case "case": return { texte: `${noms.cases[atome.case]}`, negation: null };
    case "ligne": return { texte: `sur la ligne ${noms.lignes[atome.ligne]}`, negation: null };
    case "colonne": return { texte: `dans la colonne ${noms.colonnes[atome.colonne]}`, negation: null };
    case "pas-ligne": return { texte: `sur la ligne ${noms.lignes[atome.ligne]}`, negation: "pas" };
    case "pas-colonne": return { texte: `dans la colonne ${noms.colonnes[atome.colonne]}`, negation: "pas" };
    case "coin": return { texte: "dans un coin", negation: null };
    case "diagonale": return { texte: "sur la diagonale descendante (du coin haut gauche au coin bas droit)", negation: null };
    case "diagonale-inverse": return { texte: "sur la diagonale montante (du coin haut droit au coin bas gauche)", negation: null };
    case "pas-diagonale": return { texte: "sur la diagonale descendante", negation: "pas" };
    case "pas-diagonale-inverse": return { texte: "sur la diagonale montante", negation: "pas" };
    case "pas-coin": return { texte: "dans un coin", negation: "pas" };
    case "pas-bord": return { texte: "sur le bord", negation: "pas" };
    case "ni-ni": return { texte: "dans un coin ni sur le bord", negation: "ni" };
    default: return { texte: "", negation: null };
  }
}

/** Relation entre deux figures colorées, formulée depuis la première. */
function relationAtome(atome, n) {
  const cible = `${libelleFigure(atome.figure2)} ${atome.couleur2}`;
  switch (atome.type) {
    case "voisin-gauche": return `est juste à gauche du ${cible}`;
    case "voisin-droite": return `est juste à droite du ${cible}`;
    case "voisin-dessus": return `est juste au-dessus du ${cible}`;
    case "voisin-dessous": return `est juste en dessous du ${cible}`;
    case "pas-voisin-gauche": return `n'est pas juste à gauche du ${cible}`;
    case "pas-voisin-droite": return `n'est pas juste à droite du ${cible}`;
    case "pas-voisin-dessus": return `n'est pas juste au-dessus du ${cible}`;
    case "pas-voisin-dessous": return `n'est pas juste en dessous du ${cible}`;
    case "pas-a-droite-de": return `n'est pas plus à droite que le ${cible}`;
    case "pas-a-gauche-de": return `n'est pas plus à gauche que le ${cible}`;
    case "pas-au-dessus-de": return `n'est pas plus haut que le ${cible}`;
    case "pas-en-dessous-de": return `n'est pas plus bas que le ${cible}`;
    case "voisin-diagonale": return `touche le ${cible} en diagonale`;
    case "oppose": return `est à l'opposé du ${cible}, de l'autre côté du centre`;
    case "comparaison": return `est sur la même ligne que le ${cible}, à sa gauche`;
    case "a-droite-de": return `est plus à droite que le ${cible}`;
    case "a-gauche-de": return `est plus à gauche que le ${cible}`;
    case "au-dessus-de": return `est plus haut que le ${cible}`;
    case "en-dessous-de": return `est plus bas que le ${cible}`;
    case "autre-ligne": return `n'est pas sur la même ligne que le ${cible}`;
    case "autre-colonne": return `n'est pas dans la même colonne que le ${cible}`;
    case "si-alors": return `si le ${cible} est dans un coin, alors lui aussi est sur le bord`;
    default: return "";
  }
}

/** Prédicat complet d'une information, verbe compris. */
function phraseAtome(atome, n) {
  const position = predicatAtome(atome, n);
  if (!position.texte) return relationAtome(atome, n);
  if (position.negation === "pas") return `n'est pas ${position.texte}`;
  if (position.negation === "ni") return `n'est ni ${position.texte}`;
  return `est ${position.texte}`;
}

/** Retire le « est » de tête quand la phrase enchaîne deux prédicats. */
function sansEst(texte) {
  return texte.startsWith("est ") ? texte.slice(4) : texte;
}

/** Un sélecteur peut désigner une catégorie, sans identifier sa couleur ou sa forme. */
function libelleCategorie(categorie) {
  if (categorie.figure && categorie.couleur) return `${libelleFigure(categorie.figure)} ${categorie.couleur}`;
  if (categorie.figure) return `pion de forme ${libelleFigure(categorie.figure)}`;
  return `pion de couleur ${categorie.couleur}`;
}

/** Ces contraintes appartiennent à cette grille, jamais aux règles permanentes. */
function formaterIndiceCollectif(indice, n) {
  const noms = nomsPour(n);
  const zone = indice.numero === "chaque"
    ? `Chaque ${indice.zone}`
    : `La ${indice.zone} ${(indice.zone === "ligne" ? noms.lignes : noms.colonnes)[indice.numero]}`;
  if (indice.type === "compte-categorie") {
    const categorie = libelleCategorie(indice.categorie);
    if (indice.nombre === 0) return `${zone} ne contient aucun ${categorie}.`;
    // Le nom « pion(s) » évite de pluraliser chaque nom de forme.
    const complement = indice.categorie.figure && indice.categorie.couleur
      ? `de forme ${libelleFigure(indice.categorie.figure)} et de couleur ${indice.categorie.couleur}`
      : indice.categorie.figure
        ? `de forme ${libelleFigure(indice.categorie.figure)}`
        : `de couleur ${indice.categorie.couleur}`;
    return `${zone} contient exactement ${indice.nombre} pion${indice.nombre > 1 ? "s" : ""} ${complement}.`;
  }
  if (indice.type === "diversite") {
    return `${zone} contient exactement un pion de chaque ${indice.attribut === "figure" ? "forme" : "couleur"}.`;
  }
  if (indice.type === "entre") {
    const [a, b] = indice.extremites;
    const extremites = a.figure === b.figure && a.couleur === b.couleur
      ? `deux pions ${a.figure ? `de forme ${libelleFigure(a.figure)}` : ""}${a.figure && a.couleur ? " et " : ""}${a.couleur ? `de couleur ${a.couleur}` : ""}`
      : `un ${libelleCategorie(a)} et un ${libelleCategorie(b)}`;
    const alignement = indice.axe === "ligne" ? "sur une même ligne"
      : indice.axe === "colonne" ? "dans une même colonne" : "sur une même diagonale";
    // En 3×3, trois pions alignés occupent forcément trois cases consécutives.
    // La précision sur les distances ne devient utile que pour une grille plus grande.
    const precision = n > 3 ? ", sans être nécessairement voisins ni à égale distance" : "";
    return `Le ${libelleFigure(indice.figure)} ${indice.couleur} est strictement entre ${extremites}, ${alignement}${precision}.`;
  }
  return null;
}

/** Formule une phrase en français lisible (n = taille de la grille).
 *  Une phrase est une **chaîne** : un repère sur une figure, puis des relations
 *  d'une figure à la suivante (« …, qui est juste au-dessus du … »). */
function formaterEnonce(indice, n) {
  if (["compte-categorie", "diversite", "entre"].includes(indice.type)) {
    return formaterIndiceCollectif(indice, n);
  }
  const atomes = [indice, ...(Array.isArray(indice.et) ? indice.et : [])];
  const nomDe = (atome) =>
    `${libelleFigure(atome.figure || indice.figure)} ${atome.couleur || indice.couleur}`;

  let texte = "";
  let sujet = null;
  let cible = null;
  atomes.forEach((atome, rang) => {
    const ceSujet = `${atome.figure || indice.figure}:${atome.couleur || indice.couleur}`;
    const predicat = phraseAtome(atome, n);
    if (rang === 0) {
      texte += `Le ${nomDe(atome)} ${predicat}`;
    } else if (ceSujet === sujet) {
      texte += ` et ${predicat}`;
    } else if (ceSujet === cible) {
      texte += `, qui ${predicat}`;
    } else {
      texte += `, et le ${nomDe(atome)} ${predicat}`;
    }
    sujet = ceSujet;
    cible = atome.figure2 ? `${atome.figure2}:${atome.couleur2}` : null;
  });
  return texte + ".";
}

/** Trois aides successives fondées sur les seules phrases de la grille. */
function formaterAideRaisonnement(aide, n, niveau) {
  const pion = `${libelleFigure(aide.figure)} ${aide.couleur}`;
  const references = aide.phrases.join(", ");
  const cases = nomsPour(n).cases;
  if (niveau === 0) return `Observe les phrases ${references}. Cherche où peut se trouver le ${pion}. Croise ces informations avant de placer le pion.`;
  if (niveau === 1 && aide.mode === "croisement") {
    const premiere = (aide.demonstration || []).find(e => e.reductions.some(r => r.cases.length > 1));
    const details = premiere ? premiere.reductions.filter(r => r.cases.length > 1).map(r =>
      `${libelleFigure(r.figure)} ${r.couleur} : ${r.cases.map(c => cases[c]).join(" ; ")}.`).join("\n") : "";
    return `Commence par appliquer la phrase ${premiere ? premiere.phrase : aide.phrases[0]}. Compare les possibilités restantes :\n${details}\nReprends ensuite les autres phrases citées : une case déjà occupée ne peut plus accueillir un autre pion.`;
  }
  if (niveau === 1) {
    const details = aide.phrases.map((rang, i) => `Phrase ${rang} : ${aide.possibilites[i].map(c => cases[c]).join(" ; ")}.`).join("\n");
    return `Pour le ${pion}, voici les cases encore possibles en appliquant chaque phrase séparément.\n${details}\n${aide.mode === "intersection" ? "Cherche la case commune à ces listes." : "Il faut aussi croiser les positions des autres pions : chaque case ne reçoit qu’un pion."}`;
  }
  if (aide.mode === "croisement") {
    const trace = aide.demonstration.map(e => `Avec la phrase ${e.phrase} et les possibilités déjà établies :\n` +
      e.reductions.map(r => `${libelleFigure(r.figure)} ${r.couleur} → ${r.cases.map(c => cases[c]).join(" ; ")}.`).join("\n")).join("\n\n");
    return `${trace}\n\nChaque pion et chaque case sont utilisés une fois. Ces éliminations donnent une seule position pour le ${pion} : ${cases[aide.case]}.`;
  }
  return aide.mode === "intersection"
    ? `La seule case commune aux possibilités des phrases ${references} est ${cases[aide.case]}. Le ${pion} y est donc placé : aucune information supplémentaire n’a été ajoutée.`
    : `En croisant les phrases ${references} et en tenant compte des cases occupées par les autres pions, une seule position reste possible pour le ${pion} : ${cases[aide.case]}. Chaque pion est utilisé une seule fois et chaque case reçoit un seul pion.`;
}

/** Étiquettes courtes des cases, pour le tableau de déduction. */
function nomsCourtsCases(n) {
  if (n === 4) {
    const noms = [];
    for (let ligne = 1; ligne <= 4; ligne += 1) {
      for (let colonne = 1; colonne <= 4; colonne += 1) noms.push(`L${ligne}C${colonne}`);
    }
    return noms;
  }
  return ["H·G", "H·C", "H·D", "M·G", "M·C", "M·D", "B·G", "B·C", "B·D"];
}

/** Aide facultative ajoutée au logiciel pour noter les possibilités.
 *  Une ligne par figure colorée, une colonne par case : ✗ exclu, ✓ certain. */
function rendreTableauDeduction(contenu) {
  const n = contenu.figures.length;
  const courts = nomsCourtsCases(n);
  const entete = creerElement("tr", {}, creerElement("th", { attributs: { scope: "col" } }),
    ...courts.map((nom) => creerElement("th", { texte: nom, attributs: { scope: "col" } })));
  const corps = creerElement("tbody");
  for (const couleur of contenu.couleurs) {
    for (const figure of contenu.figures) {
      const ligne = creerElement("tr");
      const titre = creerElement("th", { classe: "tableau-jeton", attributs: { scope: "row" } });
      titre.append(creerElement("span", { texte: GLYPHES[figure], attributs: { "aria-hidden": "true" } }));
      titre.append(creerElement("span", { texte: ` ${couleur}`, classe: "tableau-nom" }));
      titre.style.color = TEINTES[couleur];
      ligne.append(titre);
      for (let c = 0; c < n * n; c += 1) {
        const cellule = creerElement("td", {
          texte: "",
          attributs: {
            role: "button", tabindex: "0",
            "aria-label": `${libelleFigure(figure)} ${couleur} — case ${courts[c]}`,
          },
        });
        const basculer = () => {
          cellule.textContent = cellule.textContent === "" ? "✗" : cellule.textContent === "✗" ? "✓" : "";
          cellule.dataset.etat = cellule.textContent;
        };
        cellule.addEventListener("click", basculer);
        cellule.addEventListener("keydown", (evenement) => {
          if (evenement.key === "Enter" || evenement.key === " ") {
            evenement.preventDefault();
            basculer();
          }
        });
        ligne.append(cellule);
      }
      corps.append(ligne);
    }
  }
  const legende = n === 4
    ? "L = ligne (1 = haut), C = colonne (1 = gauche)."
    : "H = haut, M = milieu, B = bas · G = gauche, C = centre, D = droite.";
  return creerElement("details", { classe: "methode-panneau" },
    creerElement("summary", { texte: "Aide — noter les possibilités" }),
    creerElement("p", { classe: "tableau-legende",
      texte: `Ce brouillon facultatif permet de garder les possibilités sous les yeux. Tu peux faire l’exercice sans l’ouvrir. ${legende} Cliquez une case pour la marquer : ✗ impossible, ✓ certain.` }),
    creerElement("div", { classe: "tableau-enveloppe" },
      creerElement("table", { classe: "tableau-deduction" }, creerElement("thead", {}, entete), corps))
  );
}

/** Affiche la grille, la palette de jetons, les indices et l'indice de secours. */
function rendreGrille(item) {
  const contenu = item.contenu;
  const n = contenu.figures.length;
  etat.grille = Array(n * n).fill(null);
  etat.jetonChoisi = null;

  const plateau = creerElement("div", { classe: "grille-3x3" });
  plateau.style.gridTemplateColumns = `repeat(${n}, 3rem)`;
  plateau.style.gridAutoRows = "3rem";
  const cellules = [];
  for (let c = 0; c < n * n; c++) {
    const bouton = creerElement("button", {
      classe: "cellule",
      attributs: { type: "button", "aria-label": nomsPour(n).cases[c] },
    });
    bouton.addEventListener("click", () => placerCellule(c, bouton));
    plateau.append(bouton);
    cellules.push(bouton);
  }

  const palette = creerElement("div", { classe: "palette", attributs: { "aria-label": "Jetons disponibles" } });
  palette.style.gridTemplateColumns = `repeat(${n}, 2.7rem)`;
  palette.style.gridAutoRows = "2.7rem";
  const jetons = [];
  for (const couleur of contenu.couleurs) {
    for (const figure of contenu.figures) {
      const jeton = creerElement("button", {
        classe: "jeton",
        texte: GLYPHES[figure],
        attributs: {
          type: "button",
          "aria-label": `${libelleFigure(figure)} ${couleur}`,
          "data-jeton": `${figure}:${couleur}`,
          "data-nom": `${libelleFigure(figure)} ${couleur}`,
        },
      });
      jeton.style.color = TEINTES[couleur];
      jeton.addEventListener("click", () => {
        etat.jetonChoisi = `${figure}:${couleur}`;
        for (const j of jetons) j.classList.remove("jeton-actif");
        jeton.classList.add("jeton-actif");
      });
      palette.append(jeton);
      jetons.push(jeton);
    }
  }

  /** Grise les figures déjà posées : un jeton posé n'est plus sélectionnable.
   *  Il redevient disponible dès qu'il est retiré de la grille (clic sur sa case,
   *  ou « Vider la grille »). */
  function rafraichirPalette() {
    const places = new Set(etat.grille.filter(Boolean));
    for (const bouton of jetons) {
      const jeton = bouton.dataset.jeton;
      const pris = places.has(jeton);
      bouton.disabled = pris;
      bouton.classList.toggle("jeton-place", pris);
      bouton.setAttribute("aria-label", pris
        ? `${bouton.dataset.nom} — déjà placé dans la grille`
        : bouton.dataset.nom);
      if (pris) {
        bouton.classList.remove("jeton-actif");
        if (etat.jetonChoisi === jeton) etat.jetonChoisi = null;
      }
    }
  }

  const boutonVider = creerElement("button", {
    classe: "bouton bouton-secondaire",
    texte: "Vider la grille",
    attributs: { type: "button" },
  });
  boutonVider.addEventListener("click", () => {
    etat.grille = Array(n * n).fill(null);
    etat.jetonChoisi = null;
    for (const j of jetons) j.classList.remove("jeton-actif");
    for (const b of cellules) { b.textContent = ""; b.style.color = ""; }
    rafraichirPalette();
  });

  const boutonValider = creerElement("button", {
    classe: "bouton bouton-primaire bouton-large",
    texte: "Valider",
    attributs: { type: "button" },
  });
  boutonValider.addEventListener("click", () => {
    if (etat.grille.every(Boolean)) soumettreGrille();
  });

  const indices = creerElement("ol", { classe: "grille-indices" },
    ...contenu.enonces.map((e) => creerElement("li", { texte: formaterEnonce(e, n) }))
  );

  // Aides graduées ; compatibilité avec les anciens contenus à secours directs.
  let revele = 0;
  const aideRaisonnement = contenu.aide_raisonnement;
  const secours = Array.isArray(contenu.indices) ? contenu.indices : [];
  const listeSecours = creerElement("ul", { classe: "grille-indices grille-secours" });
  const boutonIndice = creerElement("button", {
    classe: "bouton bouton-secondaire",
    texte: aideRaisonnement ? "Aide au raisonnement" : "Un indice",
    attributs: { type: "button" },
  });
  boutonIndice.addEventListener("click", () => {
    if (aideRaisonnement) {
      if (revele >= 3) return;
      const texte = formaterAideRaisonnement(aideRaisonnement, n, revele);
      const paragraphe = creerElement("li", { texte });
      paragraphe.style.whiteSpace = "pre-line";
      listeSecours.append(paragraphe);
      revele += 1;
      boutonIndice.textContent = revele === 1 ? "Comparer les possibilités" : "Voir la conclusion expliquée";
      if (revele === 3) { boutonIndice.disabled = true; boutonIndice.textContent = "Aide affichée"; }
      return;
    }
    if (revele < secours.length) {
      listeSecours.append(creerElement("li", { texte: formaterEnonce(secours[revele], n) }));
      revele += 1;
      if (revele >= secours.length) boutonIndice.disabled = true;
    }
  });
  const zoneIndices = creerElement("div", {},
    contenu.methode_depart ? creerElement("p", { texte: contenu.methode_depart }) : null,
    indices,
    listeSecours,
    (aideRaisonnement || secours.length) ? boutonIndice : null
  );

  refs.zoneGrille.replaceChildren(
    creerElement("div", { classe: "grille-corps" }, plateau, palette),
    zoneIndices,
    rendreTableauDeduction(contenu),
    creerElement("div", { classe: "grille-actions" }, boutonVider, boutonValider)
  );
  refs.zoneGrille.hidden = false;

  rafraichirPalette();

  /** Pose, retire ou remplace un jeton :
   *  - un jeton est sélectionné → on le pose (ou il remplace celui de la case) ;
   *  - aucun jeton sélectionné → un clic sur une case occupée la vide. */
  function placerCellule(c, bouton) {
    const actuel = etat.grille[c];
    if (!etat.jetonChoisi && !actuel) return;
    const jeton = actuel === etat.jetonChoisi ? null : (etat.jetonChoisi || null);
    etat.grille[c] = jeton;
    if (jeton) {
      const [figure, couleur] = jeton.split(":");
      bouton.textContent = GLYPHES[figure];
      bouton.style.color = TEINTES[couleur];
    } else {
      bouton.textContent = "";
      bouton.style.color = "";
    }
    rafraichirPalette();
  }
}

/** Envoie la grille au serveur (chaîne « figure:couleur;… », ordre de lecture). */
async function soumettreGrille() {
  const chaine = etat.grille.map((cellule) => cellule || "").join(";");
  await soumettreValeur(chaine, null);
}

/** Feedback dédié : solution affichée, cases justes et fausses distinguées. */
function rendreFeedbackGrille(resultat) {
  const solution = String(resultat.attendue || "").split(";");
  const n = Math.round(Math.sqrt(solution.length)) || 3;
  refs.carteFeedback.replaceChildren();
  refs.carteFeedback.className =
    "carte-feedback " + (resultat.correcte ? "feedback-correct" : "feedback-incorrect");
  refs.carteFeedback.append(
    creerElement("p", {
      classe: "feedback-titre",
      texte: resultat.correcte ? "✓ Grille exacte !" : "✕ Pas tout à fait",
    })
  );
  const plateau = creerElement("div", { classe: "grille-3x3 grille-solution" });
  plateau.style.gridTemplateColumns = `repeat(${n}, 2.6rem)`;
  plateau.style.gridAutoRows = "2.6rem";
  for (let c = 0; c < solution.length; c++) {
    const cellule = creerElement("div", { classe: "cellule-solution" });
    const [figure, couleur] = (solution[c] || ":").split(":");
    cellule.textContent = GLYPHES[figure] || "";
    cellule.style.color = TEINTES[couleur] || "";
    cellule.classList.add(etat.grille && etat.grille[c] === solution[c] ? "bonne" : "mauvaise");
    plateau.append(cellule);
  }
  refs.carteFeedback.append(plateau);
  refs.carteFeedback.append(
    creerElement("p", { classe: "feedback-commentaire", texte: resultat.feedback })
  );
  refs.carteFeedback.hidden = false;
}

/** Zone de génération guidée d'une analyse du mot (SFA/PCA). */
function rendreGeneration(item) {
  const contenu = item.contenu;
  const bloc = creerElement("div", {});
  bloc.append(creerElement("p", { classe: "generation-consigne", texte: contenu.consigne || "" }));
  bloc.append(creerElement("p", { classe: "generation-definition", texte: contenu.definition || "" }));
  const etapes = creerElement("div", { classe: "generation-etapes" });
  for (const etape of contenu.etapes || []) {
    const ligne = creerElement("div", { classe: "generation-etape" });
    ligne.append(creerElement("label", { texte: etape }));
    ligne.append(creerElement("input", {
      classe: "champ",
      attributs: { type: "text", autocomplete: "off", spellcheck: "false" },
    }));
    etapes.append(ligne);
  }
  bloc.append(etapes);
  bloc.append(creerElement("p", {
    classe: "generation-note",
    texte: "Tes notes ne sont pas notées : elles servent seulement à retrouver le mot.",
  }));
  refs.zoneGeneration.replaceChildren(bloc);
  refs.zoneGeneration.hidden = false;
}

/* ---------------------------------------------------------------------
   Initialisation et branchements
   --------------------------------------------------------------------- */

function brancherEvenements() {
  // Entrée dans le champ = valider (soumission du formulaire).
  refs.formulaire.addEventListener("submit", (evenement) => {
    evenement.preventDefault();
    validerReponse();
  });

  refs.boutonSuivant.addEventListener("click", itemSuivant);

  // « Terminer la séance » : confirmation en deux temps, sans fenêtre brusque.
  refs.boutonTerminer.addEventListener("click", () => {
    if (etat.actionEnCours || !etat.session) return;
    if (!etat.confirmationFin) {
      etat.confirmationFin = true;
      refs.boutonTerminer.textContent = "Confirmer la fin ?";
      etat.minuterieConfirmation = setTimeout(reinitialiserConfirmationFin, 5000);
    } else {
      finirSeance();
    }
  });

  refs.boutonNouvelleSeance.addEventListener("click", revenirAuxThemes);
  refs.boutonMissions.addEventListener("click", ouvrirMissions);  refs.boutonProgramme.addEventListener("click", ouvrirProgramme);
  refs.boutonRetourProgramme.addEventListener("click", revenirAuxThemes);
  refs.boutonReperes.addEventListener("click", () => afficherVue("reperes"));
  refs.boutonRetourReperes.addEventListener("click", revenirAuxThemes);

  // Capacités du poste : écouter la consigne, répondre à voix haute.
  refs.boutonEcouter.addEventListener("click", () => {
    // Lecture à la demande (indépendante du réglage automatique).
    CAPACITES.lire(etat.enonceCourant);
  });
  refs.caseLectureAuto.addEventListener("change", () => {
    definirLectureAuto(refs.caseLectureAuto.checked);
    if (refs.caseLectureAuto.checked) {
      CAPACITES.lire(etat.enonceCourant);        // on entend tout de suite l'effet
    } else {
      CAPACITES.arreter();                       // coupée à tout moment
    }
  });

  // Réglage d'accueil : dérogation explicite au plafond du jour (ADR-021).
  if (refs.caseSansLimite) {
    refs.caseSansLimite.addEventListener("change", () => {
      definirSansLimite(refs.caseSansLimite.checked);
      majReglageSansLimite();
    });
  }
  refs.boutonDicter.addEventListener("click", () => {
    if (!etat.session || etat.repondu) return;
    const prefixe = refs.champReponse.value.trim();   // ne pas écraser ce qui est déjà saisi
    const afficher = (texte) => {
      refs.champReponse.value = [prefixe, texte].filter(Boolean).join(" ");
    };
    CAPACITES.dicter({
      onDebut: () => {
        refs.boutonDicter.textContent = "🎙️ Je t'écoute…";
        refs.champReponse.classList.add("champ-dictee");
      },
      // Transcription au fur et à mesure : la réponse s'écrit en direct.
      onPartiel: afficher,
      onResultat: (texte) => { afficher(texte); refs.champReponse.focus(); },
      onFin: () => {
        refs.boutonDicter.textContent = "🎤 Répondre à voix haute";
        refs.champReponse.classList.remove("champ-dictee");
      },
      onErreur: () => {
        refs.boutonDicter.textContent = "🎤 Répondre à voix haute";
        refs.champReponse.classList.remove("champ-dictee");
      },
    });
  });
  refs.boutonRetourJournal.addEventListener("click", revenirAuxThemes);
  refs.boutonEnregistrerNote.addEventListener("click", enregistrerNote);
}

function init() {
  if (refs.caseLectureAuto) refs.caseLectureAuto.checked = lectureAutoActivee();
  if (refs.caseSansLimite) refs.caseSansLimite.checked = sansLimiteActivee();
  majReglageSansLimite();
  brancherEvenements();
  afficherVue("themes");
  chargerThemes();
}

init();
