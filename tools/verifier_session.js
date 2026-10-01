#!/usr/bin/env node
/**
 * Vérifie que le frontend transmet le PALIER choisi au serveur — et garde le mode auto.
 *
 * Le défaut corrigé : `demarrerSession` recevait le palier mais POSTait `…/sessions`
 * sans corps, si bien qu'un essai « palier 2 » était servi au palier courant. Ce
 * contrôle n'est pas un test d'API : il exécute le VRAI `demarrerSession` + `apiFetch`
 * de `frontend/src/app.js` sur un `fetch` simulé, et vérifie la requête réellement
 * construite (méthode, URL, corps, en-têtes) pour un palier choisi et pour le mode auto.
 * Il couvre aussi la dérogation « dépasser la limite de séances » (ADR-021) :
 * `sans_limite_sessions` part dans le corps quand elle est active — seule ou avec un
 * palier — et survit au réessai réseau.
 *
 * Usage : node tools/verifier_session.js
 */

const fs = require("fs");
const path = require("path");

const racine = path.resolve(__dirname, "..");
const source = fs.readFileSync(path.join(racine, "frontend", "src", "app.js"), "utf8");

/** Extrait un bloc équilibré à partir d'un index d'ouverture ( { ou [ ).
 *
 *  Conscient des chaînes et des commentaires (ligne « double slash », bloc) :
 *  un commentaire français contient des apostrophes (« n'est », « l'aide »)
 *  qui ne doivent jamais être prises pour des chaînes — sinon le bloc déborde.
 */
function blocEquilibre(texte, depart) {
  let profondeur = 0;
  let chaine = null;
  let commentaire = null;
  for (let i = depart; i < texte.length; i += 1) {
    const c = texte[i];
    const suivant = texte[i + 1];
    if (commentaire === "ligne") {
      if (c === "\n") commentaire = null;
      continue;
    }
    if (commentaire === "bloc") {
      if (c === "*" && suivant === "/") { commentaire = null; i += 1; }
      continue;
    }
    if (chaine) {
      if (c === "\\") i += 1;
      else if (c === chaine) chaine = null;
      continue;
    }
    if (c === "/" && suivant === "/") { commentaire = "ligne"; i += 1; continue; }
    if (c === "/" && suivant === "*") { commentaire = "bloc"; i += 1; continue; }
    if (c === '"' || c === "'" || c === "`") { chaine = c; continue; }
    if (c === "{" || c === "[") profondeur += 1;
    if (c === "}" || c === "]") {
      profondeur -= 1;
      if (profondeur === 0) return texte.slice(depart, i + 1);
    }
  }
  throw new Error("bloc non équilibré");
}

/** Extrait `(async )?function nom(paramètres) { … }` du source réel. */
function extraireFonction(nom) {
  const motif = new RegExp(`(?:async\\s+)?function\\s+${nom}\\s*\\([^)]*\\)\\s*\\{`);
  const trouve = source.match(motif);
  if (!trouve) throw new Error(`« ${nom} » introuvable dans app.js`);
  const ouverture = trouve.index + trouve[0].length - 1;
  const bloc = blocEquilibre(source, ouverture);
  return source.slice(trouve.index, ouverture + bloc.length);
}

const apiBase = source.match(/const API_BASE = "([^"]+)";/);
if (!apiBase) throw new Error("« API_BASE » introuvable dans app.js");
const urlAttendue = `${apiBase[1]}/deduction/sessions`;

const fabrique = new Function(`
  const requetes = [];
  let reponseFactice = { items: [{ id: "item-test" }], session_id: "session-test" };
  let echecAvantSucces = 0;
  let reessaiReseau = null;
  let reessaiBandeau = null;

  const fetch = async (url, options) => {
    requetes.push({ url, options });
    if (echecAvantSucces > 0) {
      echecAvantSucces -= 1;
      throw new Error("réseau simulé");
    }
    return { ok: true, status: 201, json: async () => reponseFactice };
  };

  const etat = { actionEnCours: false };
  let sansLimiteActif = false;
  function sansLimiteActivee() { return sansLimiteActif; }
  function reglerEtatBoutons() {}
  function masquerBandeau() {}
  function cloreSessionSilencieusement() {}
  function montrerNoticeThemes() {}
  function preparerEcranSeance() {}
  function afficherVue() {}
  function montrerItem() {}
  function reinitialiserConfirmationFin() {}
  function masquerNoticeThemes() {}
  function afficherErreurReseau(relance) { reessaiReseau = relance; }
  function afficherBandeau(message, options = {}) {
    reessaiBandeau = options.reessayer || null;
  }

  const API_BASE = ${JSON.stringify(apiBase[1])};
  ${extraireFonction("apiFetch")}
  ${extraireFonction("demarrerSession")}

  return {
    demarrerSession,
    outils: {
      preparer: (donnees, echecs = 0) => { reponseFactice = donnees; echecAvantSucces = echecs; },
      remettreAZero: () => {
        requetes.length = 0;
        reessaiReseau = null;
        reessaiBandeau = null;
        echecAvantSucces = 0;
      },
      requetes: () => requetes,
      reessaiReseau: () => reessaiReseau,
      reglerSansLimite: (actif) => { sansLimiteActif = actif; },
    },
  };
`);

const { demarrerSession, outils } = fabrique();
const theme = { id: "deduction" };
const echecs = [];

function verifier(condition, message) {
  if (!condition) echecs.push(message);
}

