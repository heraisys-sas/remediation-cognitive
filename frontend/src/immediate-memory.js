"use strict";

const IMMEDIATE_NAMES = { code: "Retenir un code", chemin: "Refaire le chemin", changement: "Qu’est-ce qui a changé ?", objets: "Quel objet était où ?" };
const IMMEDIATE_INSTRUCTIONS = {
  code: "Retiens ce code. Quand il aura disparu, écris les chiffres dans le même ordre.",
  chemin: "Regarde les cases indiquées. Refais le même chemin, dans le même ordre.",
  changement: "Retiens les formes, puis indique si une forme a changé.",
  objets: "Retiens où se trouve chaque objet. Ensuite, replace les objets dans les cases vides.",
};
let immediateBlock = null;

function immediateDefaults(kind) {
  return { longueur: kind === "code" ? 4 : 3, modalite: "visuelle", condition: "forme", exposition_ms: kind === "objets" ? 6000 : 5000,
    signal_ms: kind === "code" ? 2000 : 1500, intervalle_ms: kind === "code" ? 1000 : 500,
    masque_ms: kind === "changement" ? 1500 : kind === "objets" ? 1000 : 0 };
}

function immediateParameters(kind) {
  const params = immediateDefaults(kind);
  for (const key of ["modalite", "condition"]) params[key] = preferenceLocale(`orthogone.mi.${kind}.${key}`, params[key]);
  if (kind !== "code") params.modalite = "visuelle";
  if (modeDerogatoireActif()) for (const key of ["longueur", "signal_ms", "intervalle_ms", "exposition_ms", "masque_ms"]) {
    const saved = preferenceLocale(`orthogone.mi.${kind}.${key}`);
    if (saved !== "") params[key] = Number(saved);
  }
  return params;
}

function immediateButton(text, callback, primary = false) {
  const button = creerElement("button", { texte: text, classe: `bouton ${primary ? "bouton-primaire" : "bouton-secondaire"}`, attributs: { type: "button" } });
  button.addEventListener("click", callback);
  return button;
}

function carteMemoiresImmediates() {
  const card = creerElement("article", { classe: "carte-theme" }, creerElement("h3", { texte: "Mémoires immédiates" }),
    creerElement("p", { texte: "Retenir un code, un chemin, des détails visuels ou la place des objets." }));
  card.dataset.activite = "memoires-immediates";
  const choices = creerElement("details", { classe: "choix-parcours" }, creerElement("summary", { texte: "Choisir le parcours" }));
  const select = creerElement("select", { classe: "selecteur-palier", attributs: { "aria-label": "Parcours pour Mémoires immédiates" } });
  for (const [id, name] of Object.entries(IMMEDIATE_NAMES)) select.append(creerElement("option", { texte: name, attributs: { value: id } }));
  select.value = preferenceLocale("orthogone.mi.parcours", "code");
  if (!IMMEDIATE_NAMES[select.value]) select.value = "code";
  const variants = creerElement("div");
  const overrides = creerElement("details", { classe: "reglages-essai" }, creerElement("summary", { texte: "Réglages de cette séance" }));
  function field(key, title, values, parent) {
    const input = creerElement("select", { classe: "selecteur-palier", attributs: { "aria-label": title } });
    for (const [value, label] of values) input.append(creerElement("option", { texte: label, attributs: { value: String(value) } }));
    input.value = String(immediateParameters(select.value)[key]);
    input.addEventListener("change", () => garderPreference(`orthogone.mi.${select.value}.${key}`, input.value));
    parent.append(creerElement("label", { texte: title }, input));
  }
  function update() {
    variants.replaceChildren();
    overrides.replaceChildren(creerElement("summary", { texte: "Réglages de cette séance" }));
    const kind = select.value;
    if (kind === "code") field("modalite", "Présentation du code", [["visuelle", "Chiffres vus"], ["auditive", "Chiffres entendus — voix locale"]], variants);
    if (kind === "changement") field("condition", "Détail à retenir", [["forme", "Formes"], ["couleur", "Couleurs"], ["association", "Associations forme–couleur"]], variants);
    const max = kind === "objets" ? 6 : kind === "changement" ? 5 : kind === "code" ? 12 : 9;
    field("longueur", kind === "code" ? "Nombre de chiffres" : kind === "chemin" ? "Longueur du chemin" : "Nombre d’éléments", Array.from({ length: max - 1 }, (_, i) => [i + 2, String(i + 2)]), overrides);
    if (["code", "chemin"].includes(kind)) {
      field("signal_ms", "Durée de chaque présentation", [[1000, "1 s"], [1500, "1,5 s"], [2000, "2 s"], [3000, "3 s"]], overrides);
      field("intervalle_ms", "Intervalle entre éléments", [[500, "0,5 s"], [1000, "1 s"], [1500, "1,5 s"]], overrides);
    } else field("exposition_ms", "Temps pour regarder", [[5000, "5 s"], [6000, "6 s"], [8000, "8 s"], [10000, "10 s"]], overrides);
    field("masque_ms", "Temps de masquage", [[0, "Sans attente supplémentaire"], [1000, "1 s"], [1500, "1,5 s"], [2000, "2 s"]], overrides);
    overrides.hidden = !modeDerogatoireActif();
  }
  select.addEventListener("change", () => { garderPreference("orthogone.mi.parcours", select.value); update(); });
  choices.append(select, variants);
  update();
  card.append(choices, overrides, immediateButton("Commencer", () => demarrerMemoiresImmediates(select.value), true));
  return card;
}

