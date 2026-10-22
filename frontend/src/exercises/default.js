"use strict";

const TYPES_REPONSE_NUMERIQUE = new Set([
  "production",
  "empan", "paires-associatives", "estimation-temps",
]);

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

function aideGeneriquePourItem(item) {
  if (item.type === "grille-deduction") return "";
  return typeof item.contenu?.aide === "string" ? item.contenu.aide.trim() : "";
}

function afficherQuestion(item) {
  annulerMemo();
  const contenu = item.contenu || {};
  viderZonesReponse();
  // Capacités du poste : réinitialisées pour chaque question (la dictée ne
  // s'affiche que pour une réponse à saisir ; l'écoute suit la disponibilité).
  CAPACITES.arreter();
  const statutDictee = refs.formulaire.querySelector?.("#statut-dictee");
  if (statutDictee) statutDictee.hidden = true;
  refs.boutonDicter.hidden = true;
  refs.boutonDicter.textContent = "🎤 Répondre à voix haute";
  refs.boutonDicter.title = "Dicter une réponse";
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
    if (item.type !== "actualiser-consigne") lireSiLectureAuto(etat.enonceCourant);
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

  if (item.type === "analyse-mot") rendreGeneration(item);
  if (handlerPour(item).render?.(item)) return;

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
    && etat.theme.interface?.dictee !== false;
  refs.boutonDicter.hidden = !dicteePossible;

  // Indices progressifs (accès au mot) : proposés, jamais imposés.
  if (Array.isArray(contenu.indices) && contenu.indices.length) rendreIndices(item);

  // On masque le feedback précédent et on redonne la main.
  refs.carteFeedback.hidden = true;
  refs.boutonSuivant.hidden = true;
  reglerEtatBoutons();

  observationContexte(item, true);
  etat.debutQuestion = Date.now();
  if (dicteePossible && etat.dicteeAutoAutorisee && etat.theme.id === "evocation" && item.type === "rappel-indice") {
    const session = etat.session;
    etat.autoDictee = DicteeAuto.demarrer({
      capacites: CAPACITES,
      verifier: transcription => apiFetch(
        `/evocation/sessions/${encodeURIComponent(session.session_id)}/verifier-dictee`,
        { method: "POST", body: JSON.stringify({ item_id: item.id, transcription }) }),
      afficher: texte => { refs.champReponse.value = texte; },
      statut: texte => {
        refs.boutonDicter.textContent = texte;
        refs.boutonDicter.title = texte;
        if (statutDictee) { statutDictee.textContent = texte; statutDictee.hidden = false; }
      },
      clavier: disponible => {
        if (disponible === false) etat.dicteeAutoAutorisee = false;
        if (statutDictee) statutDictee.hidden = true;
        etat.autoDictee = null;
        refs.boutonDicter.textContent = "🎤 Répondre à voix haute";
        refs.champReponse.focus();
      },
      valider: texte => { etat.autoDictee = null; soumettreValeur(texte, etat.indicesReveles); },
    });
  }
  if (avecChoix) {
    const premier = refs.zoneChoix.querySelector("button");
    if (premier) premier.focus();
  } else {
    refs.champReponse.focus();
  }
}

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
    refs.carteFeedback.hidden = false;
    rendreFeedbackSequence(resultat);
    const item = etat.session?.items[etat.indexItem];
    if (item?.type === "pqrst-mise-en-oeuvre") {
      refs.carteFeedback.append(creerAccompagnementPqrst(
        item.contenu?.texte || "", etat.sequence?.["4"] || "", etat.sequence?.["2"] || ""
      ));
    }
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

  const imageContexte = etat.session?.items[etat.indexItem]?.contenu?.affichage?.image;
  if (!correcte && imageContexte && etat.phaseContextes === "rappel") {
    const image = creerElement("img", { classe: "scene-contexte", attributs: {
      src: imageContexte.src, srcset: imageContexte.srcset,
      sizes: "(max-width: 640px) calc(100vw - 40px), 592px",
      width: String(imageContexte.width), height: String(imageContexte.height),
      alt: `Scène à retrouver : ${resultat.attendue}. ${imageContexte.alt}`,
      decoding: "async",
    } });
    const figure = creerElement("figure", { classe: "scene-source" }, image);
    const observation = observationContexte(etat.session.items[etat.indexItem]);
    image.addEventListener("load", () => {
      if (observation && figure.isConnected) {
        observation.photo_apres_erreur = true;
        observation.photo_revelee_ms = Date.now();
      }
    }, { once: true });
    image.addEventListener("error", () => {
      if (observation) observation.incident_photo = true;
      figure.replaceChildren(creerElement("p", {
        texte: "La scène n’a pas pu être chargée. La réponse attendue reste indiquée ci-dessus.",
      }));
    }, { once: true });
    refs.carteFeedback.append(figure);
  }
  refs.carteFeedback.hidden = false;
}

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

function inputmodePour(type) {
  return TYPES_REPONSE_NUMERIQUE.has(type) ? "numeric" : "text";
}

function clefMot(texte) {
  return String(texte ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

function motsDe(texte) {
  return String(texte ?? "")
    .split(/[^0-9A-Za-z\u00C0-\u024F']+/)
    .filter(Boolean)
    .map(clefMot);
}

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

function viderZonesReponse() {
  for (const zone of [refs.zoneChoix, refs.zoneIndices, refs.zoneGeneration, refs.zoneGrille,
                      refs.zoneSequence]) {
    zone.replaceChildren();
    zone.hidden = true;
  }
}
