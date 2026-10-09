"use strict";

function immediateVisualGlyph(kind, color = "currentColor") {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 80 80");
  svg.setAttribute("aria-hidden", "true");
  svg.setAttribute("focusable", "false");
  const paths = {
    triangle: "M40 8L73 69H7Z", carre: "M12 12H68V68H12Z", square: "M12 12H68V68H12Z",
    losange: "M40 5L75 40L40 75L5 40Z", diamond: "M40 5L75 40L40 75L5 40Z",
    etoile: "M40 5L49 29L75 30L54 46L62 72L40 57L18 72L26 46L5 30L31 29Z",
    croix: "M29 8H51V29H72V51H51V72H29V51H8V29H29Z",
    pomme: "M40 22Q17 8 11 34Q5 65 29 70Q40 75 50 70Q76 65 70 34Q64 8 40 22Z M40 22Q38 5 52 7L54 15Q44 15 40 22Z",
    cle: "M29 13A17 17 0 1 0 29 47L41 59H50V68H60V58L43 41A17 17 0 0 0 29 13Z M23 23A6 6 0 1 1 23 35A6 6 0 1 1 23 23Z",
    tasse: "M13 18H53V27H62Q75 27 75 41Q75 55 53 55Q50 67 33 67Q13 67 13 47Z M53 34V48Q67 48 67 41Q67 34 53 34Z",
    livre: "M9 15Q25 8 40 19Q55 8 71 15V65Q55 58 40 69Q25 58 9 65Z M40 19V69",
  };
  const shape = document.createElementNS("http://www.w3.org/2000/svg", paths[kind] ? "path" : "circle");
  if (paths[kind]) shape.setAttribute("d", paths[kind]);
  else { shape.setAttribute("cx", "40"); shape.setAttribute("cy", "40"); shape.setAttribute("r", "29"); }
  shape.setAttribute("fill", color);
  shape.setAttribute("fill-rule", "evenodd");
  if (kind === "livre") { shape.setAttribute("stroke", "currentColor"); shape.setAttribute("stroke-width", "2"); }
  svg.append(shape);
  return svg;
}

function renderImmediateVisualModel(root, trial, which = "avant") {
  const s = trial.stimulus;
  const board = creerElement("div", { classe: "mi-visual-board" });
  if (trial.parcours === "changement") {
    for (const [index, element] of s[which].entries()) {
      const cell = creerElement("div", { classe: "mi-visual-cell", attributs: { "aria-label": `Élément ${index + 1}` } });
      cell.append(immediateVisualGlyph(element.forme, s.palette[element.couleur] || element.couleur));
      board.append(cell);
    }
  } else {
    board.classList.add("mi-object-board");
    board.style.setProperty("--mi-object-count", s.positions.length);
    const placements = which === "modele" ? s.modele : which;
    for (const [index, position] of s.positions.entries()) {
      const cell = creerElement("div", { classe: "mi-object-slot", attributs: { "aria-label": `Emplacement ${index + 1}` } });
      cell.style.left = `${position.x * 100}%`; cell.style.top = `${position.y * 100}%`;
      const id = Object.keys(placements || {}).find(key => placements[key] === position.id);
      if (id) cell.append(immediateVisualGlyph(id));
      board.append(cell);
    }
  }
  root.replaceChildren(board);
  return board;
}