async function immediateApi(path, body) {
  return fetchJson("/api/memoires-immediates", path, { method: "POST", ...(body === undefined ? {} : { body: JSON.stringify(body) }) });
}

async function demarrerMemoiresImmediates(kind) {
  if (etat.actionEnCours) return;
  etat.actionEnCours = true;
  try {
    // Attendre les voix natives avant la consigne : éviter un repli navigateur au démarrage.
    await CAPACITES.chargerVoixLocales?.();
    const settings = immediateParameters(kind);
    const progression = !(modeDerogatoireActif() && ["longueur", "signal_ms", "intervalle_ms", "exposition_ms", "masque_ms"].some(key => preferenceLocale(`orthogone.mi.${kind}.${key}`, "") !== ""));
    const parametres = progression ? { modalite: settings.modalite, condition: settings.condition } : settings;
    const data = await immediateApi("/sessions", { parcours: kind, parametres, progression, sans_limite_sessions: sansLimiteActivee() });
    annulerMemo();
    immediateBlock = { ...data, trial: data.essai, next: null, renderer: null, controller: null,
      phase: "pret", facts: {}, times: {}, pending: false, assistee: false, example: false, correction: null };
    $("titre-memoires-immediates").textContent = IMMEDIATE_NAMES[kind];
    afficherVue("immediates");
    immediateReady();
  } catch (error) {
    afficherBandeau(error.status === 429 ? "Trois séances déjà commencées aujourd’hui. Tu peux reprendre un autre jour." : "Impossible de commencer pour le moment.",
      error.status === 429 ? {} : { reessayer: () => demarrerMemoiresImmediates(kind) });
  } finally { etat.actionEnCours = false; }
}

function immediateInstruction() {
  const b = immediateBlock;
  if (b.parcours === "objets") {
    const seconds = (b.parametres.exposition_ms / 1000).toLocaleString("fr-FR");
    return `Les objets apparaissent pendant ${seconds} secondes seulement. Retiens où se trouve chaque objet. Ensuite, replace-les dans les cases vides.`;
  }
  if (b.parcours === "chemin") {
    const seconds = (b.parametres.signal_ms / 1000).toLocaleString("fr-FR");
    return `Chaque case s’allume pendant ${seconds} seconde${b.parametres.signal_ms > 1000 ? "s" : ""}. Retiens le chemin, puis sélectionne les cases dans le même ordre.`;
  }
  if (b.parcours === "code") {
    const seconds = (b.parametres.signal_ms / 1000).toLocaleString("fr-FR");
    return b.parametres.modalite === "auditive"
      ? `Écoute les chiffres, puis écris le code dans le même ordre. Chaque chiffre est lu une fois.${b.parametres.repetitions ? " Un chiffre peut revenir dans le code." : ""}`
      : `Chaque chiffre apparaît pendant ${seconds} secondes seulement. Retiens le code, puis écris-le dans le même ordre.${b.parametres.repetitions ? " Un chiffre peut revenir dans le code." : ""}`;
  }
  if (b.parcours !== "changement") return IMMEDIATE_INSTRUCTIONS[b.parcours];
  const duration = `La première image apparaît pendant ${(b.parametres.exposition_ms / 1000).toLocaleString("fr-FR")} secondes seulement. `;
  return duration + (b.parametres.condition === "couleur" ? "Retiens les couleurs, puis indique si une couleur a changé."
    : b.parametres.condition === "association" ? "Retiens la couleur de chaque forme, puis indique si les associations ont changé. Si elles ont changé, retrouve les deux formes concernées." : IMMEDIATE_INSTRUCTIONS.changement);
}

