"use strict";

const CAPACITES = (typeof Capacites !== "undefined")
  ? Capacites
  : { voixDisponible: () => false, syntheseDisponible: () => false,
      dicter: () => null, lire: () => false, arreter: () => {} };

function lireSiLectureAuto(texte) {
  if (texte && lectureAutoActivee() && CAPACITES.syntheseDisponible()) lireTexteExercice(texte);
}

function lireTexteExercice(texte) {
  return CAPACITES.lire(texte, { francais: Boolean(etat.theme) && etat.theme.interface?.francais !== false });
}

function majModeDerogatoire() {
  $("reglages-derogatoires").hidden = !modeDerogatoireActif();
  for (const panneau of document.querySelectorAll(".reglages-essai")) {
    panneau.hidden = !modeDerogatoireActif();
  }
  majReglageSansLimite();
}

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

function revenirEnHaut() {
  const reduireMouvement = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  window.scrollTo({ top: 0, behavior: reduireMouvement ? "auto" : "smooth" });
}

function afficherVue(nom) {
  for (const [cle, section] of Object.entries(refs.vues)) {
    section.hidden = cle !== nom;
  }
  refs.titres[nom].focus({ preventScroll: true });
  revenirEnHaut();
}

function reglerEtatBoutons() {
  const enVol = etat.actionEnCours;
  refs.boutonValider.disabled = enVol || etat.repondu;
  refs.boutonSuivant.disabled = enVol || !etat.repondu;
  refs.boutonTerminer.disabled = enVol;
}

function formaterDuree(secondes) {
  if (!Number.isFinite(secondes) || secondes < 0) return "—";
  const minutes = Math.floor(secondes / 60);
  const reste = Math.round(secondes % 60);
  if (minutes === 0) return `${reste} s`;
  return `${minutes} min ${String(reste).padStart(2, "0")} s`;
}

function formaterTaux(taux) {
  if (!Number.isFinite(taux)) return "—";
  return `${Math.round(taux * 100)} %`;
}

function masquerBandeau() {
  refs.bandeau.hidden = true;
  refs.boutonReessayer.hidden = true;
  refs.boutonRetourThemes.hidden = true;
  refs.boutonReessayer.onclick = null;
  refs.boutonRetourThemes.onclick = null;
  etat.reessai = null;
}

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

function afficherErreurReseau(reessayer) {
  afficherBandeau(
    "Petit souci de connexion — vérifie le serveur, puis réessaie.",
    { reessayer }
  );
}

function montrerNoticeThemes(message) {
  refs.noticeThemes.textContent = message;
  refs.noticeThemes.hidden = false;
}

function masquerNoticeThemes() {
  refs.noticeThemes.hidden = true;
  refs.noticeThemes.textContent = "";
}

function majReglageSansLimite() {
  if (!refs.noteSansLimite) return;
  refs.noteSansLimite.textContent = sansLimiteActivee()
    ? "Limite levée — tu décides quand t’arrêter."
    : "Tous les exercices.";
}

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

  const prioritaires = ["deduction", "calcul-mental", "evocation", "methodes"];
  const themesOrdonnes = [
    ...prioritaires.flatMap(id => themes.filter(theme => theme.id === id)),
    ...themes.filter(theme => !prioritaires.includes(theme.id)),
  ];
  for (const theme of themesOrdonnes) {
    if (theme.id === "series-entendues") continue;
    let cible = refs.listeThemes;
    if (theme.interface?.extra === true) cible = refs.listeThemesExtra;
    else if (["evaluation", "cible"].includes(theme.categorie)) cible = refs.listeThemesEvaluation;
    const carte = carteTheme(theme, theme.id === "rappel-series"
      ? themes.find(t => t.id === "series-entendues") : null);
    cible.append(carte);
  }
  refs.sectionEvaluation.hidden = !refs.listeThemesEvaluation.childElementCount;
  refs.sectionExtra.hidden = !refs.listeThemesExtra.childElementCount;
}

