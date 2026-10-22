"use strict";

// Tableau externe : chaque décision reste explicite et réversible.
function rendreLogigramme(item) {
  const contenu = item.contenu;
  const [repere, ...categories] = contenu.categories;
  const zone = refs.zoneSequence;
  zone.hidden = false;
  refs.formulaire.hidden = true;
  refs.zoneChoix.hidden = true;
  const indices = creerElement("ol", { classe: "logigramme-indices" });
  for (const contrainte of contenu.contraintes) indices.append(creerElement("li", { texte: contrainte.texte }));
  const table = creerElement("table", { classe: "logigramme-table" });
  const entete = creerElement("tr", {}, creerElement("th", { texte: repere.label, attributs: { scope: "col" } }),
    ...categories.map(c => creerElement("th", { texte: c.label, attributs: { scope: "col" } })));
  table.append(creerElement("thead", {}, entete));
  const corps = creerElement("tbody");
  const reponses = {};
  const champs = [];
  const statut = creerElement("p", { attributs: { role: "status", "aria-live": "polite" } });
  function signalerDoublons() {
    const doublons = categories.filter(c => {
      const valeurs = Object.values(reponses).map(r => r[c.id]).filter(Boolean);
      return new Set(valeurs).size !== valeurs.length;
    });
    statut.textContent = doublons.length ? `À vérifier : une même valeur est choisie plusieurs fois (${doublons.map(c => c.label).join(", ")}).` : "";
  }
  const valider = creerElement("button", { texte: "Vérifier mes liens", classe: "bouton bouton-primaire", attributs: { type: "button", disabled: "" } });
  for (const valeur of repere.valeurs) {
    reponses[valeur] = {};
    const ligne = creerElement("tr", {}, creerElement("th", { texte: valeur, attributs: { scope: "row" } }));
    for (const categorie of categories) {
      const choix = creerElement("select", { classe: "champ", attributs: { "aria-label": `${valeur} — ${categorie.label}` } });
      for (const option of ["", ...categorie.valeurs]) choix.append(creerElement("option", {
        texte: option || "À déterminer", attributs: { value: option }
      }));
      choix.addEventListener("change", () => {
        reponses[valeur][categorie.id] = choix.value;
        signalerDoublons();
        valider.disabled = etat.repondu || etat.actionEnCours || champs.some(c => !c.value);
      });
      champs.push(choix);
      ligne.append(creerElement("td", {}, choix));
    }
    corps.append(ligne);
  }
  table.append(corps);
  valider.addEventListener("click", async () => {
    if (etat.actionEnCours || etat.repondu) return;
    valider.disabled = true;
    try { await soumettreValeur(reponses, etat.indicesReveles); }
    finally {
      for (const champ of champs) champ.disabled = etat.repondu;
      valider.disabled = etat.actionEnCours || etat.repondu || champs.some(c => !c.value);
    }
  });
  zone.replaceChildren(indices, table, statut, valider);
  if (Array.isArray(contenu.indices) && contenu.indices.length) rendreIndices(item);
  champs[0]?.focus();
}

function rendreFeedbackLogigramme(resultat) {
  if (resultat.essai_supplementaire) { rendreFeedback({ ...resultat, attendue: null }); return; }
  let associations;
  try { associations = typeof resultat.attendue === "string" ? JSON.parse(resultat.attendue) : resultat.attendue; }
  catch { associations = null; }
  const texte = associations && typeof associations === "object"
    ? Object.entries(associations).map(([repere, liens]) => `${repere} : ${Object.values(liens).join(" · ")}`).join(" ; ")
    : resultat.attendue;
  rendreFeedback({ ...resultat, attendue: texte });
}