function renderImmediateVisual({ root, trial, wait, emit, onAnswer }) {
  const s = trial.stimulus;
  let destroyed = false, submitted = false, acted = false, modality = "souris";
  const action = event => {
    modality = event?.detail === 0 ? "clavier" : event?.pointerType === "touch" ? "tactile" : "souris";
    if (!acted) { acted = true; emit("premiere_action", { modalite: modality }); }
  };
  const button = (text, handler, primary = false) => {
    const node = creerElement("button", { texte: text, classe: `bouton ${primary ? "bouton-primaire" : "bouton-secondaire"}`, attributs: { type: "button" } });
    node.addEventListener("click", event => { if (!destroyed && !submitted) { action(event); handler(); } });
    return node;
  };
  async function submit(response, absence = false) {
    if (submitted || destroyed) return;
    submitted = true;
    root.querySelectorAll("button").forEach(node => { node.disabled = true; });
    try { await onAnswer({ response, modality, absence }); }
    catch (error) { if (!destroyed) { submitted = false; root.querySelectorAll("button").forEach(node => { node.disabled = false; }); } throw error; }
  }
  function changeResponse() {
    const board = renderImmediateVisualModel(root, trial, "apres");
    const controls = creerElement("div", { classe: "mi-controls" });
    const localisations = new Set();
    root.append(creerElement("p", { classe: "indice", texte: "Si tu hésites, suis ton intuition. Tu peux aussi laisser la localisation vide." }), controls);
    controls.append(button("Identique", () => { emit("decision", { decision: "identique" }); submit({ decision: "identique", localisation: [], localisation_absente: false }); }),
      button("Différent", () => {
        emit("decision", { decision: "different" });
        controls.replaceChildren(creerElement("p", { texte: trial.parametres.condition === "association" ? "Sélectionnez les deux éléments concernés." : "Sélectionnez l’élément concerné." }));
        board.replaceChildren();
        const count = trial.parametres.condition === "association" ? 2 : 1;
        const confirmation = creerElement("div", { classe: "mi-controls" });
        let validate, clear;
        for (const [index, element] of s.apres.entries()) {
          const cell = button("", () => {
            if (localisations.has(element.position)) localisations.delete(element.position);
            else if (localisations.size < count) localisations.add(element.position);
            cell.setAttribute("aria-pressed", String(localisations.has(element.position)));
            confirmation.replaceChildren();
            clear.disabled = !localisations.size;
          });
          cell.setAttribute("aria-label", `Élément ${index + 1}`);
          cell.classList.add("mi-visual-cell"); cell.setAttribute("aria-pressed", "false");
          cell.append(immediateVisualGlyph(element.forme, s.palette[element.couleur] || element.couleur)); board.append(cell);
        }
        const finish = () => submit({ decision: "different", localisation: [...localisations], localisation_absente: !localisations.size });
        validate = button("Valider la localisation", () => {
          if (localisations.size !== count) confirmation.replaceChildren(creerElement("p", { texte: "La localisation est incomplète." }), button("Corriger", () => confirmation.replaceChildren()), button("Confirmer cette réponse", finish, true));
          else finish();
        }, true);
        clear = button("Vider les cases", () => { localisations.clear(); board.querySelectorAll("button").forEach(cell => cell.setAttribute("aria-pressed", "false")); clear.disabled = true; confirmation.replaceChildren(); });
        clear.disabled = true;
        controls.append(clear, validate, confirmation);
        board.querySelector("button")?.focus();
      }));
  }
  function objectsResponse() {
    const placements = {};
    let selected = null;
    const workspace = creerElement("div"), controls = creerElement("div", { classe: "mi-controls" });
    root.replaceChildren(workspace, controls);
    function draw() {
      workspace.replaceChildren(); controls.replaceChildren();
      const board = creerElement("div", { classe: "mi-visual-board mi-object-board" });
      board.style.setProperty("--mi-object-count", s.positions.length);
      for (const [index, position] of s.positions.entries()) {
        const occupant = Object.keys(placements).find(id => placements[id] === position.id);
        const label = `Emplacement ${index + 1}${occupant ? ` : ${s.objets.find(o => o.id === occupant)?.nom || occupant}` : " : vide"}`;
        const cell = button("", () => {
          if (occupant) { delete placements[occupant]; selected = null; draw(); return; }
          if (!selected) return;
          placements[selected] = position.id; selected = null; draw();
        });
        cell.setAttribute("aria-label", label);
        cell.classList.add("mi-object-slot"); cell.style.left = `${position.x * 100}%`; cell.style.top = `${position.y * 100}%`;
        if (occupant) cell.append(immediateVisualGlyph(occupant)); board.append(cell);
      }
      const reserve = creerElement("div", { classe: "mi-object-reserve", attributs: { "aria-label": "Objets à placer" } });
      for (const id of s.reserve) {
        const object = s.objets.find(o => o.id === id);
        const cell = button(object?.nom || id, () => { selected = selected === id ? null : id; draw(); workspace.querySelector("button")?.focus(); });
        cell.disabled = Boolean(placements[id]);
        if (cell.disabled) { cell.classList.add("is-placed"); cell.setAttribute("aria-label", `${object?.nom || id}, déjà placé`); }
        cell.setAttribute("aria-pressed", String(selected === id)); cell.append(immediateVisualGlyph(id)); reserve.append(cell);
      }
      workspace.append(board, creerElement("p", { texte: selected ? "Choisissez un emplacement." : "Choisissez un objet, puis son emplacement." }), reserve, creerElement("p", { classe: "indice", texte: "Si tu hésites, suis ton intuition. Tu peux aussi laisser une case vide." }));
      const clear = button("Vider les cases", () => { Object.keys(placements).forEach(id => delete placements[id]); selected = null; draw(); });
      clear.disabled = !Object.keys(placements).length;
      controls.append(clear, button("Valider les placements", () => {
        if (Object.keys(placements).length < s.objets.length) {
          controls.replaceChildren(creerElement("p", { texte: "Un emplacement est vide." }), button("Corriger", draw), button("Confirmer cette réponse", () => submit({ ...placements }), true));
        } else submit({ ...placements });
      }, true));
      (selected ? board.querySelector("button") : [...reserve.querySelectorAll("button")].find(button => !button.disabled) || board.querySelector("button"))?.focus();
    }
    draw();
  }
  return {
    async present() {
      emit("phase", { phase: "exposition" });
      renderImmediateVisualModel(root, trial, trial.parcours === "changement" ? "avant" : "modele");
      await wait(trial.parametres.exposition_ms);
      if (destroyed) return;
      root.replaceChildren(creerElement("div", { classe: "mi-visual-mask", attributs: { "aria-label": "Temps de maintien" } })); emit("phase", { phase: "masque" });
      await wait(trial.parametres.masque_ms);
      if (destroyed) return;
      if (trial.parcours === "changement") emit("seconde_composition", {});
      emit("phase", { phase: "reponse" });
      if (trial.parcours === "changement") changeResponse(); else objectsResponse();
      root.querySelector("button")?.focus();
    },
    destroy() { destroyed = true; root.replaceChildren(); },
  };
}
