"use strict";

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
    classe: "bouton bouton-primaire bouton-large", texte: "Valider la séquence",
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

function rendreFeedbackSequence(resultat) {
  const detail = resultat.sequence || {};
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
