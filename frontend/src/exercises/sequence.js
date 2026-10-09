"use strict";

let sequenceActive = null;

function nettoyerSequence() {
  sequenceActive?.nettoyer();
  sequenceActive = null;
}

function snapshotPqrst() {
  return sequenceActive?.snapshot() || null;
}

function rendreSequence(item) {
  nettoyerSequence();
  const contenu = item.contenu || {};
  const etapes = new Map((contenu.etapes || []).map(e => [e.etape, e]));
  const mots = contenu.interface_pqrst || {};
  const texte = (cle, valeurs = {}) => String(mots[cle] || "").replace(
    /\{(\w+)\}/g, (_, nom) => String(valeurs[nom] ?? ""));
  const reponse = etat.sequence = { "5": [], _pqrst: {
    version: "pqrst-sequence-v1", etapes_realisees: [], statuts: {}, tentatives: {},
    relectures: [], interruptions: {}, modele_avant_test: false, phase: "pret",
    reprise_apres_correction: Object.hasOwn(etat.reponsesAttendues || {}, item.id),
  }};
  const meta = reponse._pqrst;
  const zone = refs.zoneSequence;
  const brouillons = {};
  let phase = "pret", cibleRelecture = null, pause = false, revision = 0;
  const realisee = cle => { if (!meta.etapes_realisees.includes(cle)) meta.etapes_realisees.push(cle); };
  const active = () => etat.sequence === reponse && !etat.repondu && !refs.vues?.seance?.hidden;
  const changer = suivante => { phase = suivante; meta.phase = suivante; rendre(); };
  const paragraphe = (valeur, classe = "") => zone.append(creerElement("p", { texte: valeur, classe }));
  const action = (cle, fn, primaire = false) => {
    const rendu = revision;
    const bouton = creerElement("button", {
      texte: texte(cle), classe: `bouton ${primaire ? "bouton-primaire" : "bouton-secondaire"}`,
      attributs: { type: "button" },
    });
    bouton.addEventListener("click", () => {
      if (rendu === revision && !etat.actionEnCours && !etat.repondu) fn();
    });
    zone.append(creerElement("div", { classe: "sequence-actions" }, bouton));
    return bouton;
  };
  function enregistrer(cle, valeur) {
    const statut = valeur === null ? "absence_declaree" : "reponse";
    if (!(cle in meta.statuts)) {
      meta.statuts[cle] = statut;
      if (cle.startsWith("5.")) reponse["5"][Number(cle.slice(2))] = valeur;
      else reponse[cle] = valeur;
    }
    if (cle === "4" || cle.startsWith("5.")) {
      const interrompue = Boolean(meta.interruptions[cle]);
      const aide = meta.relectures.includes(cle)
        || (cle.startsWith("5.") && meta.relectures.some(p => p.startsWith("5.")));
      (meta.tentatives[cle] ||= []).push({ reponse: valeur,
        condition: interrompue ? "reprise_interrompue" : aide ? "apres_relecture" : "sans_relecture",
        modalite: cle === "4" ? "clavier" : "choix",
      });
    }
    realisee(({ "1": "P", "2": "Q", "4": "S", "5.0": "T1", "5.1": "T2" })[cle]);
  }
  function rendreReponse(cle, options, suite) {
    const aidee = meta.relectures.includes(cle);
    const exposee = aidee || (cle.startsWith("5.") && meta.relectures.some(p => p.startsWith("5.")));
    if (exposee) paragraphe(texte("aidee"));
    const valider = valeur => { enregistrer(cle, valeur); delete brouillons[cle]; suite(); };
    let bouton;
    if (options) {
      const choix = creerElement("div", { classe: "sequence-choix" });
      options.forEach(option => {
        const b = creerElement("button", { texte: option, classe: "sequence-option",
          attributs: { type: "button", "aria-pressed": String(brouillons[cle] === option) } });
        if (brouillons[cle] === option) b.classList.add("sequence-option-active");
        b.addEventListener("click", () => {
          if (etat.actionEnCours) return;
          brouillons[cle] = option;
          for (const autre of choix.children) {
            autre.classList.remove("sequence-option-active"); autre.setAttribute("aria-pressed", "false");
          }
          b.classList.add("sequence-option-active"); b.setAttribute("aria-pressed", "true");
          bouton.disabled = false;
          if (relire) relire.hidden = false;
          if (absenceRelire) absenceRelire.hidden = true;
        });
        choix.append(b);
      });
      zone.append(choix);
    } else {
      const label = creerElement("label", { texte: texte(cle === "2" ? "question" : "reformulation") });
      const champ = creerElement("textarea", { classe: "sequence-champ",
        attributs: { rows: "3", maxlength: "2000" } });
      champ.value = brouillons[cle] || "";
      champ.addEventListener("input", () => {
        brouillons[cle] = champ.value.trim(); bouton.disabled = !brouillons[cle];
        if (relire) relire.hidden = !brouillons[cle];
        if (absenceRelire) absenceRelire.hidden = Boolean(brouillons[cle]);
      });
      label.append(champ); zone.append(label);
    }
    bouton = action("valider", () => { if (brouillons[cle]) valider(brouillons[cle]); }, true);
    bouton.disabled = !brouillons[cle];
    action(cle === "2" ? "sans_question" : "sans_reponse", () => valider(null));
    let relire = null, absenceRelire = null;
    if ((cle === "4" || cle.startsWith("5.")) && !aidee) {
      const relecture = valeur => {
        enregistrer(cle, valeur); delete brouillons[cle]; meta.relectures.push(cle);
        cibleRelecture = cle; changer("relecture");
      };
      relire = action("relire", () => { if (brouillons[cle]) relecture(brouillons[cle]); });
      absenceRelire = action("absence_relire", () => relecture(null));
      relire.hidden = !brouillons[cle]; absenceRelire.hidden = Boolean(brouillons[cle]);
    }
  }
  function suspendre() {
    if (!active() || pause || phase === "fin" || etat.actionEnCours) return;
    const interrompue = phase === "relecture" ? cibleRelecture : phase;
    meta.interruptions[interrompue] = Math.min(10000, (meta.interruptions[interrompue] || 0) + 1);
    pause = true; rendre();
  }
  function rendre() {
    revision += 1;
    CAPACITES.arreter();
    etat.dicteeActive?.abort(); etat.dicteeActive = null;
    etat.enonceCourant = "";
    for (const cle of ["enonce", "rappelConsigne", "texteAide", "methodeExercice", "noteReprise"]) {
      if (refs[cle]) { refs[cle].replaceChildren(); refs[cle].hidden = cle !== "enonce"; }
    }
    for (const cle of ["formulaire", "zoneChoix", "zoneIndices", "zoneGeneration", "zoneAide", "panneauMethode"])
      if (refs[cle]) refs[cle].hidden = true;
    zone.replaceChildren(); zone.hidden = false;
    if (pause) {
      paragraphe(texte("pause_titre")); paragraphe(texte("pause_detail"));
      action("reprendre", () => { pause = false; rendre(); }, true);
    } else if (phase === "pret") {
      paragraphe(texte("pret")); action("commencer", () => changer("P"), true);
    } else if (phase === "P") {
      paragraphe(texte("P"), "sequence-etape");
      paragraphe(contenu.titre_texte || "", "sequence-titre");
      paragraphe((contenu.texte || "").match(/^[^.!?]*[.!?]/)?.[0] || "", "sequence-texte");
      paragraphe(etapes.get(1)?.enonce || "");
      rendreReponse("1", etapes.get(1)?.options || [], () => changer("P-retour"));
    } else if (phase === "P-retour") {
      paragraphe(texte("sujet_attendu", { sujet: etapes.get(1)?.bonne || "" }));
      action("continuer", () => changer("Q"), true);
    } else if (phase === "Q") {
      paragraphe(texte("Q"), "sequence-etape");
      rendreReponse("2", null, () => changer("Q-retour"));
    } else if (phase === "Q-retour") {
      paragraphe(texte("question_modele", { modele: etapes.get(2)?.modele || "" }));
      action("vers_lecture", () => changer("R"), true);
    } else if (phase === "R" || phase === "relecture") {
      paragraphe(texte(phase === "R" ? "R" : "relecture"), "sequence-etape");
      if (phase === "R" && reponse["2"]) paragraphe(reponse["2"]);
      paragraphe(contenu.texte || "", "sequence-texte");
      action(phase === "R" ? "vers_reformulation" : "fin_relecture", () => {
        if (phase === "R") { realisee("R"); changer("4"); }
        else changer(cibleRelecture);
      }, true);
    } else if (phase === "4") {
      paragraphe(texte("S"), "sequence-etape");
      rendreReponse("4", null, () => changer("retour-S"));
    } else if (phase === "retour-S") {
      paragraphe(texte("retour-S"), "sequence-etape"); paragraphe(texte("retour_s"));
      const derniere = meta.tentatives["4"].at(-1).reponse;
      paragraphe(derniere === null ? texte("absence") : texte("production", { reponse: derniere }));
      paragraphe(texte("modele", { modele: etapes.get(4)?.modele || "" }), "sequence-texte");
      action("vers_test", () => { realisee("retour-S"); meta.modele_avant_test = true; changer("5.0"); }, true);
    } else if (phase.startsWith("5.")) {
      const rang = Number(phase.slice(2));
      paragraphe(texte("T", { numero: rang + 1, total: 2 }), "sequence-etape");
      paragraphe(texte("test_condition"));
      const q = etapes.get(5)?.questions?.[rang] || {};
      paragraphe(q.enonce || "", "sequence-question");
      rendreReponse(phase, q.options || [], () => changer(rang === 0 ? "5.1" : "fin"));
    } else if (phase === "fin") {
      paragraphe(texte("fin"));
      action("envoyer", () => soumettreValeur(reponse, 0), true);
    }
    if (!pause && phase !== "fin" && phase !== "pret") action("pause", suspendre);
    // La lecture ne conserve que le texte de l'écran actif, jamais un ancien support.
    etat.enonceCourant = Array.from(zone.querySelectorAll("p")).map(p => p.textContent).join(" ");
    refs.ligneAudio.hidden = !CAPACITES.syntheseDisponible();
    zone.querySelector("textarea, button")?.focus();
  }
  const visibilite = () => { if (document.hidden) suspendre(); };
  document.addEventListener("visibilitychange", visibilite);
  sequenceActive = {
    nettoyer: () => {
      document.removeEventListener("visibilitychange", visibilite);
      CAPACITES.arreter(); etat.enonceCourant = "";
      zone.replaceChildren(); zone.hidden = true;
    },
    snapshot: () => active() ? JSON.parse(JSON.stringify(reponse)) : null,
  };
  rendre();
}