function immediateStop() {
  clearTimeout(immediateBlock?.countdownTimer);
  immediateBlock?.controller?.abort();
  immediateBlock?.renderer?.destroy();
  if (immediateBlock) { immediateBlock.renderer = null; immediateBlock.controller = null; }
  CAPACITES.arreter();
}

function immediateReady(note = "") {
  const b = immediateBlock;
  immediateStop();
  b.phase = "pret";
  b.facts = {}; b.times = {};
  $("mi-progression").textContent = b.example ? "Exemple — hors séance" : `${b.assistee ? "Avec aide · " : ""}Exercice ${b.trial.index} sur 4${b.progression ? ` · Palier ${b.progression.palier} sur ${b.progression.total}` : ""}`;
  const root = $("mi-contenu");
  root.replaceChildren(creerElement("p", { texte: note || immediateInstruction() }));
  if (b.parcours === "chemin") {
    const preview = creerElement("div", { classe: "immediate-path", attributs: { "aria-label": "Disposition des cases" } });
    for (const position of b.trial.stimulus.positions) {
      const cell = creerElement("div", { classe: "immediate-path-cell", attributs: { "aria-hidden": "true" } });
      cell.style.left = `${position.x * 100}%`; cell.style.top = `${position.y * 100}%`; preview.append(cell);
    }
    root.append(preview);
  }
  const commands = $("mi-commandes");
  commands.replaceChildren(immediateButton("Commencer", immediatePresent, true));
  if (b.trial.index === 1 && !b.assistee && !b.example) commands.append(immediateButton("Voir un exemple", immediateExample));
  // La consigne des objets est lue une seule fois ; le parcours visuel reste silencieux.
  const initialInstruction = !["objets", "chemin", "changement", "code"].includes(b.parcours) || !b.directiveLue;
  let readInstruction = null;
  if (initialInstruction) {
    const audio = immediateButton("Écouter", () => {
      if (audio.dataset.reading) { CAPACITES.arreter(); end(); }
      else readInstruction();
    });
    audio.className += " bouton-audio";
    const end = () => { audio.dataset.reading = ""; actualiserBoutonAudio(false, audio); };
    readInstruction = () => {
      audio.dataset.reading = "on";
      actualiserBoutonAudio(true, audio);
      if (!CAPACITES.lire(immediateInstruction(), { francais: true, onFin: end, onErreur: end })) end();
    };
    commands.append(audio);
  }
  commands.append(immediateButton("Terminer la séance", immediateFinish));
  if (["objets", "chemin", "changement", "code"].includes(b.parcours) && !b.directiveLue) {
    b.directiveLue = true;
    readInstruction();
  }
  if (["objets", "chemin", "changement", "code"].includes(b.parcours)) {
    const instruction = creerElement("article", { classe: "carte carte-enonce" });
    instruction.append(...root.childNodes);
    const audio = commands.querySelector(".bouton-audio");
    if (audio) {
      audio.className = "bouton bouton-discret bouton-audio";
      const line = creerElement("div", { classe: "ligne-audio" });
      line.append(audio); instruction.append(line);
    }
    root.replaceChildren(instruction);
    const actions = creerElement("div", { classe: "mi-start-actions" });
    const finish = creerElement("div", { classe: "pied-seance" });
    for (const button of [...commands.querySelectorAll("button")]) {
      if (button === audio) continue;
      if (button.textContent === "Terminer la séance") finish.append(button);
      else { button.className += " bouton-large"; actions.append(button); }
    }
    commands.replaceChildren(actions, finish);
  }
  commands.querySelector("button")?.focus();
  if (b.example && b.parcours === "changement") {
    root.append(creerElement("p", { texte: "Compare d’abord ces deux compositions pour vérifier que les formes et couleurs sont bien perceptibles. Ensuite, tu peux essayer avec masquage." }));
    immediateShowModel(root, b.trial, null);
  }
}

