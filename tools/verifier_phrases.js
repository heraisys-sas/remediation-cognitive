#!/usr/bin/env node
/**
 * Vérifie que l'interface sait rendre **chaque phrase** du contenu « déduction ».
 *
 * Le formateur de phrases vit dans `frontend/src/app.js`. Plutôt que de le recopier
 * (on testerait une copie, pas le vrai code), ce contrôle extrait les fonctions pures
 * du fichier et les exécute sur tout le contenu : une phrase vide, un « undefined »
 * ou un prédicat sans verbe font échouer la vérification.
 *
 * Usage : node tools/verifier_phrases.js
 */

const fs = require("fs");
const path = require("path");

const racine = path.resolve(__dirname, "..");
const source = fs.readFileSync(path.join(racine, "frontend", "src", "app.js"), "utf8");

/** Extrait un bloc équilibré à partir d'un index d'ouverture ( { ou [ ). */
function blocEquilibre(texte, depart) {
  let profondeur = 0;
  let chaine = null;
  for (let i = depart; i < texte.length; i += 1) {
    const c = texte[i];
    if (chaine) {
      if (c === "\\") i += 1;
      else if (c === chaine) chaine = null;
      continue;
    }
    if (c === '"' || c === "'" || c === "`") { chaine = c; continue; }
    if (c === "{" || c === "[") profondeur += 1;
    if (c === "}" || c === "]") {
      profondeur -= 1;
      if (profondeur === 0) return texte.slice(depart, i + 1);
    }
  }
  throw new Error("bloc non équilibré");
}

