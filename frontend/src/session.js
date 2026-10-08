"use strict";

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

    // L'autorisation précède tout affichage/lecture de la première question.
    // Le flux ouvert est transféré à la dictée, sans deuxième demande d'accès.
    CAPACITES.libererPreparationDictee?.();
    annulerMemo();
    reinitialiserConfirmationFin();
    resetSessionState();
    etat.dicteeAutoAutorisee = false;
    if (theme.id === "evocation" && donnees.items.some(item => item.type === "rappel-indice")) {
      montrerNoticeThemes("Préparation du microphone… En cas de refus, tu répondras au clavier.");
      etat.dicteeAutoAutorisee = Boolean(await CAPACITES.autoriserDictee?.());
    }
    etat.theme = theme;
    etat.session = donnees;
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

function cloreSessionSilencieusement(theme, sessionId) {
  if (!sessionId) return;
  apiFetch(`/${encodeURIComponent(theme.id)}/sessions/${encodeURIComponent(sessionId)}/fin`, {
    method: "POST",
  }).catch(() => { /* rien à signaler : l'utilisateur n'a rien à faire */ });
}

function preparerEcranSeance() {
  refs.titres.seance.textContent = etat.theme.nom;
  refs.carteFeedback.hidden = true;
  refs.boutonSuivant.hidden = true;
  masquerBandeau();
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

function annulerMemo() {
  etat.autoDictee?.abort();
  etat.autoDictee = null;
  etat.dicteeActive?.abort();
  etat.dicteeActive = null;
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

async function validerReponse() {
  // Terminer la transcription avant de juger le texte, sans valider un aperçu.
  if (etat.dicteeActive) { etat.dicteeActive.stop(); return; }
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

async function soumettreValeur(brut, indiceUtilise) {
  if (etat.actionEnCours || etat.repondu || !etat.session) return;
  etat.autoDictee?.abort();
  etat.autoDictee = null;

  const item = etat.session.items[etat.indexItem];
  // Séquence guidée : le payload est déjà l'objet des réponses par étape.
  const handler = handlerPour(item);
  const corps = {
    item_id: item.id,
    reponse: handler.readAnswer(brut),
    temps_ms: Math.max(0, Date.now() - etat.debutQuestion),
  };
  if (Number.isInteger(indiceUtilise) && indiceUtilise > 0) {
    corps.indice_utilise = indiceUtilise;
  }
  etat.reponseSoumise = typeof brut === "object" ? "" : String(brut);

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
      handler.renderFeedback(resultat);
      etat.actionEnCours = false;
      reglerEtatBoutons();
      return;
    }
    etat.repondu = true;

    // Feedback : statut + réponse attendue (après coup) + commentaire serveur.
    handler.renderFeedback(resultat);
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
    programmerSuiteLexicale(resultat, item);
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

function programmerSuiteLexicale(resultat, item) {
  if (resultat.correcte !== true || etat.theme?.id !== "evocation"
      || item.type !== "rappel-indice") return;
  const session = etat.session;
  const index = etat.indexItem;
  etat.minuteriesMemo.push(setTimeout(() => {
    if (etat.session !== session || etat.indexItem !== index
        || !etat.repondu || etat.actionEnCours) return;
    itemSuivant();
  }, 3000));
}

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

async function finirSeance() {
  if (etat.actionEnCours || !etat.session) return;
  CAPACITES.libererPreparationDictee?.();
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

function reinitialiserConfirmationFin() {
  etat.confirmationFin = false;
  if (etat.minuterieConfirmation) {
    clearTimeout(etat.minuterieConfirmation);
    etat.minuterieConfirmation = null;
  }
  refs.boutonTerminer.textContent = "Terminer la séance";
}
