"use strict";

function immediateSpokenDigits(text) {
  const digits = { zero: "0", un: "1", une: "1", deux: "2", trois: "3", quatre: "4", cinq: "5", six: "6", sept: "7", huit: "8", neuf: "9" };
  const tokens = String(text).normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[.,;:!?-]/g, " ").trim().split(/\s+/);
  if (!tokens[0]) return "";
  if (tokens.some(token => !/^[0-9]+$/.test(token) && !(token in digits))) return null;
  return tokens.map(token => digits[token] ?? token).join("");
}

function renderImmediateSequence({ root, trial, wait, now, emit, onAnswer, onIncident }) {
  let destroyed = false, answered = false, firstAction = false, utterance = null, rejectSpeech = null;
  let dictation = null;
  const stopDictation = () => { dictation?.abort(); dictation = null; };
  const path = trial.parcours === "chemin";
  const params = trial.parametres;
  const el = (tag, text = "", className = "") => {
    const node = document.createElement(tag);
    node.textContent = text;
    node.className = className;
    return node;
  };
  const button = (text, handler, primary = false) => {
    const node = el("button", text, `bouton ${primary ? "bouton-primaire" : "bouton-secondaire"}`);
    node.type = "button";
    node.addEventListener("click", handler);
    return node;
  };
  const phase = name => { root.replaceChildren(); emit("phase", { phase: name }); };
  const action = modality => {
    if (!firstAction) { firstAction = true; emit("premiere_action", { modalite: modality }); }
  };
  const answer = async (response, modality, absence = false) => {
    if (answered || destroyed) return;
    answered = true; stopDictation();
    root.querySelectorAll("button,input").forEach(node => { node.disabled = true; });
    await onAnswer({ response, modality, ...(absence ? { absence: true } : {}) });
  };
  const positionLabel = position => position.nom || position.label ||
    `${position.y < 0.34 ? "En haut" : position.y > 0.66 ? "En bas" : "Au milieu"}, ${position.x < 0.34 ? "à gauche" : position.x > 0.66 ? "à droite" : "au centre"}`;
  function board(interactive = false, select = () => {}) {
    const area = el("div", "", "immediate-path");
    const cells = trial.stimulus.positions.map(position => {
      const cell = el(interactive ? "button" : "div", "", "immediate-path-cell");
      cell.style.left = `${position.x * 100}%`;
      cell.style.top = `${position.y * 100}%`;
      if (interactive) {
        cell.type = "button";
        cell.setAttribute("aria-label", positionLabel(position));
        let pointer = "souris";
        cell.addEventListener("click", event => select(position.id, event.detail === 0 ? "clavier" : pointer));
        cell.addEventListener("pointerdown", event => { pointer = event.pointerType === "touch" ? "tactile" : "souris"; });
        cell.addEventListener("keydown", event => {
          if (event.repeat && (event.key === "Enter" || event.key === " ")) { event.preventDefault(); return; }
          const direction = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[event.key];
          if (!direction) return;
          event.preventDefault();
          const options = trial.stimulus.positions.map((p, index) => ({ p, index,
            dx: p.x - position.x, dy: p.y - position.y }))
            .filter(p => p.dx * direction[0] + p.dy * direction[1] > 0)
            .sort((a, b) => (a.dx ** 2 + a.dy ** 2) - (b.dx ** 2 + b.dy ** 2));
          if (options.length) cells[options[0].index].focus();
        });
      } else cell.setAttribute("aria-hidden", "true");
      area.append(cell);
      return cell;
    });
    root.append(area);
    cells.area = area;
    return cells;
  }
  function codeResponse() {
    let modality = "clavier", generation = 0;
    const form = el("form", "", "immediate-code-response");
    const label = el("label", "Le code, dans le même ordre");
    const input = el("input");
    input.type = "text";
    input.value = "";
    input.inputMode = "numeric";
    input.autocomplete = "off";
    input.maxLength = 32;
    input.setAttribute("aria-label", "Le code, dans le même ordre");
    input.addEventListener("input", () => { generation++; stopDictation(); modality = "clavier"; action("clavier"); error.replaceChildren(); error.textContent = ""; });
    label.append(input);
    const error = el("p");
    error.setAttribute("role", "status");
    const submit = button("Valider le code", () => {} , true);
    submit.type = "submit";
    form.addEventListener("submit", event => {
      event.preventDefault();
      const code = input.value.replace(/[\s-]/g, "");
      if (!/^[0-9]*$/.test(code)) {
        error.textContent = "Utilise uniquement des chiffres."; input.focus(); return;
      }
      action("clavier");
      if (code.length !== params.longueur) {
        error.textContent = code.length ? "Le code est incomplet ou sa longueur est différente." : "La saisie est vide.";
        error.replaceChildren(el("p", error.textContent), button("Corriger", () => { error.replaceChildren(); input.focus(); }),
          button("Confirmer cette réponse", () => answer(code || null, modality, !code), true));
      } else answer(code, modality);
    });
    const clear = button("Vider la saisie", () => { generation++; stopDictation(); modality = "clavier"; input.value = ""; error.replaceChildren(); error.textContent = ""; input.focus(); });
    form.append(label, el("p", "Si tu hésites, suis ton intuition. Tu peux aussi laisser la saisie vide.", "indice"), error, clear, submit);
    if (params.modalite === "auditive" && typeof CAPACITES !== "undefined" && CAPACITES.voixDisponible?.()) {
      const voice = button("Répondre à voix haute", () => {
        if (dictation) { dictation.stop(); return; }
        CAPACITES.arreter();
        const token = ++generation, prefix = input.value.replace(/[\s-]/g, "");
        let finishing = false;
        const live = () => !destroyed && !answered && generation === token;
        const display = text => {
          if (!live()) return;
          const code = immediateSpokenDigits(text);
          if (code === null) { error.textContent = "Dis les chiffres un par un, de zéro à neuf, ou corrige la saisie."; return; }
          input.value = prefix + code; modality = "vocale"; action("vocale"); error.textContent = "";
        };
        voice.textContent = "Préparation de la dictée locale…";
        dictation = CAPACITES.dicter({
          onDebut: () => { if (live()) voice.textContent = "Parle maintenant · Terminer la dictée"; },
          onTraitement: () => { if (live()) voice.textContent = "Transcription locale…"; },
          onPartiel: text => {
            display(text);
            if (live() && !finishing && immediateSpokenDigits(text) !== null && input.value.length === params.longueur) {
              finishing = true; dictation?.stop();
            }
          }, onResultat: text => {
            if (!live()) return;
            const digits = immediateSpokenDigits(text);
            display(text);
            if (digits !== null && digits.length && input.value.length === params.longueur) {
              // Seule une transcription définitive complète déclenche la validation.
              const code = input.value;
              generation++; stopDictation();
              answer(code, "vocale");
            } else if (live()) input.focus();
          },
          onFin: () => { if (live()) { dictation = null; voice.textContent = "Répondre à voix haute"; } },
          onErreur: () => { if (live()) { stopDictation(); voice.textContent = "Répondre à voix haute"; error.textContent = "Dictée indisponible. Tu peux réessayer ou saisir le code."; } },
        });
        if (!dictation) voice.textContent = "Répondre à voix haute";
      });
      form.append(el("p", "Dis les chiffres un par un. Une réponse vocale complète est validée automatiquement.", "indice"), voice);
      // Le stimulus est terminé : ouvrir la même dictée locale que les champs libres.
      voice.click();
    }
    root.append(form);
    input.focus();
  }
  function pathResponse() {
    const response = [];
    let modality = "clavier";
    const update = () => {
      cells.forEach((cell, index) => {
        const id = trial.stimulus.positions[index].id;
        const ranks = response.flatMap((value, rank) => value === id ? [rank + 1] : []);
        cell.textContent = ranks.join(" · ");
        cell.setAttribute("aria-label", positionLabel(trial.stimulus.positions[index]) +
          (ranks.length ? ` ; votre choix ${ranks.join(", ")}` : ""));
      });
      links.replaceChildren();
      for (let i = 1; i < response.length; i++) {
        const from = trial.stimulus.positions.find(p => p.id === response[i - 1]);
        const to = trial.stimulus.positions.find(p => p.id === response[i]);
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        for (const [key, value] of Object.entries({ x1: from.x * 100, y1: from.y * 100, x2: to.x * 100, y2: to.y * 100 })) line.setAttribute(key, value);
        links.append(line);
      }
      status.textContent = `${response.length} choix sur ${params.longueur}.`;
      reset.disabled = !response.length;
      confirmation.replaceChildren();
    };
    const cells = board(true, (id, mode) => {
      if (answered) return;
      const previous = response.indexOf(id);
      if (previous >= 0) { response.splice(previous, 1); update(); return; }
      if (response.length >= params.longueur) return;
      modality = mode;
      action(mode);
      response.push(id);
      update();
    });
    const links = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    links.setAttribute("class", "immediate-path-links");
    links.setAttribute("viewBox", "0 0 100 100");
    links.setAttribute("preserveAspectRatio", "none");
    links.setAttribute("aria-hidden", "true");
    links.setAttribute("focusable", "false");
    cells.area.append(links);
    const status = el("p");
    status.setAttribute("role", "status");
    const reset = button("Vider les cases", () => { response.length = 0; update(); });
    const confirmation = el("div", "", "mi-controls");
    root.append(status, el("p", "Si tu hésites, suis ton intuition. Tu peux aussi laisser le chemin incomplet.", "indice"), reset,
      button("Valider le chemin", () => {
        if (response.length < params.longueur) {
          confirmation.replaceChildren(el("p", "Le chemin est incomplet."), button("Corriger", () => confirmation.replaceChildren()),
            button("Confirmer cette réponse", () => answer([...response], modality), true));
        } else answer([...response], modality);
      }, true), confirmation);
    update();
    cells[0].focus();
  }
  async function say(digit, voice) {
    await new Promise((resolve, reject) => {
      rejectSpeech = reject;
      const text = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf"][Number(digit)];
      if (typeof CAPACITES !== "undefined" && CAPACITES.lire) {
        const finish = () => { rejectSpeech = null; resolve(); };
        if (!CAPACITES.lire(text, { francais: true, onFin: finish, onErreur: () => { rejectSpeech = null; reject(new Error("Synthèse vocale interrompue")); } })) {
          rejectSpeech = null; reject(new Error("Voix indisponible"));
        }
        return;
      }
      utterance = new SpeechSynthesisUtterance(text);
      utterance.voice = voice;
      utterance.lang = voice.lang;
      utterance.onend = () => { rejectSpeech = null; resolve(); };
      utterance.onerror = () => { rejectSpeech = null; reject(new Error("Synthèse vocale interrompue")); };
      speechSynthesis.speak(utterance);
    });
  }
  async function present() {
    try {
      const auditory = !path && params.modalite === "auditive";
      const localVoices = auditory && typeof CAPACITES !== "undefined" && CAPACITES.voixLocales
        ? CAPACITES.voixLocales() : [];
      const voice = auditory ? localVoices.find(v => v.voiceURI === CAPACITES.choixVoix?.()) || localVoices.find(v => v.native) || localVoices.find(v => v.default) || localVoices[0]
        || (typeof speechSynthesis !== "undefined" ? speechSynthesis.getVoices().find(v => v.localService && /^fr\b/i.test(v.lang)) : null) : null;
      if (auditory && !voice) {
        onIncident("audio_indisponible");
        root.replaceChildren(el("p", "La voix française locale est indisponible. Choisissez un autre essai en mode visuel."));
        return;
      }
      if (voice) emit("voix", { voix: voice.voiceURI });
      phase("exposition");
      const cells = path ? board() : null;
      const display = !path ? el("div", auditory ? "Écoutez le code." : "", "immediate-code") : null;
      if (display) root.append(display);
      const sequence = path ? trial.stimulus.trajet : trial.stimulus.chiffres;
      for (let i = 0; i < sequence.length; i++) {
        if (destroyed) return;
        const cell = path ? cells[trial.stimulus.positions.findIndex(p => p.id === sequence[i])] : null;
        emit("signal_debut", { index: i, temps_ms: now() });
        if (auditory) await say(sequence[i], voice);
        else {
          if (cell) cell.classList.add("is-stimulus");
          else display.textContent = sequence[i];
          await wait(params.signal_ms);
        }
        if (destroyed) return;
        if (cell) cell.classList.remove("is-stimulus");
        if (display && !auditory) display.textContent = "";
        emit("signal_fin", { index: i, temps_ms: now() });
        if (i < sequence.length - 1) await wait(params.intervalle_ms);
      }
      phase("masque");
      await wait(params.masque_ms || 0);
      if (destroyed) return;
      phase("reponse");
      if (path) pathResponse(); else codeResponse();
    } catch (error) {
      if (!destroyed && error.name !== "AbortError") onIncident("presentation_interrompue");
    }
  }
  function destroy() {
    destroyed = true; stopDictation();
    if (params.modalite === "auditive" && typeof CAPACITES !== "undefined") { CAPACITES.arreter(); rejectSpeech?.(new DOMException("Interrompu", "AbortError")); rejectSpeech = null; }
    if (utterance) {
      utterance.onend = utterance.onerror = null;
      speechSynthesis.cancel();
      rejectSpeech?.(new DOMException("Interrompu", "AbortError"));
    }
    root.replaceChildren();
  }
  return { present, destroy };
}