function immediateExample() {
  const b = immediateBlock;
  b.savedTrial = b.trial; b.example = true;
  const positions = [{ id: "0", x: .15, y: .2 }, { id: "1", x: .5, y: .12 }, { id: "2", x: .82, y: .3 }, { id: "3", x: .22, y: .72 }, { id: "4", x: .58, y: .6 }, { id: "5", x: .85, y: .82 }];
  const avant = [{ position: "0", forme: "cercle", couleur: "bleu" }, { position: "1", forme: "triangle", couleur: "ocre" }, { position: "2", forme: "carre", couleur: "rose" }];
  const apres = avant.map(e => ({ ...e }));
  if (b.parametres.condition === "association") [apres[0].couleur, apres[1].couleur] = [apres[1].couleur, apres[0].couleur];
  else if (b.parametres.condition === "couleur") apres[0].couleur = "vert";
  else apres[0].forme = "losange";
  b.trial = { id: "exemple", index: 0, stimulus: b.parcours === "code" ? { chiffres: ["0", "4", "7"] }
    : b.parcours === "chemin" ? { positions, trajet: ["0", "2", "4"] }
    : b.parcours === "changement" ? { avant, apres, palette: { bleu: "#668fc0", ocre: "#c39b54", rose: "#b87892", vert: "#6ca48e" } }
    : { positions: [{ id: "0", x: .2, y: .5 }, { id: "1", x: .5, y: .5 }, { id: "2", x: .8, y: .5 }], objets: [{ id: "cle", nom: "clé" }, { id: "tasse", nom: "tasse" }, { id: "livre", nom: "livre" }], modele: { cle: "1", tasse: "0", livre: "2" }, reserve: ["livre", "cle", "tasse"] } };
  immediateReady("Exemple : aucune réponse de cet exemple n’est enregistrée. Tu peux essayer les commandes avant la séance.");
}

function immediateEmit(type, detail = {}) {
  const b = immediateBlock, now = performance.now();
  if (type === "phase") {
    b.phase = detail.phase; b.times[detail.phase] = now;
    if (detail.phase === "masque") b.facts.exposition_ms = now - b.times.exposition;
    if (detail.phase === "reponse") {
      b.facts.masque_ms = now - b.times.masque;
      b.facts.delai_rappel_ms = now - b.times.masque;
    }
  } else if (type === "premiere_action" && b.times.first === undefined) {
    b.times.first = now; b.facts.latence_ms = now - b.times.reponse;
  } else if (type === "seconde_composition") b.facts.seconde_composition_ms = now - b.times.masque;
  else if (type === "voix") b.facts.voix = detail.voix;
  else if (type === "signal_debut") {
    b.times.signal = now;
    if (b.times.signalEnd !== undefined) b.facts[`intervalle_${detail.index - 1}_ms`] = now - b.times.signalEnd;
  } else if (type === "signal_fin") {
    b.facts[`signal_${detail.index}_ms`] = now - b.times.signal;
    b.times.signalEnd = now;
  }
}

function immediateFacts(modality, absence = false) {
  const b = immediateBlock, now = performance.now();
  const facts = { ...b.facts, modalite: modality || "non_renseignee", absence_declaree: absence };
  if (b.phase === "exposition") facts.exposition_ms = now - b.times.exposition;
  if (b.phase === "masque") facts.masque_ms = now - b.times.masque;
  if (b.times.first !== undefined) facts.saisie_ms = now - b.times.first;
  return facts;
}