function carteTheme(theme, parcoursAudio = null) {
  const carte = creerElement("article", { classe: "carte-theme" },
    creerElement("h3", { texte: theme.nom }),
    creerElement("p", { texte: theme.description || "" })
  );

  const optionsParcours = creerElement("details", { classe: "choix-parcours" },
    creerElement("summary", { texte: "Choisir le parcours" }));
  if (parcoursAudio || (theme.parcours || []).length) carte.append(optionsParcours);
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
      texte: "Auto — suivre ma progression",
      attributs: { value: "" },
    }));
    for (const palier of paliers) choix.append(creerElement("option", {
      texte: `Palier ${palier}${definition?.libelles_paliers?.[palier] ? " — " + definition.libelles_paliers[palier] : ""}`, attributs: { value: String(palier) },
    }));
    const memorise = preferenceLocale(`orthogone.palier.${themeChoisi.id}.${parcoursChoisi || "default"}`);
    if ([...choix.options].some(option => option.value === memorise)) choix.value = memorise;
    choix.hidden = paliers.length <= 1;
  }

  function majParcours() {
    if (!selecteurParcours) return;
    const parcours = themeChoisi.parcours || [];
    selecteurParcours.replaceChildren(...parcours.map(definition => creerElement("option", {
      texte: definition.nom, attributs: { value: definition.id },
    })));
    const memorise = preferenceLocale(`orthogone.parcours.${themeChoisi.id}`);
    parcoursChoisi = parcours.some(p => p.id === memorise) ? memorise : parcours[0]?.id || null;
    selecteurParcours.value = parcoursChoisi || "";
    selecteurParcours.hidden = parcours.length <= 1;
    const definition = parcours.find(p => p.id === parcoursChoisi);
    descriptionParcours.textContent = definition?.description || "Chaque parcours a sa propre progression.";
    majPaliers();
  }

  if (parcoursAudio) {
    const selecteur = creerElement("select", { classe: "selecteur-palier",
      attributs: { "aria-label": "Parcours de mémorisation" } });
    selecteur.append(creerElement("option", { texte: "Mots lus", attributs: { value: theme.id } }),
      creerElement("option", { texte: "Mots entendus", attributs: { value: parcoursAudio.id } }));
    const modalite = preferenceLocale(`orthogone.modalite.${theme.id}`, theme.id);
    selecteur.value = modalite === parcoursAudio.id ? parcoursAudio.id : theme.id;
    themeChoisi = selecteur.value === parcoursAudio.id ? parcoursAudio : theme;
    selecteur.addEventListener("change", () => {
      garderPreference(`orthogone.modalite.${theme.id}`, selecteur.value);
      themeChoisi = selecteur.value === parcoursAudio.id ? parcoursAudio : theme;
      majParcours();
    });
    optionsParcours.append(selecteur, creerElement("p", { classe: "ligne-discrete",
      texte: "La progression est distincte dans chaque parcours." }));
  }

  if ((theme.parcours || []).length || (parcoursAudio?.parcours || []).length) {
    selecteurParcours = creerElement("select", { classe: "selecteur-palier",
      attributs: { "aria-label": `Parcours pour ${theme.nom}` } });
    descriptionParcours = creerElement("p", { classe: "ligne-discrete" });
    selecteurParcours.addEventListener("change", () => {
      parcoursChoisi = selecteurParcours.value || null;
      garderPreference(`orthogone.parcours.${themeChoisi.id}`, parcoursChoisi || "");
      const definition = (themeChoisi.parcours || []).find(p => p.id === parcoursChoisi);
      descriptionParcours.textContent = definition?.description || "Progression indépendante.";
      majPaliers();
    });
    optionsParcours.append(selecteurParcours, descriptionParcours);
  }

  choix = creerElement("select", {
    classe: "selecteur-palier",
    attributs: { "aria-label": `Palier d'essai pour ${theme.nom}` },
  });
  const essais = creerElement("details", { classe: "reglages-essai" },
    creerElement("summary", { texte: "Réglages de cette séance" }), choix);
  essais.hidden = !modeDerogatoireActif();
  carte.append(essais);
  choix.addEventListener("change", () => {
    garderPreference(`orthogone.palier.${themeChoisi.id}.${parcoursChoisi || "default"}`, choix.value);
  });
  majParcours();
  majPaliers();

  const bouton = creerElement("button", {
    classe: "bouton bouton-primaire",
    texte: "Commencer",
    attributs: { type: "button" },
  });
  bouton.addEventListener("click", () => demarrerSession(
    themeChoisi, modeDerogatoireActif() && choix && choix.value ? Number(choix.value) : null, parcoursChoisi
  ));
  carte.append(bouton);
  return carte;
}

function revenirAuxThemes() {
  CAPACITES.libererPreparationDictee?.();
  annulerMemo();
  reinitialiserConfirmationFin();
  resetSessionState();
  afficherVue("themes");
  chargerThemes();
}


