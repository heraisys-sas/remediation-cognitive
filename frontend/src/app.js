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
const API_SOCIAL = "/api/social";

//: Types dont la réponse se choisit parmi des propositions (contenu.options).
const TYPES_A_CHOIX = new Set([
  "reconnaissance",
  "rappel-source",
  "emotion-vignette",
  "reponse-adaptee",
  "lecture-intention",
]);

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
  },
  titres: {
    themes: $("titre-themes"),
    seance: $("titre-seance"),
    resume: $("titre-resume"),
    missions: $("titre-missions"),
  },
  bandeau: $("bandeau-erreur"),
  bandeauMessage: $("bandeau-message"),
  boutonReessayer: $("bouton-reessayer"),
  boutonRetourThemes: $("bouton-retour-themes"),
  noticeThemes: $("notice-themes"),
  listeThemes: $("liste-themes"),
  progressionTexte: $("progression-texte"),
  barreProgression: $("barre-progression"),
  barreRemplie: $("barre-remplie"),
  enonce: $("enonce"),
  zoneMemo: $("zone-memo"),
  zoneChoix: $("zone-choix"),
  zoneIndices: $("zone-indices"),
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
  "production", "chaine-calcul", "serie-manquante", "double-tache",
  "empan", "paires-associatives",
]);

function inputmodePour(type) {
  return TYPES_REPONSE_NUMERIQUE.has(type) ? "numeric" : "text";
}

/** Annule les minuteries de la phase de mémorisation et masque la zone. */
function annulerMemo() {
  for (const minuterie of etat.minuteriesMemo) clearTimeout(minuterie);
  etat.minuteriesMemo = [];
  refs.zoneMemo.hidden = true;
  refs.zoneMemo.replaceChildren();
}

/**
 * Normalise la saisie pour le corps de POST /reponses (contrat : str | number).
 * Thèmes calcul-mental et concentration : saisie numérique → nombre.
 * Sinon (anglais, mémoire, prédiction de sortie…) on envoie la chaîne brute.
 */
