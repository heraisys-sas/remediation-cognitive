"use strict";

// Correspondances documentaires, sans profil clinique ni modification du moteur.
const AccueilDifficultes = (() => {
  const cle = "orthogone.accueil.difficultes.v1";
  const categories = [
    { id: "attention", nom: "Concentration et attention", description: "Garder le fil et repérer les informations utiles.", cartes: ["reperer-essentiel", "comparer-documents", "garder-cap", "methodes"] },
    { id: "immediat", nom: "Mémoire immédiate", description: "Retenir une information pendant quelques secondes.", cartes: ["memoires-immediates", "memoire", "rappel-series", "series-entendues"] },
    { id: "manipulation", nom: "Manipuler des informations en tête", description: "Garder une information tout en la transformant ou en la mettant à jour.", cartes: ["actualiser-consigne", "memoire", "nback"] },
    { id: "rappel", nom: "Retrouver une information mémorisée", description: "Se rappeler une série, un message ou son contexte.", cartes: ["rappel-series", "series-entendues", "evocation", "methodes", "strategies"] },
    { id: "mots", nom: "Trouver ses mots", description: "Retrouver un mot et utiliser des indices pour y parvenir.", cartes: ["evocation"] },
    { id: "organisation", nom: "S’organiser et penser à agir", description: "Préparer ses étapes et utiliser des rappels.", cartes: ["quotidien", "methodes", "strategies"] },
    { id: "adaptation", nom: "S’adapter et vérifier ses actions", description: "Tenir compte d’un changement et contrôler ce qui a été fait.", cartes: ["garder-cap", "actualiser-consigne", "comparer-documents", "strategies"] },
    { id: "raisonnement", nom: "Raisonner et calculer", description: "Croiser des informations ou résoudre un calcul pratique.", cartes: ["deduction", "calcul-mental"] },
    { id: "extra", nom: "Autres apprentissages", description: "À part : vocabulaire anglais et commandes Python.", cartes: ["anglais", "python"] },
  ];
  let selection = lire();
  let groupes = [], cartes = [], empreinte = "", initialise = false;
  const listes = ["liste-themes", "liste-themes-evaluation", "liste-themes-extra"];
  const element = id => document.getElementById(id);

  function lire() {
    try {
      const brut = window.localStorage.getItem(cle);
      if (brut === null) return null;
      const valeur = JSON.parse(brut);
      return Array.isArray(valeur) && valeur.every(id => typeof id === "string") ? valeur : null;
    } catch { return null; }
  }
  function idsActifs() { return selection === null ? groupes.map(g => g.id) : selection; }
  function groupesPour(inventaire) {
    const ids = new Set(inventaire.map(c => c.id));
    const connus = new Set(categories.flatMap(g => g.cartes));
    const autres = [...ids].filter(id => !connus.has(id));
    return [...categories, ...(autres.length ? [{ id: "autres", nom: "Autres activités disponibles", description: "Activités du catalogue restant à classer.", cartes: autres }] : [])]
      .map(g => ({ ...g, cartes: g.cartes.filter(id => ids.has(id)) })).filter(g => g.cartes.length);
  }
  function visibles(inventaire, choix, definitions) {
    if (choix === null) return inventaire.map(c => c.id);
    const ids = new Set(definitions.filter(g => choix.includes(g.id)).flatMap(g => g.cartes));
    return inventaire.filter(c => ids.has(c.id)).map(c => c.id);
  }
  function enregistrer(choix) {
    try { window.localStorage.setItem(cle, JSON.stringify(choix)); }
    catch {
      element("erreur-difficultes").textContent = "Le choix n’a pas pu être enregistré. Le dernier choix conservé reste appliqué. Réessaie après avoir autorisé le stockage local.";
      element("erreur-difficultes").hidden = false;
      synchroniser(); return;
    }
    selection = choix;
    element("erreur-difficultes").hidden = true;
    synchroniser(); filtrer();
  }
  function synchroniser() {
    for (const input of element("choix-difficultes").querySelectorAll("input")) input.checked = idsActifs().includes(input.value);
  }
  function filtrer() {
    const ids = new Set(visibles(cartes, selection, groupes));
    for (const carte of cartes) carte.node.hidden = !ids.has(carte.id);
    for (const [section, liste] of [["section-evaluation", "liste-themes-evaluation"], ["section-extra", "liste-themes-extra"]]) {
      const zone = element(liste), panneau = element(section);
      if (zone && panneau) panneau.hidden = ![...zone.children].some(c => !c.hidden);
    }
    element("accueil-filtre-vide").hidden = !cartes.length || ids.size > 0;
  }
  function rendreChoix() {
    const zone = element("choix-difficultes");
    const legend = document.createElement("legend"); legend.textContent = "Difficultés et activités associées";
    zone.replaceChildren(legend);
    for (const groupe of groupes) {
      const label = document.createElement("label"); label.className = "choix-difficulte";
      const input = document.createElement("input"); input.type = "checkbox"; input.value = groupe.id;
      input.id = `difficulte-${groupe.id}`;
      const texte = document.createElement("span"), titre = document.createElement("strong"); titre.textContent = groupe.nom;
      const description = document.createElement("span"); description.textContent = groupe.description; description.id = `${input.id}-description`;
      const activites = document.createElement("span"); activites.className = "ligne-discrete"; activites.id = `${input.id}-cartes`;
      activites.textContent = "Cartes : " + cartes.filter(c => groupe.cartes.includes(c.id)).map(c => c.nom).join(" ; ") + ".";
      input.setAttribute("aria-describedby", `${description.id} ${activites.id}`);
      input.setAttribute("aria-labelledby", `${input.id}-titre`); titre.id = `${input.id}-titre`;
      input.addEventListener("change", () => {
        const nouveaux = new Set(idsActifs());
        if (input.checked) nouveaux.add(groupe.id); else nouveaux.delete(groupe.id);
        enregistrer([...nouveaux]);
      });
      texte.append(titre, description, activites); label.append(input, texte); zone.append(label);
    }
    const actions = document.createElement("div"); actions.className = "actions-suite";
    for (const [texte, choix] of [["Tout afficher", null], ["Tout masquer", []]]) {
      const bouton = document.createElement("button"); bouton.type = "button"; bouton.className = "bouton bouton-secondaire"; bouton.textContent = texte;
      bouton.addEventListener("click", () => enregistrer(choix === null ? groupes.map(g => g.id) : [])); actions.append(bouton);
    }
    zone.append(actions); synchroniser();
  }
  function actualiser() {
    if (!element("choix-difficultes")) return;
    cartes = listes.flatMap(id => [...(element(id)?.children || [])]).filter(n => n.dataset?.activite)
      .map(node => ({ id: node.dataset.activite, nom: node.querySelector("h3")?.textContent || node.dataset.activite, node }));
    groupes = groupesPour(cartes);
    const signature = JSON.stringify(cartes.map(c => [c.id, c.nom]));
    if (signature !== empreinte) { empreinte = signature; rendreChoix(); }
    filtrer();
  }
  function initialiser() {
    if (initialise || !element("choix-difficultes")) return;
    initialise = true;
    const attente = document.createElement("p"); attente.textContent = "Les choix seront disponibles après le chargement des activités.";
    element("choix-difficultes").append(attente);
    element("ouvrir-choix-difficultes").addEventListener("click", () => {
      element("reglages-interface").open = true; element("reglages-difficultes").open = true;
      element("reglages-difficultes").querySelector("summary").focus();
    });
  }
  return { initialiser, actualiser, groupesPour, visibles };
})();