function brancherEvenements() {

  refs.formulaire.addEventListener("submit", (evenement) => {
    evenement.preventDefault();
    validerReponse();
  });

  $("case-mode-derogatoire").addEventListener("change", (evenement) => {
    garderPreference(CLE_MODE_DEROGATOIRE, evenement.target.checked ? "on" : "off");
    majModeDerogatoire();
  });
  refs.boutonSuivant.addEventListener("click", itemSuivant);

  refs.boutonTerminer.addEventListener("click", () => {
    if (etat.actionEnCours || !etat.session) return;
    if (!etat.confirmationFin) {
      etat.confirmationFin = true;
      refs.boutonTerminer.textContent = "Confirmer la fin ?";

    } else {
      finirSeance();
    }
  });

  refs.boutonNouvelleSeance.addEventListener("click", revenirAuxThemes);
  refs.boutonMissions.addEventListener("click", ouvrirMissions);  refs.boutonProgramme.addEventListener("click", ouvrirProgramme);
  refs.boutonRetourProgramme.addEventListener("click", revenirAuxThemes);
  refs.boutonReperes.addEventListener("click", () => afficherVue("reperes"));
  refs.boutonRetourReperes.addEventListener("click", revenirAuxThemes);

  refs.boutonEcouter.addEventListener("click", () => {

    if (CAPACITES.lectureEnCours?.()) CAPACITES.arreter();
    else lireTexteExercice(etat.enonceCourant);
  });
  refs.caseLectureAuto.addEventListener("change", () => {
    definirLectureAuto(refs.caseLectureAuto.checked);
    if (refs.caseLectureAuto.checked) {
      lireTexteExercice(etat.enonceCourant);        // on entend tout de suite l'effet
    } else {
      CAPACITES.arreter();                       // coupée à tout moment
    }
  });

  if (refs.caseSansLimite) {
    refs.caseSansLimite.addEventListener("change", () => {
      definirSansLimite(refs.caseSansLimite.checked);
      majReglageSansLimite();
    });
  }
  refs.boutonDicter.addEventListener("click", () => {
    if (etat.autoDictee) { etat.autoDictee.manuel(); return; }
    if (!etat.session || etat.repondu) return;
    if (etat.dicteeActive) { etat.dicteeActive.stop(); return; }
    CAPACITES.arreter();
    const sessionDictee = etat.session;
    const indexDictee = etat.indexItem;
    const prefixe = refs.champReponse.value.trim();   // ne pas écraser ce qui est déjà saisi
    const afficher = (texte) => {
      if (etat.session !== sessionDictee || etat.indexItem !== indexDictee || etat.repondu) return;
      refs.champReponse.value = [prefixe, texte].filter(Boolean).join(" ");
    };
    refs.boutonDicter.textContent = "Préparation de la dictée locale…";
    etat.dicteeActive = CAPACITES.dicter({
      onTraitement: () => { refs.boutonDicter.textContent = "Transcription locale…"; },
      onDebut: () => {
        refs.boutonDicter.textContent = "Parle maintenant · Terminer la dictée";
        refs.champReponse.classList.add("champ-dictee");
      },

      onPartiel: afficher,
      onResultat: (texte) => { afficher(texte); refs.champReponse.focus(); },
      onFin: () => {
        etat.dicteeActive = null;
        refs.boutonDicter.textContent = "🎤 Répondre à voix haute";
        refs.champReponse.classList.remove("champ-dictee");
      },
      onErreur: (code) => {
        etat.dicteeActive = null;
        const messages = {
          parole_non_detectee: "Aucune parole reconnue — réessaie",
          audio_vide: "Enregistrement trop court — réessaie",
          micro_refuse: "Autorise le microphone pour dicter",
          delai_depasse: "Transcription trop longue — réessaie",
          transcription_trop_longue: "Transcription trop longue — réessaie",
        };
        refs.boutonDicter.textContent = messages[code] || "Dictée locale indisponible — réessaie";
        refs.champReponse.classList.remove("champ-dictee");
      },
    });
  });
  refs.boutonRetourJournal.addEventListener("click", revenirAuxThemes);
  refs.boutonEnregistrerNote.addEventListener("click", enregistrerNote);
}

function initialiserChoixVoix() {
  const select = $("choix-voix");
  if (!select || !CAPACITES.voixLocales) return;
  const actualiser = () => {
    const voix = CAPACITES.voixLocales();
    select.replaceChildren(creerElement("option", {
      texte: voix.length ? "Automatique (voix locale)" : "Aucune voix française locale disponible",
      attributs: { value: "" },
    }), ...voix.map(v => creerElement("option", {
      texte: `${v.name} (${v.lang})`, attributs: { value: v.voiceURI },
    })));
    select.value = voix.some(v => v.voiceURI === CAPACITES.choixVoix()) ? CAPACITES.choixVoix() : "";
    select.disabled = voix.length === 0;
  };
  select.addEventListener("change", () => {
    CAPACITES.arreter();
    CAPACITES.choisirVoix(select.value);
  });
  window.speechSynthesis?.addEventListener("voiceschanged", actualiser);
  actualiser();
  CAPACITES.chargerVoixLocales?.().then(actualiser);
}

function actualiserBoutonAudio(active) {
  const bouton = refs.boutonEcouter;
  bouton.replaceChildren();
  bouton.setAttribute("aria-label", active ? "Arrêter la lecture" : "Écouter");
  bouton.title = active ? "Arrêter la lecture" : "Écouter";
  if (!active) { bouton.textContent = "Écouter"; return; }
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("aria-hidden", "true");
  svg.setAttribute("focusable", "false");
  const chemin = document.createElementNS(svg.namespaceURI, "path");
  chemin.setAttribute("d", "M3 9h4l5-4v14l-5-4H3z M16 9l5 6 M21 9l-5 6");
  svg.append(chemin);
  bouton.append(svg);
}

function init() {
  CAPACITES.observerLecture?.(actualiserBoutonAudio);
  initialiserChoixVoix();
  if (refs.caseLectureAuto) refs.caseLectureAuto.checked = lectureAutoActivee();
  if (refs.caseSansLimite) refs.caseSansLimite.checked = preferenceLocale(CLE_SANS_LIMITE) === "on";
  $("case-mode-derogatoire").checked = modeDerogatoireActif();
  majModeDerogatoire();
  brancherEvenements();
  afficherVue("themes");
  chargerThemes();
}

init();