function normaliserReponse(brut, theme) {
  const texte = brut.trim();
  if (
    theme && (theme.id === "calcul-mental" || theme.id === "concentration")
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

  try {
    const donnees = await apiFetch("/themes");
    masquerBandeau();
    rendreThemes(donnees.themes || []);
  } catch (erreur) {
    refs.listeThemes.replaceChildren();
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
  masquerNoticeThemes();

  if (!themes.length) {
    montrerNoticeThemes("Aucun thème disponible pour le moment — reviens bientôt.");
    return;
  }

  for (const theme of themes) {
    const carte = creerElement("article", { classe: "carte-theme" },
      creerElement("h3", { texte: theme.nom }),
      creerElement("p", { texte: theme.description || "" }),
      creerElement("button", {
        classe: "bouton bouton-primaire",
        texte: "Commencer",
        attributs: { type: "button" },
      })
    );
    carte.querySelector("button").addEventListener("click", () => demarrerSession(theme));
    refs.listeThemes.append(carte);
  }
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

async function demarrerSession(theme) {
  if (etat.actionEnCours) return;
  etat.actionEnCours = true;
  reglerEtatBoutons();

  try {
    const donnees = await apiFetch(
      `/${encodeURIComponent(theme.id)}/sessions`,
      { method: "POST" }
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
      montrerNoticeThemes(
        "Trois séances déjà faites aujourd’hui — le repos fait partie de l’entraînement."
      );
    } else if (erreur.type === "reseau") {
      afficherErreurReseau(() => demarrerSession(theme));
    } else {
      afficherBandeau("Impossible de démarrer la séance pour le moment.", {
        reessayer: () => demarrerSession(theme),
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
function montrerItem() {
  const items = etat.session.items;
  const item = items[etat.indexItem];
  const total = items.length;
  etat.repondu = false;
  etat.indicesReveles = 0;
  etat.optionChoisie = null;
  annulerMemo();

  // Progression discrète : « Question n sur max » + fine barre.
  refs.progressionTexte.textContent = `Question ${etat.indexItem + 1} sur ${total}`;
  refs.barreProgression.setAttribute("aria-valuemax", String(total));
  refs.barreProgression.setAttribute("aria-valuenow", String(etat.indexItem + 1));
  refs.barreRemplie.style.width = `${((etat.indexItem + 1) / total) * 100}%`;

  const contenu = item.contenu || {};
  if (contenu.affichage) {
    // Exercices de mémorisation : consigne → stimulus temporisé → question.
    afficherPhaseMemo(item);
    return;
  }
  afficherQuestion(item);
}

/** Phase de mémorisation : la consigne est posée, le stimulus attend le signal. */
function afficherPhaseMemo(item) {
  const contenu = item.contenu || {};
  const affichage = contenu.affichage;
  const estSequence = affichage.mode === "sequence";
  const dureeEstimee = estSequence
    ? Math.round((affichage.elements.length * (affichage.duree_par_item_ms + 250)) / 1000)
    : Math.round(affichage.duree_totale_ms / 1000);
  const mention = estSequence
    ? `${affichage.elements.length} éléments · environ ${dureeEstimee} s`
    : `${affichage.elements.length} paires · environ ${dureeEstimee} s`;

  // Consigne dans la carte énoncé ; le stimulus reste masqué jusqu'au signal
  // de l'utilisateur (set attentionnel : on sait quoi chercher avant de voir).
  refs.enonce.textContent = contenu.consigne ?? "Mémorise le contenu affiché.";
  refs.enonce.className = "enonce";
  refs.zoneAide.hidden = true;
  refs.carteFeedback.hidden = true;
  refs.boutonSuivant.hidden = true;
  refs.formulaire.hidden = true;

  const boutonAfficher = creerElement("button", {
    classe: "bouton bouton-primaire bouton-large",
    texte: "Afficher",
    attributs: { type: "button" },
  });
  boutonAfficher.addEventListener("click", () => jouerAffichage(item));
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
    etat.minuteriesMemo.push(
      setTimeout(() => afficherQuestion(item), affichage.duree_totale_ms)
    );
    return;
  }

  // Séquence : un élément à la fois, 250 ms de blanc entre chaque.
  const blancMemoMs = 250;
  let delai = 0;
  affichage.elements.forEach((element, index) => {
    etat.minuteriesMemo.push(setTimeout(() => {
      plateau.replaceChildren(
        creerElement("span", { classe: "memo-element", texte: element })
      );
      indicateur.textContent = `${index + 1} / ${affichage.elements.length}`;
    }, delai));
    delai += affichage.duree_par_item_ms;
    if (index < affichage.elements.length - 1) {
      etat.minuteriesMemo.push(setTimeout(() => { plateau.replaceChildren(); }, delai));
      delai += blancMemoMs;
    }
  });
  etat.minuteriesMemo.push(setTimeout(() => afficherQuestion(item), delai));
}

/** Phase question : le stimulus a disparu — énoncé, saisie, focus. */
function afficherQuestion(item) {
  annulerMemo();
  const contenu = item.contenu || {};

  // Énoncé : grand texte ; variante monospace pour la prédiction de sortie.
  refs.enonce.textContent = contenu.enonce ?? "";
  refs.enonce.className =
    "enonce" + (item.type === "prediction-sortie" ? " enonce-code" : "");

  // Aide optionnelle (contenu.aide) : repliée par défaut.
  if (contenu.aide) {
    refs.texteAide.textContent = contenu.aide;
    refs.zoneAide.hidden = false;
  } else {
    refs.texteAide.textContent = "";
    refs.zoneAide.hidden = true;
  }

  // Choix de réponse ou saisie libre selon le type d'exercice.
  const options = Array.isArray(contenu.options) ? contenu.options : null;
  const avecChoix = Boolean(options) && TYPES_A_CHOIX.has(item.type);
  refs.zoneChoix.replaceChildren();
  refs.zoneChoix.hidden = !avecChoix;
  refs.zoneIndices.replaceChildren();
  refs.zoneIndices.hidden = true;
  if (avecChoix) rendreOptions(options);
  refs.formulaire.hidden = avecChoix;

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
function rendreOptions(options) {
  const bac = creerElement("div", { classe: "grille-options" });
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
  const corps = {
    item_id: item.id,
    reponse: normaliserReponse(brut, etat.theme),
    temps_ms: Math.max(0, Date.now() - etat.debutQuestion),
  };
  if (Number.isInteger(indiceUtilise) && indiceUtilise > 0) {
    corps.indice_utilise = indiceUtilise;
  }

  etat.actionEnCours = true;
  reglerEtatBoutons();

  try {
    const resultat = await apiFetch(
      `/${encodeURIComponent(etat.theme.id)}/sessions/${encodeURIComponent(etat.session.session_id)}/reponses`,
      { method: "POST", body: JSON.stringify(corps) }
    );
    masquerBandeau();
    etat.repondu = true;

    // Feedback : statut + réponse attendue (après coup) + commentaire serveur.
    rendreFeedback(resultat);

    // On masque la saisie pour laisser toute la place au retour.
    refs.formulaire.hidden = true;

    const dernier = etat.indexItem === etat.session.items.length - 1;
    refs.boutonSuivant.textContent = dernier ? "Voir le résumé" : "Suivant";
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
  const correcte = Boolean(resultat.correcte);
  const assistee = Boolean(resultat.assistee);
  refs.carteFeedback.replaceChildren();
  refs.carteFeedback.className =
    "carte-feedback " +
    (assistee ? "feedback-assiste" : correcte ? "feedback-correct" : "feedback-incorrect");

  refs.carteFeedback.append(
    creerElement("p", {
      classe: "feedback-titre",
      texte: assistee ? "Réponse affichée" : correcte ? "✓ Bonne réponse !" : "✕ Pas tout à fait",
    })
  );

  if (resultat.attendue !== undefined && resultat.attendue !== null) {
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
  if (etat.indexItem < etat.session.items.length - 1) {
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

  // Proposition d'arrêt (arret_propose) : bienveillante, jamais forcée.
  refs.carteArret.hidden = !donnees.arret_propose;

  // Séances restantes aujourd'hui : information douce, l'utilisateur décide.
  const restantes = donnees.sessions_restantes_aujourdhui;
  let texteRestantes = "";
  if (Number.isFinite(restantes)) {
    if (restantes <= 0) {
      texteRestantes = "C’était la dernière séance du jour — à bientôt.";
    } else if (restantes === 1) {
      texteRestantes = "Il te reste une séance aujourd’hui, si tu en sens l’envie.";
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
    const donnees = await fetchSocial("/missions");
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
    await fetchSocial("/journal", {
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
    const donnees = await fetchSocial("/journal");
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

/** Appel direct du périmètre social (base /api/social, hors sessions). */
async function fetchSocial(chemin, options = {}) {
  const entetes = { "Accept": "application/json" };
  if (options.body !== undefined) entetes["Content-Type"] = "application/json";
  let reponse;
  try {
    reponse = await fetch(API_SOCIAL + chemin, { ...options, headers: entetes });
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
  refs.boutonMissions.addEventListener("click", ouvrirMissions);
  refs.boutonRetourJournal.addEventListener("click", revenirAuxThemes);
  refs.boutonEnregistrerNote.addEventListener("click", enregistrerNote);
}

function init() {
  brancherEvenements();
  afficherVue("themes");
  chargerThemes();
}

init();