/** Extrait `const nom = ...` ou `function nom(...) {...}`. */
function extraire(nom) {
  const motif = new RegExp(`(?:const|function)\\s+${nom}\\b`);
  const trouve = source.match(motif);
  if (!trouve) throw new Error(`« ${nom} » introuvable dans app.js`);
  const debut = trouve.index;
  const ouverture = source.indexOf(source.includes("function " + nom) ? "{" : "=", debut);
  const depuis = source[ouverture] === "{" || source[ouverture] === "[" || source[ouverture] === "="
    ? ouverture : ouverture;
  if (source[depuis] === "=") {
    const suite = source.slice(depuis + 1).search(/[[{]/) + depuis + 1;
    return source.slice(debut, depuis) + source.slice(depuis, suite) + blocEquilibre(source, suite);
  }
  return source.slice(debut, blocEquilibre(source, depuis).length + depuis);
}

const morceaux = [
  "GLYPHES", "TEINTES", "LIBELLES_FIGURES",
  "NOMS_CASES_3", "NOMS_LIGNES_3", "NOMS_COLONNES_3",
  "NOMS_CASES_4", "NOMS_LIGNES_4", "NOMS_COLONNES_4",
].map(extraire)
  .concat([
    source.slice(source.indexOf("const libelleFigure"),
                 source.indexOf("\n", source.indexOf("const libelleFigure"))),
    extraire("nomsPour"), extraire("predicatAtome"), extraire("relationAtome"),
    extraire("phraseAtome"), extraire("sansEst"), extraire("libelleCategorie"),
    extraire("formaterIndiceCollectif"), extraire("formaterEnonce"),
  ]);

const fabrique = new Function(`${morceaux.join("\n")}\nreturn { formaterEnonce };`);
const { formaterEnonce } = fabrique();

//: Phrases dorées : rendu EXACT attendu pour chaque type négatif (les huit types
//: ajoutés avec les négations de voisinage et les relatives négatives). Un rendu
//: vide, un « undefined » ou une formulation qui dit l'inverse échoue ici — même
//: quand le contenu du dépôt ne contient pas encore ce type.
const DOREES = [
  [{type:"pas-colonne",figure:"carre",couleur:"bleu",colonne:0,
    et:[{type:"voisin-dessus",figure2:"cercle",couleur2:"rouge"}]},
   "Le carré bleu n'est pas dans la colonne de gauche et est juste au-dessus du cercle rouge."],
  [{type:"voisin-dessus",figure:"carre",couleur:"bleu",figure2:"cercle",couleur2:"rouge",
    et:[{type:"voisin-gauche",figure:"cercle",couleur:"rouge",figure2:"triangle",couleur2:"vert"}]},
   "Le carré bleu est juste au-dessus du cercle rouge, qui est juste à gauche du triangle vert."],
  [{ type: "compte-categorie", categorie: { figure: "carre" }, zone: "colonne", numero: 3, nombre: 0 },
   "La colonne 4 ne contient aucun pion de forme carré.", 4],
  [{ type: "entre", figure: "losange", couleur: "jaune", extremites: [{ couleur: "bleu" }, { couleur: "bleu" }], axe: "ligne" },
   "Le losange jaune est strictement entre deux pions de couleur bleu, sur une même ligne, sans être nécessairement voisins ni à égale distance.", 4],
  [{ type: "compte-categorie", categorie: { couleur: "rouge" }, zone: "colonne", numero: 2, nombre: 0 },
   "La colonne de droite ne contient aucun pion de couleur rouge."],
  [{ type: "compte-categorie", categorie: { figure: "losange" }, zone: "ligne", numero: "chaque", nombre: 1 },
   "Chaque ligne contient exactement 1 pion de forme losange."],
  [{ type: "compte-categorie", categorie: { couleur: "vert" }, zone: "ligne", numero: 0, nombre: 2 },
   "La ligne du haut contient exactement 2 pions de couleur vert."],
  [{ type: "diversite", attribut: "figure", zone: "ligne", numero: "chaque" },
   "Chaque ligne contient exactement un pion de chaque forme."],
  [{ type: "diversite", attribut: "couleur", zone: "colonne", numero: 1 },
   "La colonne du centre contient exactement un pion de chaque couleur."],
  [{ type: "entre", figure: "carre", couleur: "rouge", extremites: [{ figure: "cercle" }, { figure: "cercle" }], axe: "diagonale" },
   "Le carré rouge est strictement entre deux pions de forme cercle, sur une même diagonale, sans être nécessairement voisins ni à égale distance."],
  [{ type: "entre", figure: "carre", couleur: "rouge", extremites: [{ couleur: "vert" }, { figure: "triangle", couleur: "bleu" }], axe: "colonne" },
   "Le carré rouge est strictement entre un pion de couleur vert et un triangle bleu, dans une même colonne, sans être nécessairement voisins ni à égale distance."],
  [{ type: "pas-voisin-gauche", figure: "carre", couleur: "bleu", figure2: "cercle", couleur2: "rouge" },
   "Le carré bleu n'est pas juste à gauche du cercle rouge."],
  [{ type: "pas-voisin-droite", figure: "carre", couleur: "bleu", figure2: "cercle", couleur2: "rouge" },
   "Le carré bleu n'est pas juste à droite du cercle rouge."],
  [{ type: "pas-voisin-dessus", figure: "carre", couleur: "bleu", figure2: "cercle", couleur2: "rouge" },
   "Le carré bleu n'est pas juste au-dessus du cercle rouge."],
  [{ type: "pas-voisin-dessous", figure: "carre", couleur: "bleu", figure2: "cercle", couleur2: "rouge" },
   "Le carré bleu n'est pas juste en dessous du cercle rouge."],
  [{ type: "pas-a-droite-de", figure: "triangle", couleur: "vert", figure2: "losange", couleur2: "jaune" },
   "Le triangle vert n'est pas plus à droite que le losange jaune."],
  [{ type: "pas-a-gauche-de", figure: "triangle", couleur: "vert", figure2: "losange", couleur2: "jaune" },
   "Le triangle vert n'est pas plus à gauche que le losange jaune."],
  [{ type: "pas-au-dessus-de", figure: "triangle", couleur: "vert", figure2: "losange", couleur2: "jaune" },
   "Le triangle vert n'est pas plus haut que le losange jaune."],
  [{ type: "pas-en-dessous-de", figure: "triangle", couleur: "vert", figure2: "losange", couleur2: "jaune" },
   "Le triangle vert n'est pas plus bas que le losange jaune."],
];
for (const [atome, attendu, taille = 3] of DOREES) {
  const rendu = formaterEnonce(atome, taille);
  if (rendu !== attendu) {
    console.error(`✗ phrase dorée « ${atome.type} » : attendu « ${attendu} », rendu « ${rendu} »`);
    process.exit(1);
  }
  if (/undefined/.test(rendu) || /\bet\s*\./.test(rendu)) {
    console.error(`✗ phrase dorée « ${atome.type} » incomplète : « ${rendu} »`);
    process.exit(1);
  }
}
console.log(`✓ ${DOREES.length} phrases dorées (relations et indices collectifs) rendues à l'identique`);

//: Expressions attendues pour chaque type de relation : une inversion entre le nom de
//: l'indice et la phrase affichée (« voisin-dessus » écrit « en dessous ») rendait la
//: grille insoluble. Ces garde-fous verrouillent la convention côté interface.
const ATTENDUS = {
  "voisin-gauche": { contient: ["juste à gauche"], exclut: ["droite", "dessus", "dessous"] },
  "voisin-droite": { contient: ["juste à droite"], exclut: ["gauche", "dessus", "dessous"] },
  "voisin-dessus": { contient: ["juste au-dessus"], exclut: ["dessous", "gauche", "droite"] },
  "voisin-dessous": { contient: ["juste en dessous"], exclut: ["au-dessus", "gauche", "droite"] },
  "comparaison": { contient: ["même ligne", "à sa gauche"], exclut: ["plus bas"] },
  "a-droite-de": { contient: ["plus à droite"], exclut: ["plus à gauche"] },
  "a-gauche-de": { contient: ["plus à gauche"], exclut: ["plus à droite"] },
  "au-dessus-de": { contient: ["plus haut"], exclut: ["plus bas"] },
  "en-dessous-de": { contient: ["plus bas"], exclut: ["plus haut"] },
  "autre-ligne": { contient: ["n'est pas sur la même ligne"], exclut: [] },
  "autre-colonne": { contient: ["n'est pas dans la même colonne"], exclut: [] },
  "pas-ligne": { contient: ["n'est pas sur la ligne"], exclut: [] },
  "pas-colonne": { contient: ["n'est pas dans la colonne"], exclut: [] },
  "pas-voisin-gauche": { contient: ["n'est pas juste à gauche"], exclut: ["juste à droite", "au-dessus", "en dessous"] },
  "pas-voisin-droite": { contient: ["n'est pas juste à droite"], exclut: ["juste à gauche", "au-dessus", "en dessous"] },
  "pas-voisin-dessus": { contient: ["n'est pas juste au-dessus"], exclut: ["en dessous", "juste à gauche", "juste à droite"] },
  "pas-voisin-dessous": { contient: ["n'est pas juste en dessous"], exclut: ["au-dessus", "juste à gauche", "juste à droite"] },
  "pas-a-droite-de": { contient: ["n'est pas plus à droite"], exclut: ["plus à gauche", "plus haut", "plus bas"] },
  "pas-a-gauche-de": { contient: ["n'est pas plus à gauche"], exclut: ["plus à droite", "plus haut", "plus bas"] },
  "pas-au-dessus-de": { contient: ["n'est pas plus haut"], exclut: ["plus bas", "plus à droite", "plus à gauche"] },
  "pas-en-dessous-de": { contient: ["n'est pas plus bas"], exclut: ["plus haut", "plus à droite", "plus à gauche"] },
  "pas-coin": { contient: ["n'est pas dans un coin"], exclut: [] },
  "coin": { contient: ["est dans un coin"], exclut: ["n'est pas"] },
  "diagonale": { contient: ["diagonale descendante"], exclut: ["n'est pas"] },
  "diagonale-inverse": { contient: ["diagonale montante"], exclut: ["descendante", "n'est pas"] },
  "pas-diagonale": { contient: ["n'est pas sur la diagonale descendante"], exclut: [] },
  "pas-diagonale-inverse": { contient: ["n'est pas sur la diagonale montante"], exclut: ["descendante"] },
  "voisin-diagonale": { contient: ["en diagonale"], exclut: ["juste à gauche", "juste au-dessus", "juste en dessous"] },
  "oppose": { contient: ["à l'opposé"], exclut: ["juste"] },
  "pas-bord": { contient: ["n'est pas sur le bord"], exclut: [] },
  "ni-ni": { contient: ["n'est ni"], exclut: [] },
};

const dossier = path.join(racine, "content", "entrainement", "deduction", "paliers");
let phrases = 0;
let atomes = 0;
const anomalies = [];

for (const fichier of fs.readdirSync(dossier).filter((f) => f.endsWith(".json"))) {
  for (const item of JSON.parse(fs.readFileSync(path.join(dossier, fichier), "utf8"))) {
    const n = item.contenu.figures.length;
    for (const [rang, phrase] of item.contenu.enonces.entries()) {
      const rendu = formaterEnonce(phrase, n);
      phrases += 1;
      const fautes = [];
      if (/undefined/.test(rendu)) fautes.push("undefined");
      if (/\bet\s*\./.test(rendu) || /,\s*\./.test(rendu)) fautes.push("prédicat vide");
      if (!/\best\b|\bn'est\b|\bcontient\b|\btouche\b/.test(rendu)) fautes.push("aucun verbe");
      if (fautes.length) anomalies.push(`${item.id} phrase ${rang + 1} — ${fautes.join(", ")} → « ${rendu} »`);

      // Chaque information, rendue seule, doit dire ce que son nom annonce.
      for (const atome of [phrase, ...(phrase.et || [])]) {
        const attendu = ATTENDUS[atome.type];
        if (!attendu) continue;
        atomes += 1;
        const seul = formaterEnonce({ ...atome, figure: atome.figure || phrase.figure,
                                      couleur: atome.couleur || phrase.couleur, et: [] }, n);
        for (const marque of attendu.contient) {
          if (!seul.includes(marque)) {
            anomalies.push(`${item.id} : « ${atome.type} » devrait dire « ${marque} » → « ${seul} »`);
          }
        }
        for (const marque of attendu.exclut) {
          if (seul.includes(marque) && !attendu.contient.some((m) => m.includes(marque))) {
            anomalies.push(`${item.id} : « ${atome.type} » ne doit pas dire « ${marque} » → « ${seul} »`);
          }
        }
      }
    }
  }
}

if (anomalies.length) {
  console.error(`✗ ${anomalies.length} anomalie(s) de rendu :`);
  for (const ligne of anomalies.slice(0, 20)) console.error("   " + ligne);
  process.exit(1);
}
console.log(`✓ ${phrases} phrases et ${atomes} informations rendues sans anomalie`);
