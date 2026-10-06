"use strict";

/** Retour facultatif après correction : n'intervient jamais dans le score. */
function creerAccompagnementPqrst(texte, reformulation) {
  const zone = document.createElement("section");
  const titre = document.createElement("h3");
  titre.textContent = "Revenir sur ma méthode";
  const explication = document.createElement("p");
  explication.textContent = "Accompagnement local facultatif — deux relances maximum, sans changer ton résultat.";
  const label = document.createElement("label");
  label.textContent = "Ma reformulation, que je peux retravailler";
  const champ = document.createElement("textarea");
  champ.className = "sequence-champ";
  champ.value = reformulation || "";
  champ.maxLength = 2000;
  label.append(champ);
  const bouton = document.createElement("button");
  bouton.type = "button";
  bouton.className = "bouton-secondaire";
  bouton.textContent = "Demander une relance";
  const retour = document.createElement("p");
  retour.setAttribute("role", "status");
  let nombre = 0;
  const categories = [];
  let attente = false;
  const maj = () => { bouton.disabled = attente || nombre >= 2 || !champ.value.trim(); };
  champ.addEventListener("input", maj);
  bouton.addEventListener("click", async () => {
    if (attente || nombre >= 2 || !champ.value.trim()) return;
    attente = true;
    maj();
    retour.textContent = "Préparation de la relance sur ce Mac…";
    const controleur = new AbortController();
    const minuterie = setTimeout(() => controleur.abort(), 30000);
    try {
      const reponse = await fetch("/api/capacites/accompagnement", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({texte, reformulation: champ.value.trim(), categories_deja_vues: categories}),
        signal: controleur.signal,
      });
      if (!reponse.ok) throw new Error("indisponible");
      const resultat = await reponse.json();
      if (!zone.isConnected) return;
      if (!resultat.disponible || !resultat.relance) {
        retour.textContent = "L’accompagnement Apple local n’est pas disponible. Tu peux poursuivre normalement.";
      } else {
        nombre += 1;
        if (resultat.categorie) categories.push(resultat.categorie);
        retour.textContent = resultat.relance;
        bouton.textContent = nombre < 2 ? "Demander une dernière relance" : "Deux relances effectuées";
      }
    } catch (_) {
      if (zone.isConnected) retour.textContent = "La relance n’est pas disponible pour le moment. Tu peux poursuivre normalement.";
    } finally {
      clearTimeout(minuterie);
      attente = false;
      maj();
    }
  });
  zone.append(titre, explication, label, bouton, retour);
  maj();
  return zone;
}