async function immediatePresent() {
  const b = immediateBlock;
  if (b.pending || b.phase !== "pret") return;
  CAPACITES.arreter();
  b.controller = new AbortController();
  const signal = b.controller.signal;
  const wait = ms => new Promise((resolve, reject) => {
    if (signal.aborted) { reject(new DOMException("Interrompu", "AbortError")); return; }
    const timer = setTimeout(() => { signal.removeEventListener("abort", cancel); resolve(); }, ms);
    const cancel = () => { clearTimeout(timer); reject(new DOMException("Interrompu", "AbortError")); };
    signal.addEventListener("abort", cancel, { once: true });
  });
  const render = ["code", "chemin"].includes(b.parcours) ? renderImmediateSequence : renderImmediateVisual;
  b.renderer = render({ root: $("mi-contenu"), trial: { ...b.trial, parcours: b.parcours,
    parametres: b.example ? { ...b.parametres, longueur: 3 } : b.parametres, assistee: b.assistee }, wait, now: () => performance.now(), emit: immediateEmit,
    onAnswer: immediateAnswer, onIncident: reason => immediatePause(reason) });
  const commands = $("mi-commandes");
  commands.replaceChildren();
  if (!["objets", "chemin", "changement", "code"].includes(b.parcours)) commands.append(immediateButton("Mettre en pause", () => immediatePause("pause")));
  commands.append(immediateButton("Terminer la séance", immediateFinish));
  try { await b.renderer.present(); }
  catch (error) { if (error.name !== "AbortError") await immediatePause("presentation_interrompue"); }
}

async function immediateRequest(path, payload, success) {
  clearTimeout(immediateBlock?.countdownTimer);
  const b = immediateBlock;
  if (b.pending) return;
  b.pending = true;
  $("mi-commandes").querySelectorAll("button").forEach(button => { button.disabled = true; });
  try { const data = await immediateApi(`/sessions/${b.session_id}/${path}`, payload); b.pending = false; success(data); }
  catch {
    b.pending = false;
    $("mi-commandes").replaceChildren(creerElement("p", { texte: "La sauvegarde n’est pas confirmée. Réessaie avant de poursuivre.", attributs: { role: "status" } }), immediateButton("Réessayer", () => immediateRequest(path, payload, success), true));
  }
}

async function immediateAnswer(answer) {
  const b = immediateBlock;
  const facts = immediateFacts(answer.modality, answer.absence);
  immediateStop(); b.phase = "retour";
  if (b.example) {
    immediateExampleFeedback(answer.response);
    return;
  }
  await immediateRequest("reponses", { essai_id: b.trial.id, reponse: answer.absence ? null : answer.response, assistee: b.assistee, observations: facts }, data => {
    b.correction = data.correction; b.response = answer.response; b.next = data.essai_suivant;
    immediateFeedback();
  });
}

function immediateExampleFeedback(response) {
  const b = immediateBlock;
  const root = $("mi-contenu");
  root.replaceChildren(creerElement("p", { texte: "Voici le modèle de l’exemple. Compare-le à ta réponse, à ton rythme." }));
  immediateShowModel(root, b.trial, response);
  $("mi-commandes").replaceChildren(immediateButton("Continuer", () => {
    b.trial = b.savedTrial; b.savedTrial = null; b.example = false; immediateReady();
  }, true), immediateButton("Terminer la séance", immediateFinish));
}

function immediateShowModel(root, trial, response) {
  const b = immediateBlock, sample = trial.stimulus;
  if (b.parcours === "code") root.append(creerElement("p", { texte: `Code présenté : ${sample.chiffres.join(" ")}` }));
  else if (b.parcours === "chemin") {
    const board = creerElement("div", { classe: "immediate-path" });
    sample.positions.forEach(position => {
      const ranks = sample.trajet.flatMap((id, index) => id === position.id ? [index + 1] : []);
      const cell = creerElement("div", { classe: "immediate-path-cell", texte: ranks.join(" · ") });
      cell.style.left = `${position.x * 100}%`; cell.style.top = `${position.y * 100}%`; board.append(cell);
    }); root.append(creerElement("p", { texte: "Le chemin présenté, avec son ordre :" }), board);
  } else {
    const comparison = creerElement("div", { classe: "mi-model-comparison" });
    root.append(comparison);
    for (const [label, model] of b.parcours === "changement" ? [["Avant", "avant"], ["Après", "apres"]] : [["Modèle", "modele"], ["Ton placement", response || {}]]) {
      const area = creerElement("div"), group = creerElement("div", {}, creerElement("p", { texte: label }), area); comparison.append(group);
      renderImmediateVisualModel(area, { ...trial, parcours: b.parcours }, model);
    }
  }
}

