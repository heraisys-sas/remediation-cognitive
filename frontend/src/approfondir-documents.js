"use strict";

/** Dialogue facultatif, après correction, sans aucune soumission au moteur. */
function creerApprofondissementDocuments(itemId, reponses) {
  const zone = document.createElement("details");
  const ouverture = document.createElement("summary");
  ouverture.textContent = "Approfondir";
  const explication = document.createElement("p");
  explication.textContent = "Explique ce qui appuie ta conclusion ou ce que tu vérifierais avant d’agir. Deux relances locales au maximum, sans changer ton résultat.";
  const historique = document.createElement("div");
  const label = document.createElement("label");
  label.textContent = "Ton raisonnement";
  const champ = document.createElement("textarea");
  champ.className = "sequence-champ";
  champ.maxLength = 800;
  champ.rows = 3;
  label.append(champ);
  const envoyer = document.createElement("button");
  envoyer.type = "button";
  envoyer.className = "bouton-secondaire";
  envoyer.textContent = "Échanger sur ma réponse";
  const statut = document.createElement("p");
  statut.setAttribute("role", "status");
  const echanges = [];
  const reponsesInitiales = {...reponses};
  let attente = false;
  function maj() { envoyer.disabled = attente || !champ.value.trim() || echanges.length >= 2; }
  champ.addEventListener("input", maj);
  envoyer.addEventListener("click", async () => {
    if (attente || echanges.length >= 2 || !champ.value.trim()) return;
    const justification = champ.value.trim();
    attente = true;
    champ.disabled = true;
    maj();
    statut.textContent = "Préparation de la relance sur ce Mac…";
    const controleur = new AbortController();
    const delai = setTimeout(() => controleur.abort(), 30000);
    try {
      const response = await fetch("/api/capacites/accompagnement-documents", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({item_id: itemId, reponses: reponsesInitiales, justification, echanges}),
        signal: controleur.signal,
      });
      if (!response.ok) throw new Error("indisponible");
      const data = await response.json();
      if (!zone.isConnected) return;
      if (!data.disponible || !data.relance) {
        statut.textContent = "L’échange local n’est pas disponible pour le moment. Tu peux poursuivre l’exercice.";
        return;
      }
      echanges.push({justification, relance: data.relance});
      for (const texte of [`Ta réflexion : ${justification}`, data.relance]) {
        const ligne = document.createElement("p");
        ligne.textContent = texte;
        historique.append(ligne);
      }
      champ.value = "";
      envoyer.textContent = "Demander une dernière relance";
      statut.textContent = data.relance;
      if (echanges.length >= 2) {
        label.hidden = true;
        envoyer.hidden = true;
        statut.textContent = "Tu peux garder cette dernière question pour réfléchir, puis poursuivre l’exercice.";
      } else champ.focus();
    } catch (_) {
      if (zone.isConnected) statut.textContent = "La relance n’est pas disponible pour le moment. Tu peux réessayer ou poursuivre.";
    } finally {
      clearTimeout(delai);
      attente = false;
      champ.disabled = false;
      maj();
    }
  });
  zone.append(ouverture, explication, historique, label, envoyer, statut);
  maj();
  return zone;
}