function rendreFicheMethode() {
  const precedent = refs.statsResume.parentElement.querySelector(".fiche-methode");
  if (precedent) precedent.remove();
  const sequence = (etat.session?.items || []).find(
    (item) => item.type === "pqrst-mise-en-oeuvre"
  );
  const lignes = sequence?.contenu?.fiche_methode;
  if (!Array.isArray(lignes) || !lignes.length) return;
  const bloc = creerElement("details", { classe: "fiche-methode" },
    creerElement("summary", { texte: "Méthode PQRST — à garder" }),
    creerElement("ol", {}, ...lignes.map((ligne) => creerElement("li", { texte: ligne })))
  );
  refs.statsResume.parentElement.append(bloc);
}

function rendreFeedbackSequence(resultat) {
  const detail = resultat.sequence || {};
  if (detail.observation) {
    rendreObservationPqrst(detail);
    return;
  }
  const lignes = [
    { titre: "1. Parcours", correcte: detail["1"]?.correcte,
      texte: detail["1"]?.correcte ? "sujet du texte trouvé" : `attendu : ${detail["1"]?.attendue ?? "—"}` },
    { titre: "2. Ta question", correcte: true, nonNotee: true,
      texte: `${etat.sequence?.["2"]?.trim() ? `« ${etat.sequence["2"].trim()} »` : "Aucune question saisie"} — sans score. Autre question possible : « ${detail["2"]?.modele ?? ""} »` },
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

function rendreObservationPqrst(detail) {
  nettoyerSequence();
  CAPACITES.arreter();
  etat.enonceCourant = "";
  refs.zoneSequence.replaceChildren(); refs.zoneSequence.hidden = true;
  refs.ligneAudio.hidden = true;
  const mots = etat.session?.items[etat.indexItem]?.contenu?.interface_pqrst || {};
  const texte = (cle, valeurs = {}) => String(mots[cle] || "").replace(
    /\{(\w+)\}/g, (_, nom) => String(valeurs[nom] ?? ""));
  const observation = detail.observation;
  refs.carteFeedback.replaceChildren(); refs.carteFeedback.className = "carte-feedback";
  const ligne = contenu => refs.carteFeedback.append(creerElement("p", { texte: contenu }));
  ligne(texte("resultat")); ligne(texte("condition"));
  if (observation.reprise_apres_correction) ligne(texte("reprise_corrigee"));
  ligne(`${texte("P")} : ${observation.statuts["1"] === "absence_declaree"
    ? texte("absence") : texte(detail["1"]?.correcte ? "correcte" : "incorrecte")}`);
  ligne(texte("retour_question", { question: observation.question || texte("absence") }));
  for (const [cle, essais] of Object.entries(observation.tentatives)) {
    essais.forEach((essai, rang) => {
      const titre = cle === "4" ? (rang ? "reformulation_aidee" : "reformulation_initiale")
        : rang ? "test_aide" : "test_initial";
      const etatCorrection = essai.correction.etat;
      const statut = etatCorrection === "absence_declaree" ? "absence"
        : etatCorrection === "exacte" ? "correcte" : etatCorrection;
      ligne(`${texte(titre, { numero: Number(cle.slice(2)) + 1 })} : ${texte(statut)} · ${texte(essai.condition)}`);
      if (essai.reponse !== null) ligne(texte("production", { reponse: essai.reponse }));
      if (cle === "4" && essai.reponse !== null) ligne(texte("idees_reconnues", {
        nombre: essai.correction.trouvees.length,
        total: essai.correction.trouvees.length + essai.correction.manquantes.length + essai.correction.contredites.length,
      }));
    });
  }
  ligne(texte("modele", { modele: detail["4"]?.modele || "" }));
  (detail["5"]?.questions || []).forEach((bonne, i) => ligne(`${i + 1}. ${bonne}`));
  const interruptions = Object.values(observation.interruptions).reduce((a, b) => a + b, 0);
  if (interruptions) ligne(texte("interruptions", { nombre: interruptions }));
}