function immediateFeedback() {
  const b = immediateBlock, c = b.correction, root = $("mi-contenu");
  root.replaceChildren(creerElement("p", { texte: c.absence_declaree ? "Absence de réponse déclarée." : c.exacte ? "Réponse exacte." : "Compare ta réponse au modèle." }));
  if (b.parcours === "code" && b.response !== null && b.response !== undefined) root.append(creerElement("p", { texte: `Ta réponse : ${b.response}` }));
  if (["code", "chemin"].includes(b.parcours) && !c.absence_declaree) root.append(creerElement("p", { texte: `${c.positions_exactes} position${c.positions_exactes > 1 ? "s" : ""} exacte${c.positions_exactes > 1 ? "s" : ""} sur ${c.longueur} ; ${c.elements_retrouves} élément${c.elements_retrouves > 1 ? "s" : ""} retrouvé${c.elements_retrouves > 1 ? "s" : ""}, indépendamment de l’ordre.` }));
  if (b.parcours === "objets" && !c.absence_declaree) root.append(creerElement("p", { texte: `${c.associations_exactes} association${c.associations_exactes > 1 ? "s" : ""} exacte${c.associations_exactes > 1 ? "s" : ""} sur ${c.nombre} ; ${c.associations_erronees} placement${c.associations_erronees > 1 ? "s" : ""} différent${c.associations_erronees > 1 ? "s" : ""} ; ${c.non_places} objet${c.non_places > 1 ? "s" : ""} non placé${c.non_places > 1 ? "s" : ""}.${c.permutation ? " Des objets ont été échangés." : ""}` }));
  if (b.parcours === "changement" && !c.absence_declaree) {
    const types = { detection: "Changement détecté", changement_manque: "Changement non détecté", fausse_alerte: "Différence déclarée sur des compositions identiques", rejet_correct: "Compositions identiques reconnues" };
    root.append(creerElement("p", { texte: types[c.type] }));
    if (c.localisation_exacte !== null) root.append(creerElement("p", { texte: c.localisation_exacte ? "Localisation exacte." : "Localisation différente du modèle." }));
    if (c.positions_modifiees.length) {
      const before = b.trial.stimulus.avant.filter(element => c.positions_modifiees.includes(element.position));
      const forms = { cercle: "cercle", carre: "carré", triangle: "triangle", losange: "losange", etoile: "étoile", croix: "croix" };
      const description = b.parametres.condition === "association"
        ? `${before.map(element => forms[element.forme]).join(" et ")} ont échangé leurs couleurs.`
        : before.map(element => { const after = b.trial.stimulus.apres.find(next => next.position === element.position); return b.parametres.condition === "couleur"
          ? `${forms[element.forme]} : ${element.couleur} → ${after.couleur}` : `${forms[element.forme]} → ${forms[after.forme]}`; }).join(" ; ");
      root.append(creerElement("p", { texte: description }));
    }
  }
  immediateShowModel(root, b.trial, b.response);
  if (b.assistee) root.append(creerElement("p", { texte: "Exercice après une nouvelle présentation et la correction. La première réponse est conservée." }));
  const commands = $("mi-commandes");
  commands.replaceChildren(immediateButton(b.next ? "Suivant" : "Voir le résumé", () => {
    if (!b.next) { immediateFinish(); return; }
    b.trial = b.next; b.assistee = false;
    if (["chemin", "objets", "changement", "code"].includes(b.parcours)) immediateCountdown(); else immediateReady();
  }, true));
  if (!b.assistee) commands.append(immediateButton("Revoir et essayer avec aide", () => immediateRequest("aide", { essai_id: b.trial.id }, data => { b.trial = data.essai; b.assistee = true; immediateReady("Cet exercice suit la correction et une nouvelle présentation. Il reste séparé de la première réponse."); })));
  commands.append(immediateButton("Terminer la séance", immediateFinish));
  commands.querySelector("button")?.focus();
  if (b.parcours === "code" && b.next) immediateCorrectionCountdown();
}

