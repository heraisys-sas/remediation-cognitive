"use strict";
const NBACK_FORMES = { cercle: "Cercle", carre: "Carré", triangle: "Triangle", etoile: "Étoile" };
let nbackSession = null;
function nbackConsigne(n = 1) {
  const reference = n === 1 ? "celle juste avant" : `celle ${n} places avant`;
  return `Une seule forme apparaît à la fois. Mémorise ${n === 1 ? "la première forme" : `les ${n} premières formes`}. Ensuite, indique si chaque forme est identique à ${reference}, ou différente. Après chaque réponse, clique sur Suivant. Il n’y a pas de limite de temps ni de correction pendant la série. Si tu ne sais pas, tu peux le dire. Tu peux terminer la séance à tout moment.`;
}
function nbackBouton(texte, action, principal = false) {
  const b = creerElement("button", { texte, classe: `bouton bouton-${principal ? "primaire" : "secondaire"}`, attributs: { type: "button" } });
  b.addEventListener("click", action); return b;
}
function carteNBack() {
  const carte = creerElement("article", { classe: "carte-theme" }, creerElement("h3", { texte: "N-back : comparer les formes" }), creerElement("p", { texte: "Comparer une forme avec celle une, deux ou trois places avant, à ton rythme." }));
  carte.dataset.activite = "nback";
  const reglages = creerElement("details", { classe: "choix-parcours" }, creerElement("summary", { texte: "Réglages de cette séance" }));
  const select = creerElement("select", { classe: "selecteur-palier", attributs: { "aria-label": "Distance de comparaison N-back" } });
  for (const n of [1, 2, 3]) select.append(creerElement("option", { texte: `${n}-back : ${n === 1 ? "la forme juste avant" : `${n} places avant`}`, attributs: { value: String(n) } }));
  const saved = Number(preferenceLocale("orthogone.nback.n", "1")); select.value = String([1, 2, 3].includes(saved) ? saved : 1);
  select.addEventListener("change", () => garderPreference("orthogone.nback.n", select.value));
  reglages.append(select); carte.append(reglages, nbackBouton("Commencer", () => demarrerNBack(Number(select.value)), true)); return carte;
}
function nbackApi(path, body) { return fetchJson("/api/nback", path, { method: "POST", body: JSON.stringify(body) }); }
async function demarrerNBack(n = 1) {
  if (etat.actionEnCours) return; etat.actionEnCours = true;
  try {
    await CAPACITES.chargerVoixLocales?.();
    const data = await nbackApi("/sessions", { n, sans_limite_sessions: sansLimiteActivee() });
    CAPACITES.arreter(); annulerMemo(); nbackSession = { ...data, choix: null, pending: null, busy: false, interrompre: false, exemple: null };
    afficherVue("nback"); rendreNBack();
  } catch (e) { afficherBandeau(e.status === 429 ? "La limite de séances est atteinte aujourd’hui." : "Impossible de commencer la séance.", e.status === 429 ? {} : { reessayer: () => demarrerNBack(n) }); }
  finally { etat.actionEnCours = false; }
}
async function nbackEtape(action, donnees = {}, fin = false) {
  const s = nbackSession; if (!s || s.busy || s.pending || s.sortiePage) return;
  s.pending = { path: `/sessions/${s.session_id}/${fin ? "fin" : "etapes"}`, body: fin ? {} : { etape_id: crypto.randomUUID(), action, donnees }, fin };
  return nbackEnvoyer();
}
async function nbackEnvoyer() {
  const s = nbackSession; if (!s?.pending || s.busy) return;
  s.busy = true; CAPACITES.arreter(); nbackEffacerForme();
  [$("nback-contenu"), $("nback-commandes")].forEach(n => n.querySelectorAll("button").forEach(b => { b.disabled = !b.nbackInterruption; }));
  try {
    const p = s.pending, data = await nbackApi(p.path, p.body); s.pending = null; s.busy = false;
    if (s.sortiePage) return;
    if (p.fin) { nbackSession = null; revenirAuxThemes(); return; }
    Object.assign(s, data); s.choix = null;
    if ((document.hidden || s.interrompre) && ["initialisation", "decision", "neutre"].includes(s.phase)) {
      const raison = s.interrompre || "masquage"; s.interrompre = false; return nbackEtape("interrompre", { raison });
    }
    if (!$("vue-nback").hidden) rendreNBack();
  } catch {
    s.busy = false; if (s.sortiePage) return;
    $("nback-commandes").replaceChildren(creerElement("p", { texte: "La sauvegarde n’est pas confirmée. Réessaie avant de poursuivre.", attributs: { role: "alert" } }), nbackBouton("Réessayer", nbackEnvoyer, true));
  }
}
function nbackEffacerForme() { const zone = $("nback-contenu").querySelector(".nback-forme"); if (zone) { zone.replaceChildren(); zone.removeAttribute("role"); zone.removeAttribute("aria-label"); } }
function nbackForme(parent, symbole) {
  const zone = creerElement("div", { classe: "nback-forme mi-visual-cell", attributs: { role: "img", "aria-label": NBACK_FORMES[symbole] || "Forme" } });
  zone.append(immediateVisualGlyph(symbole)); parent.append(zone);
}
function nbackAudio(parent) {
  let lecture = false;
  const b = nbackBouton("Écouter", () => {
    if (lecture) { CAPACITES.arreter(); terminer(); return; }
    lecture = true; actualiserBoutonAudio(true, b);
    if (CAPACITES.lire(nbackConsigne(nbackSession?.n || 1), { francais: true, onFin: terminer, onErreur: terminer }) === false) terminer();
  });
  function terminer() { lecture = false; actualiserBoutonAudio(false, b); }
  b.className = "bouton bouton-discret bouton-audio";
  if (CAPACITES.syntheseDisponible?.() !== false) parent.append(creerElement("div", { classe: "ligne-audio" }, b));
}
function rendreNBack() {
  const s = nbackSession; if (!s) return; CAPACITES.arreter();
  const c = $("nback-contenu"), commandes = $("nback-commandes"); c.replaceChildren(); commandes.replaceChildren();
  const n = s.n || 1;
  $("titre-nback").textContent = "N-back : comparer les formes";
  $("nback-progression").textContent = s.phase === "ready" ? `Observation visuelle · ${n}-back` : ["resultat", "interrompu"].includes(s.phase) ? "Retour sur l’observation" : `Forme ${s.position} sur ${s.total}`;
  const texte = t => c.append(creerElement("p", { texte: t })); let principal;
  const suite = (titre, action) => { principal = nbackBouton(titre, action, true); commandes.append(principal); };
  if (s.phase === "ready" && s.exemple !== null) {
    nbackExemple(c, commandes); principal = commandes.querySelector(".bouton-primaire");
  } else if (s.phase === "ready") {
    texte(nbackConsigne(n)); texte(`La série contient ${s.total || n + 15} formes. ${n === 1 ? "La première sert" : `Les ${n} premières servent`} à mémoriser, les 15 suivantes demandent une réponse.`); nbackAudio(c);
    commandes.append(nbackBouton("Voir un exemple", () => { s.exemple = { position: 0, choix: null, corrige: false }; rendreNBack(); }));
    suite("Commencer", () => nbackEtape("commencer"));
  } else if (s.phase === "initialisation") {
    texte(`Mémorise cette forme (${s.position} sur ${n} pour démarrer).`); nbackForme(c, s.symbole); suite("Suivant", () => nbackEtape("suivant"));
  } else if (s.phase === "decision") {
    texte(`Identique à la forme ${n === 1 ? "juste avant" : `${n} places avant`}, ou différente ?`); nbackForme(c, s.symbole);
    const choix = creerElement("div", { classe: "nback-choix mi-controls" });
    for (const [value, label] of [["identique", "Identique"], ["different", "Différent"], ["absence", "Je ne sais pas"]]) {
      const b = nbackBouton(label, () => { s.choix = value; rendreNBack(); }); b.setAttribute("aria-pressed", String(s.choix === value)); if (s.choix === value) b.classList.add("selectionnee"); choix.append(b);
    }
    c.append(choix); suite("Valider", () => nbackEtape("repondre", { decision: s.choix })); principal.disabled = s.choix === null;
  } else if (s.phase === "neutre") {
    texte("Réponse enregistrée."); suite("Suivant", () => nbackEtape("suivant"));
  } else {
    nbackBilan(c, s.resultat || {}); suite("Retour à l’accueil", () => nbackEtape("", {}, true));
  }
  if (!["resultat", "interrompu"].includes(s.phase)) {
    for (const [label, raison] of [["Terminer la séance", "sortie"]]) { const b = nbackBouton(label, () => nbackInterrompre(raison)); b.nbackInterruption = true; commandes.append(b); }
  }
  $("vue-nback").onkeydown = e => {
    if (e.repeat && ["Enter", " "].includes(e.key)) { e.preventDefault(); return; }
    if (e.key === "Enter" && !e.repeat && !e.isComposing && !e.ctrlKey && !e.altKey && !e.metaKey && !e.shiftKey && !e.target?.isContentEditable && !["BUTTON", "SELECT", "TEXTAREA", "A", "SUMMARY"].includes(e.target?.tagName) && !s.pending && !s.busy && !$("vue-nback").hidden && principal && !principal.disabled) { e.preventDefault(); principal.click(); }
  };
  if (s.phase !== "decision" || s.choix !== null) principal?.focus();
}
function nbackExemple(c, commandes) {
  const s = nbackSession, ex = s.exemple, n = s.n || 1;
  const sequence = { 1: ["cercle", "carre", "carre", "triangle"], 2: ["cercle", "carre", "cercle", "triangle", "triangle"], 3: ["cercle", "carre", "triangle", "cercle", "carre", "triangle", "etoile"] }[n];
  const identique = ex.position >= n && sequence[ex.position] === sequence[ex.position - n], attendu = identique ? "identique" : "different";
  c.append(creerElement("p", { texte: `Exemple guidé ${n}-back, hors séance.` })); nbackForme(c, sequence[ex.position]);
  if (ex.position < n) c.append(creerElement("p", { texte: `Mémorise cette forme (${ex.position + 1} sur ${n} pour démarrer).` }));
  if (ex.corrige) c.append(creerElement("p", { texte: `${ex.choix === attendu ? "Oui." : "À revoir."} Cette forme est ${identique ? "identique à" : "différente de"} celle ${n === 1 ? "juste avant" : `${n} places avant`}.` }));
  if (ex.position >= n && !ex.corrige) {
    for (const [value, label] of [["identique", "Identique"], ["different", "Différent"]]) commandes.append(nbackBouton(label, () => { ex.choix = value; ex.corrige = true; rendreNBack(); }));
  } else commandes.append(nbackBouton(ex.position === sequence.length - 1 ? "Revenir à la consigne" : "Suivant", () => { if (ex.position === sequence.length - 1) s.exemple = null; else { ex.position++; ex.corrige = false; ex.choix = null; } rendreNBack(); }, true));
  commandes.append(nbackBouton("Quitter l’exemple", () => { s.exemple = null; rendreNBack(); }));
}
function nbackBilan(parent, resultat) {
  parent.append(creerElement("p", { texte: resultat.statut === "interrompu" ? "L’observation a été interrompue. Les réponses déjà enregistrées sont conservées." : "La série est terminée." }));
  if (resultat.decisions_observees === 0) { parent.append(creerElement("p", { texte: "Aucune réponse enregistrée." })); return; }
  const labels = { decisions_observees: "Réponses enregistrées", correspondances_detectees: "Identiques reconnues", correspondances_manquees: "Identiques non reconnues", fausses_alertes: "Différentes jugées identiques", non_correspondances_rejetees: "Différentes reconnues", absences_declarees: "Réponses « Je ne sais pas »" };
  for (const [key, label] of Object.entries(labels)) if (Number.isFinite(resultat[key])) {
    const total = key === "correspondances_detectees" ? resultat.correspondances_observees : key === "non_correspondances_rejetees" ? resultat.non_correspondances_observees : null;
    if (total === 0) { parent.append(creerElement("p", { texte: key === "correspondances_detectees" ? "Aucune forme identique observée." : "Aucune forme différente observée." })); continue; }
    parent.append(creerElement("p", { texte: `${label} : ${resultat[key]}${Number.isFinite(total) ? ` sur ${total}` : ""}` }));
  }
  parent.append(creerElement("p", { texte: "Ces observations décrivent cette série à ton rythme. Elles ne constituent pas un score clinique ni une mesure d’intelligence." }));
}
function nbackInterrompre(raison = "masquage") {
  const s = nbackSession; if (!s || ["resultat", "interrompu"].includes(s.phase)) return;
  CAPACITES.arreter(); nbackEffacerForme(); s.exemple = null; s.interrompre = raison;
  if (!s.busy && !s.pending) { s.interrompre = false; return nbackEtape("interrompre", { raison }); }
}
document.addEventListener("visibilitychange", () => { if (document.hidden) nbackInterrompre("masquage"); });
function nbackQuitter() {
  CAPACITES.arreter(); nbackInterrompre("sortie"); $("nback-contenu").replaceChildren(); $("nback-commandes").replaceChildren();
}

window.addEventListener("pagehide", () => {
  const s = nbackSession; CAPACITES.arreter(); $("nback-contenu").replaceChildren(); $("nback-commandes").replaceChildren();
  if (!s || s.sortiePage) return;
  s.sortiePage = true;
  if (["resultat", "interrompu"].includes(s.phase)) return;
  s.interrompre = "sortie";
  // Dernière tentative de clôture ; aucun accusé n'est garanti à la fermeture.
  try { fetch(`/api/nback/sessions/${s.session_id}/fin`, { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}", keepalive: true }).catch(() => {}); } catch {}
});

window.addEventListener("pageshow", e => {
  if (e.persisted && nbackSession?.sortiePage) { nbackSession = null; revenirAuxThemes(); }
});
