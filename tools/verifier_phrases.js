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
    extraire("phraseAtome"), extraire("sansEst"), extraire("formaterEnonce"),
  ]);

const fabrique = new Function(`${morceaux.join("\n")}\nreturn { formaterEnonce };`);
const { formaterEnonce } = fabrique();

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
  "pas-coin": { contient: ["n'est pas dans un coin"], exclut: [] },
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
      if (!/\best\b|\bn'est\b/.test(rendu)) fautes.push("aucun verbe");
      if (fautes.length) anomalies.push(`${item.id} phrase ${rang + 1} — ${fautes.join(", ")} → « ${rendu} »`);

      // Chaque information, rendue seule, doit dire ce que son nom annonce.
      for (const atome of [phrase, ...(phrase.et || [])]) {
        const attendu = ATTENDUS[atome.type];
        if (!attendu) continue;
        atomes += 1;
        const seul = formaterEnonce({ ...atome, figure: atome.figure || phrase.figure,
                                      couleur: atome.couleur || phrase.couleur }, n);
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