function immediateCorrectionCountdown() {
  const b = immediateBlock;
  clearTimeout(b.countdownTimer);
  b.phase = "attente_correction";
  const note = creerElement("p", { classe: "indice" });
  $("mi-contenu").append(note);
  const commands = $("mi-commandes");
  const paused = () => {
    clearTimeout(b.countdownTimer); b.phase = "retour"; note.textContent = "En pause.";
    commands.replaceChildren(immediateButton("Reprendre", () => immediateFeedback(), true), immediateButton("Terminer la séance", immediateFinish));
    commands.querySelector("button")?.focus();
  };
  b.pauseCorrection = paused;
  const pause = immediateButton("Mettre en pause", paused);
  commands.replaceChildren(pause, ...[...commands.querySelectorAll("button")].slice(1));
  let remaining = 3;
  const tick = () => {
    note.textContent = `Le prochain code commence dans ${remaining} seconde${remaining > 1 ? "s" : ""}.`;
    b.countdownTimer = setTimeout(() => {
      if (immediateBlock !== b || b.phase !== "attente_correction") return;
      if (--remaining === 0) {
        b.trial = b.next; b.assistee = false; b.phase = "pret";
        $("mi-progression").textContent = `Exercice ${b.trial.index} sur 4${b.progression ? ` · Palier ${b.progression.palier} sur ${b.progression.total}` : ""}`;
        immediatePresent();
      }
      else tick();
    }, 1000);
  };
  tick(); pause.focus();
}

function immediateCountdown() {
  const b = immediateBlock;
  immediateStop(); b.phase = "attente"; b.facts = {}; b.times = {};
  $("mi-progression").textContent = `Exercice ${b.trial.index} sur 4${b.progression ? ` · Palier ${b.progression.palier} sur ${b.progression.total}` : ""}`;
  const note = creerElement("p");
  $("mi-contenu").replaceChildren(note);
  $("mi-commandes").replaceChildren(immediateButton("Mettre en pause", () => immediatePause("pause")), immediateButton("Terminer la séance", immediateFinish));
  let remaining = 3;
  const tick = () => {
    if (immediateBlock !== b || b.phase !== "attente") return;
    note.textContent = `${b.parcours === "objets" ? "Les prochains objets apparaissent" : b.parcours === "changement" ? "La prochaine image apparaît" : b.parcours === "code" ? "Le prochain code commence" : "Le prochain chemin commence"} dans ${remaining} seconde${remaining > 1 ? "s" : ""}.`;
    b.countdownTimer = setTimeout(() => {
      if (immediateBlock !== b || b.phase !== "attente") return;
      if (--remaining === 0) { b.phase = "pret"; immediatePresent(); } else tick();
    }, 1000);
  };
  tick(); $("mi-commandes").querySelector("button")?.focus();
}

async function immediatePause(reason) {
  const b = immediateBlock;
  if (b?.phase === "attente_correction") { b.pauseCorrection(); return; }
  if (b?.phase === "attente") {
    immediateStop(); b.phase = "pause";
    $("mi-contenu").replaceChildren(creerElement("p", { texte: "En pause. Le prochain exercice commencera 3 secondes après la reprise." }));
    $("mi-commandes").replaceChildren(immediateButton("Reprendre", immediateCountdown, true), immediateButton("Terminer la séance", immediateFinish));
    $("mi-commandes").querySelector("button")?.focus(); return;
  }
  if (!b || b.pending || (!["exposition", "masque", "reponse"].includes(b.phase) && !(b.phase === "pret" && reason === "audio_indisponible"))) return;
  const phase = b.phase, facts = { ...immediateFacts(), raison: reason };
  immediateStop(); b.phase = "pause";
  if (b.example) { immediateReady("Exemple interrompu. Tu peux le recommencer."); return; }
  await immediateRequest("interruption", { essai_id: b.trial.id, phase, observations: facts, assistee: b.assistee }, data => {
    b.assistee = false;
    if (!data.essai) { b.phase = "pret"; immediateFinish(); return; }
    b.trial = data.essai; immediateReady("Exercice interrompu, sans résultat. Quand tu seras prêt, un nouvel exercice sera présenté.");
    if (reason === "audio_indisponible") $("mi-commandes").append(immediateButton("Choisir les chiffres vus", async () => { await immediateFinish(); garderPreference("orthogone.mi.code.modalite", "visuelle"); demarrerMemoiresImmediates("code"); }));
  });
}