(async () => {
  // 1. Essai « palier 2 » : le corps JSON porte le palier, la méthode est POST.
  outils.remettreAZero();
  outils.reglerSansLimite(false);

  await demarrerSession(theme, 2);
  let requetes = outils.requetes();
  verifier(requetes.length === 1, `palier 2 : ${requetes.length} requête(s) au lieu d'une`);
  if (requetes.length) {
    const { url, options } = requetes[0];
    verifier(url === urlAttendue, `URL inattendue : ${url}`);
    verifier(options.method === "POST", "méthode non POST");
    verifier(
      typeof options.body === "string" && JSON.parse(options.body).palier === 2,
      `corps sans palier 2 : ${options.body}`
    );
    verifier(
      (options.headers || {})["Content-Type"] === "application/json",
      "en-tête Content-Type manquant"
    );
  }

  // 2. Mode auto : aucun corps — le serveur suit la progression.
  outils.remettreAZero();
  outils.reglerSansLimite(false);
  await demarrerSession(theme);
  requetes = outils.requetes();
  verifier(requetes.length === 1, `auto : ${requetes.length} requête(s) au lieu d'une`);
  if (requetes.length) {
    verifier(
      requetes[0].options.body === undefined,
      `auto : corps inattendu (${requetes[0].options.body})`
    );
    verifier(
      (requetes[0].options.headers || {})["Content-Type"] === undefined,
      "auto : en-tête Content-Type inattendu"
    );
  }

  // 3. Un réessai après incident réseau conserve le palier choisi.
  outils.remettreAZero();
  outils.reglerSansLimite(false);
  outils.preparer({ items: [{ id: "item-test" }], session_id: "session-test" }, 1);
  await demarrerSession(theme, 2);
  const relance = outils.reessaiReseau();
  verifier(typeof relance === "function", "palier 2 + incident réseau : aucun réessai proposé");
  if (typeof relance === "function") {
    await relance();
    requetes = outils.requetes();
    verifier(requetes.length === 2, `réessai : ${requetes.length} requête(s) au total au lieu de deux`);
    if (requetes.length >= 2) {
      verifier(
        typeof requetes[1].options.body === "string"
          && JSON.parse(requetes[1].options.body).palier === 2,
        "réessai : le palier choisi est perdu"
      );
    }
  }

  // 4. Dérogation « dépasser la limite » : le corps la porte telle quelle (sans palier).
  outils.remettreAZero();
  outils.reglerSansLimite(true);
  await demarrerSession(theme);
  requetes = outils.requetes();
  verifier(requetes.length === 1, `dérogation : ${requetes.length} requête(s) au lieu d'une`);
  if (requetes.length) {
    const corps = typeof requetes[0].options.body === "string"
      ? JSON.parse(requetes[0].options.body)
      : null;
    verifier(
      corps && corps.sans_limite_sessions === true && Object.keys(corps).length === 1,
      `dérogation : corps inattendu (${requetes[0].options.body})`
    );
    verifier(
      (requetes[0].options.headers || {})["Content-Type"] === "application/json",
      "dérogation : en-tête Content-Type manquant"
    );
  }

  // 5. Dérogation + palier ensemble — et le réessai réseau conserve les deux.
  outils.remettreAZero();
  outils.preparer({ items: [{ id: "item-test" }], session_id: "session-test" }, 1);
  await demarrerSession(theme, 3);
  const relanceDerogation = outils.reessaiReseau();
  verifier(typeof relanceDerogation === "function", "dérogation + palier 3 : aucun réessai proposé");
  if (typeof relanceDerogation === "function") {
    await relanceDerogation();
  }
  requetes = outils.requetes();
  verifier(
    requetes.length === 2,
    `dérogation + palier : ${requetes.length} requête(s) au total au lieu de deux`
  );
  for (const requete of requetes) {
    const corps = typeof requete.options.body === "string"
      ? JSON.parse(requete.options.body)
      : {};
    verifier(corps.palier === 3, `dérogation + palier : palier perdu (${requete.options.body})`);
    verifier(
      corps.sans_limite_sessions === true,
      `dérogation + palier : dérogation perdue (${requete.options.body})`
    );
  }
  outils.reglerSansLimite(false);

  // 6. Un parcours choisi est transmis et survit au réessai réseau.
  outils.remettreAZero();
  outils.preparer({ items: [{ id: "item-test" }], session_id: "session-test" }, 1);
  await demarrerSession(theme, null, "mots");
  const relanceParcours = outils.reessaiReseau();
  verifier(typeof relanceParcours === "function", "parcours + incident réseau : aucun réessai proposé");
  if (typeof relanceParcours === "function") await relanceParcours();
  requetes = outils.requetes();
  verifier(requetes.length === 2, `parcours : ${requetes.length} requête(s) au lieu de deux`);
  for (const requete of requetes) {
    const corps = typeof requete.options.body === "string" ? JSON.parse(requete.options.body) : {};
    verifier(corps.parcours === "mots", `parcours perdu (${requete.options.body})`);
  }

  if (echecs.length) {
    for (const echec of echecs) console.error(`✗ ${echec}`);
    process.exit(1);
  }
  console.log("✓ palier 2 : POST avec corps {\"palier\": 2} et Content-Type JSON");
  console.log("✓ auto : POST sans corps (le serveur suit la progression)");
  console.log("✓ réessai réseau : le palier choisi est conservé");
  console.log('✓ dérogation active : POST avec corps {"sans_limite_sessions": true}');
  console.log("✓ dérogation + palier : les deux champs partent, réessai compris");
  console.log("✓ parcours : transmis et conservé au réessai");
})();
