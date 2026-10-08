"use strict";

function lireEtapeActualisation(item, texte, premiereEtape = false) {
  CAPACITES.arreter();
  const consigne = premiereEtape ? String(item.contenu.consigne || "").trim() : "";
  const dejaLue = etat.consignesMemoVues.has(consigne);
  if (consigne) etat.consignesMemoVues.add(consigne);
  etat.enonceCourant = [consigne, texte].filter(Boolean).join(" ");
  refs.ligneAudio.hidden = !CAPACITES.syntheseDisponible();
  lireSiLectureAuto([!dejaLue ? consigne : "", texte].filter(Boolean).join(" "));
}

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
        // Champs sur une seule ligne : Entrée équivaut au bouton Valider.
        saisie.addEventListener("keydown", (evenement) => {
          if (evenement.key !== "Enter" || evenement.isComposing || evenement.repeat) return;
          evenement.preventDefault();
          if (!valider.disabled) valider.click();
        });
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
        lireEtapeActualisation(item, "Écris la consigne finale. Les éléments non modifiés restent valables.");
        formulaire(); return;
      }
      zone.append(creerElement("p", { classe: "ligne-discrete", texte: `${etape.titre} — ${index + 1}/${c.etapes.length}` }),
        creerElement("p", { classe: "document-source", texte: etape.texte }),
        bouton(index === c.etapes.length - 1 ? "Restituer la consigne" : "Message suivant", () => { index++; montrer(); }));
      lireEtapeActualisation(item, `${etape.titre}. ${etape.texte}`, index === 0);
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
