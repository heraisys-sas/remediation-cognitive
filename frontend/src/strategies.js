"use strict";
const STRATEGIES_NOMS = { plan: "Préparer et utiliser un plan", rappel: "Utiliser un rappel", message: "Prendre un message", temps: "Estimer et organiser son temps" };
let strategieSession = null;
function strategieBouton(texte, action, principal = false) {
  const b = creerElement("button", { texte, classe: `bouton bouton-${principal ? "primaire" : "secondaire"}`, attributs: { type: "button" } });
  b.addEventListener("click", action); return b;
}
function carteStrategies() {
  const carte = creerElement("article", { classe: "carte-theme" }, creerElement("h3", { texte: "Application des stratégies" }), creerElement("p", { texte: "Préparer, agir et vérifier dans une petite simulation." }));
  carte.dataset.activite = "strategies";
  const choix = creerElement("details", { classe: "choix-parcours" }, creerElement("summary", { texte: "Choisir le parcours" }));
  const select = creerElement("select", { classe: "selecteur-palier", attributs: { "aria-label": "Parcours de stratégies" } });
  Object.entries(STRATEGIES_NOMS).forEach(([value, texte]) => select.append(creerElement("option", { texte, attributs: { value } })));
  select.value = preferenceLocale("orthogone.strategies.parcours", "plan");
  if (!STRATEGIES_NOMS[select.value]) select.value = "plan";
  const condition = creerElement("select", { classe: "selecteur-palier", attributs: { "aria-label": "Aide pendant la séance" } });
  condition.append(creerElement("option", { texte: "Avec une note", attributs: { value: "avec-note" } }), creerElement("option", { texte: "Sans note", attributs: { value: "sans-note" } })); condition.value = preferenceLocale("orthogone.strategies.condition", "avec-note");
  condition.addEventListener("change", () => garderPreference("orthogone.strategies.condition", condition.value));
  const changer = () => { condition.hidden = !["message", "rappel"].includes(select.value); condition.options[0].textContent = select.value === "rappel" ? "Avec un rappel" : "Avec une note"; condition.options[1].textContent = select.value === "rappel" ? "Sans rappel" : "Sans note"; }; select.addEventListener("change", () => { garderPreference("orthogone.strategies.parcours", select.value); changer(); }); changer();
  choix.append(select, condition); carte.append(choix, strategieBouton("Commencer", () => demarrerStrategies(select.value, condition.value), true)); return carte;
}
function strategieApi(path, body) { return fetchJson("/api/strategies", path, { method: "POST", body: JSON.stringify(body) }); }
async function demarrerStrategies(parcours, condition = "avec-note") {
  if (etat.actionEnCours) return; etat.actionEnCours = true;
  try {
    await CAPACITES.chargerVoixLocales?.();
    const data = await strategieApi("/sessions", { parcours, ...(parcours === "message" ? { condition } : {}), sans_limite_sessions: sansLimiteActivee() });
    CAPACITES.arreter(); annulerMemo();
    strategieSession = { ...data, rappelChoisi: condition === "avec-note", note: "", noteVisible: false, timing: null, brouillon: {}, ordre: null, pending: null, busy: false, paused: false };
    afficherVue("strategies"); rendreStrategies();
  } catch (e) { afficherBandeau(e.status === 429 ? "La limite de séances est atteinte aujourd’hui." : "Impossible de commencer la séance.", e.status === 429 ? {} : { reessayer: () => demarrerStrategies(parcours, condition) }); }
  finally { etat.actionEnCours = false; }
}
// Le même identifiant et le même contenu sont conservés jusqu'à l'accusé durable.
async function strategieEtape(action, donnees = {}, fin = false) {
  const s = strategieSession; if (!s || s.busy || s.pending) return;
  if (action === "classer" && s.timing) { const now = performance.now(); s.timing.active += now - s.timing.segment; s.timing.segment = null; if (Object.keys(s.donnees.classement || {}).length === (s.scenario.documents || []).length - 1) s.timing.fin = now; }
  if (action === "pause" && s.timing && s.timing.pause === null) { s.timing.pause = performance.now(); if (s.timing.segment !== null) { s.timing.active += s.timing.pause - s.timing.segment; s.timing.segment = null; } }
  if (action === "reprendre" && s.timing?.pause !== null && s.timing) { s.timing.pauses += performance.now() - s.timing.pause; s.timing.pause = null; }
  s.pending = { path: `/sessions/${s.session_id}/${fin ? "fin" : "etapes"}`, body: fin ? {} : { etape_id: crypto.randomUUID(), action, donnees }, fin };
  return strategieEnvoyer();
}
async function strategieEnvoyer() {
  const s = strategieSession; if (!s?.pending || s.busy) return;
  s.busy = true; CAPACITES.arreter(); strategieVerrouiller(true);
  try {
    const p = s.pending; const data = await strategieApi(p.path, p.body);
    s.pending = null; s.busy = false;
    if (p.fin) { strategieSession = null; revenirAuxThemes(); return; }
    Object.assign(s, data);
    if (p.body.action === "pause") s.paused = true;
    if (p.body.action === "reprendre") s.paused = false;
    s.noteVisible = false; rendreStrategies();
  } catch {
    s.busy = false; const commandes = $("strategie-commandes");
    commandes.replaceChildren(creerElement("p", { texte: "La sauvegarde n’est pas confirmée. Réessaie avant de poursuivre.", attributs: { role: "alert" } }), strategieBouton("Réessayer", strategieEnvoyer, true));
  }
}
function strategieVerrouiller(disabled) {
  [$("strategie-contenu"), $("strategie-commandes")].forEach(n => n.querySelectorAll("button, input, select, textarea").forEach(b => { b.disabled = disabled; }));
}
function strategieChamp(parent, titre, type = "text", valeur = "") {
  const input = creerElement("input", { attributs: { type } }); input.value = strategieSession.brouillon[`${strategieSession.phase}:${titre}`] ?? valeur;
  input.addEventListener("input", () => { strategieSession.brouillon[`${strategieSession.phase}:${titre}`] = input.value; });
  parent.append(creerElement("label", { texte: titre }, input)); return input;
}
function strategieSelect(parent, titre, options) {
  const input = creerElement("select", { classe: "selecteur-palier" });
  input.append(creerElement("option", { texte: "Choisir…", attributs: { value: "" } }));
  options.forEach(([value, texte]) => input.append(creerElement("option", { texte, attributs: { value } })));
  input.value = strategieSession.brouillon[`${strategieSession.phase}:${titre}`] ?? "";
  input.addEventListener("change", () => { strategieSession.brouillon[`${strategieSession.phase}:${titre}`] = input.value; });
  parent.append(creerElement("label", { texte: titre }, input)); return input;
}
function rendreStrategies() {
  const s = strategieSession; if (!s) return;
  CAPACITES.arreter(); const c = $("strategie-contenu"), commandes = $("strategie-commandes"); c.replaceChildren(); commandes.replaceChildren();
  $("titre-strategies").textContent = STRATEGIES_NOMS[s.parcours]; $("strategie-progression").textContent = s.phase === "correction" ? "Retour sur la simulation" : "Une étape à la fois, à ton rythme";
  const scenario = s.scenario || {}, d = s.donnees || {};
  if (s.parcours === "temps" && s.phase === "classement" && !s.paused) { s.timing ||= { debut: performance.now(), segment: null, active: 0, pause: null, pauses: 0, fiable: true }; if (s.timing.segment === null) s.timing.segment = performance.now(); }
  const texte = t => c.append(creerElement("p", { texte: t }));
  let principal;
  const suite = (titre, action, valeurs = () => ({})) => { principal = strategieBouton(titre, () => strategieEtape(action, valeurs()), true); commandes.append(principal); };
  if (s.paused) { texte("La séance est en pause. Ton travail est conservé."); suite("Reprendre", "reprendre"); }
  else if (s.phase === "correction") {
    texte("La simulation est terminée. Ce retour décrit les actions réalisées dans cette situation.");
    const resultat = s.resultat || d.resultat || d;
    strategieBilan(c, resultat.observations || resultat); strategieCorrection(c, resultat.correction);
    commandes.replaceChildren(strategieBouton("Retour à l’accueil", () => strategieEtape("", {}, true), true)); principal = commandes.querySelector("button");
  } else if (s.parcours === "plan") {
    texte(scenario.but);
    (scenario.contraintes || []).forEach(texte);
    if (["plan_initial", "revision"].includes(s.phase)) {
      if (s.phase === "revision") texte("Une nouvelle contrainte a été ajoutée. Vérifie ton plan, puis utilise-le.");
      const actions = scenario.actions || [];
      s.ordre ||= actions.map(a => a.id); const liste = creerElement("ol");
      s.ordre.forEach((id, i) => { const ligne = creerElement("li", { texte: actions.find(a => a.id === id)?.texte || id });
        for (const [delta, label] of [[-1, "Monter"], [1, "Descendre"]]) { const b = strategieBouton(`${label} ${i + 1}`, () => { [s.ordre[i], s.ordre[i + delta]] = [s.ordre[i + delta], s.ordre[i]]; rendreStrategies(); }); b.disabled = i + delta < 0 || i + delta >= s.ordre.length; ligne.append(b); } liste.append(ligne); }); c.append(liste);
      suite(s.phase === "plan_initial" ? "Enregistrer mon plan" : "Utiliser ce plan", s.phase === "plan_initial" ? "plan_initial" : "reviser", () => ({ ordre: [...s.ordre] }));
    } else if (s.phase === "execution") {
      const faites = d.actions_executees || d.executees || []; const id = (d.plan_final || s.ordre || []).find(id => !faites.includes(id));
      texte(`Plan : ${(d.plan_final || s.ordre || []).map(id => (scenario.actions || []).find(a => a.id === id)?.texte || id).join(" → ")}`);
      if (id) suite(`Réaliser : ${(scenario.actions || []).find(a => a.id === id)?.texte || id}`, "executer", () => ({ action_id: id })); else suite("Passer à la vérification", "verifier");
    } else { texte(`Actions réalisées : ${(d.actions_executees || []).map(id => (scenario.actions || []).find(a => a.id === id)?.texte || id).join(" → ")}`); texte("Vérifie les actions et les contraintes avant de terminer. Tu peux chercher sans afficher la correction."); suite(d.verification_realisee ? "Voir le résultat" : "Vérifier mon plan", d.verification_realisee ? "terminer" : "verifier"); }
  } else if (s.parcours === "rappel") {
    if (s.phase === "configuration") texte(scenario.consigne);
    if (s.phase === "configuration") { const piece = strategieSelect(c, "Pièce prévue", (scenario.pieces || []).map(p => [p.id, p.texte])); suite("Configurer mon intention", "configurer", () => ({ piece_id: piece.value, rappel: s.rappelChoisi })); }
    else if (s.phase === "intercale") { const faites = d.actions_intercalees || d.intercalees || []; const action = (scenario.actions_intercalees || []).find(a => !faites.includes(a.id)); if (action) { texte(action.texte); suite("C’est vérifié", "intercaler", () => ({ action_id: action.id })); } }
    else { texte(d.signal); if (d.rappel_delivre) commandes.append(strategieBouton("Consulter mon rappel", async () => { await strategieEtape("consulter_rappel"); if (strategieSession && !strategieSession.pending) c.append(creerElement("p", { texte: strategieSession.scenario.rappel_texte || `Joindre : ${(scenario.pieces || []).find(p => p.id === d.piece_prevue)?.texte || d.piece_prevue}` })); }));
      if (!d.piece_jointe) commandes.append(strategieBouton("Continuer sans joindre", () => strategieEtape("terminer")));
      if (d.piece_jointe) {
        texte(`Pièce jointe : ${(scenario.pieces || []).find(p => p.id === d.piece_jointe)?.texte || d.piece_jointe}`);
        suite("Voir le résultat", "terminer");
      } else {
        const piece = strategieSelect(c, "Pièce à joindre", (scenario.pieces || []).map(p => [p.id, p.texte]));
        suite("Joindre la pièce", "joindre", () => ({ piece_id: piece.value }));
      }
    }
  } else if (s.parcours === "message") {
    if (s.phase === "encodage") {
      texte(scenario.message);
      if (s.condition === "avec-note") { const note = creerElement("textarea", { attributs: { rows: "3" } }); note.value = s.note; note.addEventListener("input", () => { s.note = note.value; }); c.append(creerElement("label", { texte: "Ma note (facultative, conservée seulement ici)" }, note)); }
      suite("Masquer le message", "masquer", () => ({ note_presente: Boolean(s.note.trim()) }));
    } else {
      commandes.append(strategieBouton("Revoir le message", () => strategieEtape("reecouter")));
      if (s.condition === "avec-note" && s.note.trim()) commandes.append(strategieBouton("Consulter ma note", async () => { await strategieEtape("consulter_note"); if (!strategieSession?.pending) { s.noteVisible = true; c.append(creerElement("p", { texte: s.note })); } }));
      if (s.phase === "restitution") { texte("Redis ce que tu as retenu."); const quoi = strategieChamp(c, "Quoi faire ?", "text", s.brouillon.quoi || ""), quand = strategieChamp(c, "Quand ?", "text", s.brouillon.quand || "");
        quoi.addEventListener("input", () => { s.brouillon.quoi = quoi.value; }); quand.addEventListener("input", () => { s.brouillon.quand = quand.value; }); suite("Valider ma restitution", "restituer", () => ({ quoi: quoi.value, quand: quand.value, absence: !quoi.value.trim() && !quand.value.trim() })); }
      else { const action = strategieSelect(c, "Action à réaliser", (scenario.actions || []).map(a => [a.id, a.texte])), heure = strategieSelect(c, "Créneau", (scenario.heures || []).map(h => [h, h])); suite("Réaliser la demande", "agir", () => ({ action_id: action.value, heure: heure.value })); }
    }
  } else if (s.parcours === "temps") {
    texte(scenario.consigne);
    if (s.phase === "estimation") { const minutes = strategieChamp(c, "Durée estimée (minutes)", "number", "2"); minutes.min = "0.1"; minutes.step = "0.1"; minutes.max = "1440"; suite("Commencer le classement", "estimer", () => ({ secondes: Number(minutes.value) * 60 })); }
    else if (s.phase === "classement") {
      const documents = scenario.documents || []; documents.forEach(x => texte(x.texte)); const classes = d.classement || {}; const doc = documents.find(x => !(x.id in classes));
      if (doc) { texte(doc.libelle || doc.texte || doc.id); const categorie = strategieSelect(c, `Dossier pour ${doc.texte}`, (scenario.categories || []).map(categorie => [categorie, categorie.charAt(0).toUpperCase() + categorie.slice(1)])); suite("Classer ce document", "classer", () => ({ document_id: doc.id, categorie: categorie.value })); } else suite("Examiner mon estimation", "comparer", () => strategieTemps(s));
    } else if (!d.comparaison_realisee) { suite("Examiner mon estimation", "comparer", () => strategieTemps(s)); } else { strategieBilan(c, d); if (!Number.isFinite(d.duree_active_secondes)) texte("La durée n’a pas pu être mesurée de façon fiable. Tu peux préparer une marge sans comparaison."); const marge = strategieChamp(c, "Marge pour une prochaine tâche (minutes)", "number", "1"); marge.min = "0"; marge.max = "1440"; suite("Préparer cette marge", "marge", () => ({ secondes: Number(marge.value) * 60 })); }
  }
  if (!s.paused && s.phase !== "correction") commandes.append(strategieBouton("Mettre en pause", () => strategieEtape("pause")));
  if (s.phase !== "correction") commandes.append(strategieBouton("Terminer la séance", () => strategieEtape("", {}, true)));
  const lisible = Array.from(c.querySelectorAll("p")).map(p => p.textContent).join(". ");
  if (lisible && CAPACITES.syntheseDisponible?.() !== false) {
    let lecture = false;
    const audio = strategieBouton("Écouter", () => {
      if (lecture) { CAPACITES.arreter(); terminer(); return; }
      lecture = true; actualiserBoutonAudio(true, audio);
      const texteVisible = Array.from(c.querySelectorAll("p")).map(p => p.textContent).join(". ");
      if (CAPACITES.lire(texteVisible, { francais: true, onFin: terminer, onErreur: terminer }) === false) terminer();
    });
    audio.className = "bouton bouton-discret bouton-audio";
    function terminer() { lecture = false; actualiserBoutonAudio(false, audio); }
    c.append(creerElement("div", { classe: "ligne-audio" }, audio));
  }
  c.onkeydown = e => { if (e.key === "Enter" && !e.repeat && !e.isComposing && !e.ctrlKey && !e.altKey && !e.metaKey && !e.shiftKey && !e.target?.isContentEditable && !["TEXTAREA", "BUTTON", "SELECT", "A", "SUMMARY"].includes(e.target?.tagName) && principal && !principal.disabled) { e.preventDefault(); principal.click(); } };
  const champs = [...c.querySelectorAll("select, input[type='number']")];
  const verifierChamps = () => {
    if (principal) principal.disabled = champs.some(champ => !champ.value || (champ.tagName === "INPUT" && (!Number.isFinite(Number(champ.value)) || Number(champ.value) < Number(champ.min || 0) || Number(champ.value) > Number(champ.max || Infinity))));
  };
  champs.forEach(champ => { champ.addEventListener("change", verifierChamps); champ.addEventListener("input", verifierChamps); });
  verifierChamps(); principal?.focus();
}
function strategieBilan(parent, resultat) {
  const labels = { estimation_secondes: "Estimation", duree_active_secondes: "Durée active", duree_ecoulee_secondes: "Durée écoulée", pauses_secondes: "Pauses", attente_interface_secondes: "Attente de l’interface", ecart_secondes: "Écart (durée active moins estimation)" };
  for (const [key, label] of Object.entries(labels)) if (Number.isFinite(resultat[key])) parent.append(creerElement("p", { texte: `${label} : ${key === "ecart_secondes" && resultat[key] > 0 ? "+" : ""}${Number(resultat[key].toFixed(1)).toLocaleString("fr-FR")} secondes` }));
  if (resultat.resume) parent.append(creerElement("p", { texte: resultat.resume }));
  if (resultat.condition) parent.append(creerElement("p", { texte: `Condition : ${resultat.condition}` }));
}

