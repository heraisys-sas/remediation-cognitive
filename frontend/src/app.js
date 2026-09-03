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

/* ---------------------------------------------------------------------
   Raccourcis DOM (l'HTML statique porte toutes les vues)
   --------------------------------------------------------------------- */

const $ = (id) => document.getElementById(id);

const refs = {
  vues: {
    themes: $("vue-themes"),
    seance: $("vue-seance"),
    resume: $("vue-resume"),
  },
  titres: {
    themes: $("titre-themes"),
    seance: $("titre-seance"),
    resume: $("titre-resume"),
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

/**
 * Normalise la saisie pour le corps de POST /reponses (contrat : str | number).
 * Thème calcul-mental : si la saisie est numérique, on envoie un nombre.
 * Sinon (anglais, prédiction de sortie…) on envoie la chaîne brute.
 */
function normaliserReponse(brut, theme) {
  const texte = brut.trim();
  if (theme && theme.id === "calcul-mental" && /^-?\d+(?:[.,]\d+)?$/.test(texte)) {
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

/** Affiche l'item courant : énoncé, aide éventuelle, champ vierge, progression. */
function montrerItem() {
  const items = etat.session.items;
  const item = items[etat.indexItem];
  const total = items.length;
  etat.repondu = false;

  // Progression discrète : « Question n sur max » + fine barre.
  refs.progressionTexte.textContent = `Question ${etat.indexItem + 1} sur ${total}`;
  refs.barreProgression.setAttribute("aria-valuemax", String(total));
  refs.barreProgression.setAttribute("aria-valuenow", String(etat.indexItem + 1));
  refs.barreRemplie.style.width = `${((etat.indexItem + 1) / total) * 100}%`;

  // Énoncé : grand texte ; variante monospace pour la prédiction de sortie.
  const contenu = item.contenu || {};
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

  // Champ de saisie : remise à zéro, clavier numérique pour le calcul mental.
  refs.champReponse.value = "";
  refs.champReponse.disabled = false;
  refs.champReponse.setAttribute(
    "inputmode",
    etat.theme.id === "calcul-mental" ? "numeric" : "text"
  );
  refs.indiceReponse.hidden = true;

  // On masque le feedback précédent et on redonne la main.
  refs.carteFeedback.hidden = true;
  refs.boutonSuivant.hidden = true;
  refs.formulaire.hidden = false;
  reglerEtatBoutons();

  etat.debutQuestion = Date.now();
  refs.champReponse.focus();
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

  const item = etat.session.items[etat.indexItem];
  const corps = {
    item_id: item.id,
    reponse: normaliserReponse(brut, etat.theme),
    temps_ms: Math.max(0, Date.now() - etat.debutQuestion),
  };

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
      afficherErreurReseau(validerReponse);
    } else if (erreur.type === "api" && (erreur.status === 404 || erreur.status === 409)) {
      refs.champReponse.disabled = true;
      afficherBandeau("Cette séance n’est plus disponible.", { retour: true });
    } else {
      afficherBandeau("La réponse n’a pas pu être vérifiée pour le moment.", {
        reessayer: validerReponse,
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
  refs.carteFeedback.replaceChildren();
  refs.carteFeedback.className =
    "carte-feedback " + (correcte ? "feedback-correct" : "feedback-incorrect");

  refs.carteFeedback.append(
    creerElement("p", {
      classe: "feedback-titre",
      texte: correcte ? "✓ Bonne réponse !" : "✕ Pas tout à fait",
    })
  );

  if (resultat.attendue !== undefined && resultat.attendue !== null) {
    const ligne = creerElement("p", { classe: "feedback-attendue" });
    ligne.append("Réponse attendue : ");
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
}

function init() {
  brancherEvenements();
  afficherVue("themes");
  chargerThemes();
}

init();
