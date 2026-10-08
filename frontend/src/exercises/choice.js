"use strict";

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