function strategieTemps(s) {
  const t = s.timing; if (!t || !t.fiable || t.pause !== null) return {};
  const elapsed = ((t.fin ?? performance.now()) - t.debut) / 1000, pauses = t.pauses / 1000;
  return Number.isFinite(elapsed) && elapsed >= pauses && pauses >= 0 ? { duree_active_secondes: t.active / 1000, duree_ecoulee_secondes: elapsed, pauses_secondes: pauses, attente_interface_secondes: Math.max(0, elapsed - t.active / 1000 - pauses) } : {};
}
function strategieCorrection(parent, correction) {
  if (!correction) return;
  const labels = { plan_initial_compatible: "Plan initial compatible", plan_final_compatible: "Plan final compatible", execution_compatible: "Actions réalisées dans un ordre compatible", action_exacte: "Action demandée réalisée", heure_exacte: "Créneau demandé choisi", quoi: "Quoi faire", quand: "Quand", action: "Action au signal" };
  Object.entries(labels).forEach(([key, label]) => { if (correction[key] !== undefined) parent.append(creerElement("p", { texte: `${label} : ${typeof correction[key] === "boolean" ? (correction[key] ? "oui" : "non") : ({ exacte: "exacte", prematuree: "réalisée avant le signal", incorrecte: "incorrecte", occasion_terminee_sans_action: "occasion terminée sans action", exact: "exact", absence: "absence de réponse", a_verifier: "à vérifier", confusion: "autre information" }[correction[key]] || correction[key])}` })); });
  if (typeof correction.attendu === "string") parent.append(creerElement("p", { texte: `Pièce demandée : ${(strategieSession.scenario.pieces || []).find(p => p.id === correction.attendu)?.texte || correction.attendu}.` }));
  if (correction.attendu?.quoi) parent.append(creerElement("p", { texte: `Demande : ${correction.attendu.quoi}, ${correction.attendu.quand}.` }));
  if (correction.classement) Object.entries(correction.classement).forEach(([id, ok]) => parent.append(creerElement("p", { texte: `${(strategieSession.scenario.documents || []).find(doc => doc.id === id)?.texte || id} : classement ${ok ? "exact" : "à revoir"}.` })));
}
document.addEventListener("visibilitychange", () => {
  const s = strategieSession; if (!s || !document.hidden || s.phase === "correction") return;
  CAPACITES.arreter(); if (s.timing) s.timing.fiable = false;
  if (!s.busy && !s.pending && !s.paused) strategieEtape("pause");
});