async function immediateFinish() {
  const b = immediateBlock;
  if (!b || b.pending) return;
  if (["exposition", "masque", "reponse"].includes(b.phase)) { await immediatePause("sortie"); if (b.phase !== "pret") return; }
  immediateStop(); b.phase = "fin";
  await immediateRequest("fin", undefined, data => {
    const rows = data.observations.filter(row => row.premiere), root = $("mi-contenu");
    root.replaceChildren(creerElement("h3", { texte: "Séance terminée" }), creerElement("p", { texte: "Tu peux faire une pause maintenant." }));
    const details = creerElement("details", { classe: "details-resultats" }, creerElement("summary", { texte: "Voir les détails de la séance" }));
    root.append(details);
    details.append(creerElement("p", { texte: `${rows.length} réponse${rows.length > 1 ? "s" : ""} validée${rows.length > 1 ? "s" : ""} ; ${data.observations.filter(row => row.interruption).length} exercices initiaux interrompus, sans score ; ${data.observations.filter(row => row.aide?.interruption).length} exercices aidés interrompus.` }));
    rows.forEach(row => {
      const c = row.premiere.correction;
      if (["code", "chemin"].includes(b.parcours) && !c.absence_declaree) details.append(creerElement("p", { texte: `${c.positions_exactes} position${c.positions_exactes > 1 ? "s" : ""} exacte${c.positions_exactes > 1 ? "s" : ""} sur ${c.longueur} ; ${c.elements_retrouves} élément${c.elements_retrouves > 1 ? "s" : ""} retrouvé${c.elements_retrouves > 1 ? "s" : ""} sans tenir compte de l’ordre.` }));
      if (b.parcours === "objets" && !c.absence_declaree) details.append(creerElement("p", { texte: `${c.associations_exactes} association${c.associations_exactes > 1 ? "s" : ""} exacte${c.associations_exactes > 1 ? "s" : ""} sur ${c.nombre} ; ${c.associations_erronees} placement${c.associations_erronees > 1 ? "s" : ""} différent${c.associations_erronees > 1 ? "s" : ""} ; ${c.non_places} objet${c.non_places > 1 ? "s" : ""} non placé${c.non_places > 1 ? "s" : ""}.` }));
      details.append(creerElement("p", { texte: `Exercice ${row.index} : ${c.absence_declaree ? "absence déclarée" : c.exacte ? "réponse exacte" : "réponse différente"}${row.aide?.reponse_validee ? " · exercice avec aide conservé séparément" : ""}.` }));
    });
    if (b.parcours === "changement") {
      const count = type => rows.filter(row => row.premiere.correction.type === type).length;
      const different = count("detection") + count("changement_manque"), identical = count("rejet_correct") + count("fausse_alerte");
      const localized = rows.filter(row => row.premiere.correction.type === "detection" && row.premiere.correction.localisation_exacte !== null);
      details.append(creerElement("p", { texte: `${count("detection")} changements détectés sur ${different} exercices avec changement ; ${count("changement_manque")} changements non détectés.` }),
        creerElement("p", { texte: `${count("rejet_correct")} identiques reconnus sur ${identical} exercices sans changement ; ${count("fausse_alerte")} fausses alertes.` }),
        creerElement("p", { texte: `${localized.filter(row => row.premiere.correction.localisation_exacte).length} localisations exactes sur ${localized.length} changements détectés et localisés.` }));
    }
    details.append(creerElement("p", { classe: "ligne-discrete", texte: "Les résultats décrivent cette séance et ses conditions. Ils ne constituent pas un bilan." }));
    $("mi-commandes").replaceChildren(immediateButton("Retour à l’accueil", () => { immediateBlock = null; revenirAuxThemes(); }, true));
    $("mi-progression").textContent = "À ton rythme";
    $("mi-commandes").querySelector("button")?.focus();
  });
}

function initialiserMemoiresImmediates() {
  document.addEventListener("keydown", event => {
    if (event.key !== "Enter" || event.repeat || event.isComposing || event.defaultPrevented || event.ctrlKey || event.altKey || event.metaKey || event.shiftKey) return;
    const view = $("vue-memoires-immediates");
    if (view.hidden || immediateBlock?.pending) return;
    // Les champs et boutons déjà focalisés gardent leur activation native.
    if (event.target?.closest?.("input, textarea, select, button, a, summary, [contenteditable='true']")) return;
    const primary = [...view.querySelectorAll("button.bouton-primaire")].find(button => !button.disabled && button.getClientRects().length);
    if (primary) { event.preventDefault(); primary.click(); }
  });
  document.addEventListener("visibilitychange", () => { if (document.hidden) immediatePause("onglet_masque"); });
  let width = window.innerWidth;
  window.addEventListener("resize", () => {
    if (Math.abs(window.innerWidth - width) > 2) immediatePause("geometrie_modifiee");
    width = window.innerWidth;
  });
}
