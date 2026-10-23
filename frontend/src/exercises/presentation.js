"use strict";

const BLANC_INTER_ITEM_MS = 2000;

function afficherPhaseMemo(item) {
  viderZonesReponse();
  const contenu = item.contenu || {};
  const affichage = contenu.affichage;
  const estSequence = affichage.mode === "sequence";
  const estSeries = affichage.mode === "series";
  const audio = affichage.modalite === "auditive";
  const parElement = (affichage.duree_par_item_ms + (affichage.pause_item_ms ?? BLANC_INTER_ITEM_MS)) / 1000;
  const nbElements = estSeries
    ? affichage.series.reduce((total, serie) => total + serie.length, 0)
    : affichage.elements.length;
  const mention = affichage.image ? `Une scène · ${Math.round(affichage.duree_totale_ms / 1000)} s` : audio ? `${nbElements} mots · 2 s de pause après chaque mot entendu` : estSequence || estSeries
    ? `${nbElements} éléments · un toutes les ${parElement.toFixed(2).replace(".", ",")} s`
    : `${affichage.elements.length} paires · environ ${Math.round(affichage.duree_totale_ms / 1000)} s`;

  // Consigne dans la carte énoncé ; le stimulus reste masqué jusqu'au signal
  // de l'utilisateur (set attentionnel : on sait quoi chercher avant de voir).
  // La consigne de méthode n'est affichée qu'UNE fois par type dans la séance :
  // ensuite une phrase courte suffit (la répétition serait rébarbative).
  const consigneComplete = String(contenu.consigne || "").trim();
  const cleConsigne = consigneComplete || (audio
    ? "Mémorise les mots entendus."
    : "Mémorise le contenu affiché.");
  const consigneDejaVue = etat.consignesMemoVues.has(cleConsigne);
  const consigneAffichee = (consigneComplete && !consigneDejaVue)
    ? consigneComplete
    : audio ? "Mémorise les mots entendus." : "Mémorise le contenu affiché.";
  etat.consignesMemoVues.add(cleConsigne);
  refs.enonce.textContent = consigneAffichee;
  refs.enonce.className = "enonce";
  // « Écouter » lit ce qui est affiché à ce stade : la consigne, pas la question.
  etat.enonceCourant = consigneAffichee;
  refs.ligneAudio.hidden = !CAPACITES.syntheseDisponible();
  refs.rappelConsigne.hidden = true;
  // Le texte reste visible à chaque item, mais une consigne identique n'est lue
  // automatiquement qu'à sa première occurrence dans la séance. Le bouton
  // « Écouter » reste disponible si la personne souhaite l'entendre à nouveau.
  if (!consigneDejaVue) lireSiLectureAuto(consigneAffichee);
  refs.zoneAide.hidden = true;
  refs.carteFeedback.hidden = true;
  refs.boutonSuivant.hidden = true;
  refs.formulaire.hidden = true;

  const boutonAfficher = creerElement("button", {
    classe: "bouton bouton-primaire bouton-large",
    texte: audio ? "Écouter la série" : "Afficher",
    attributs: { type: "button" },
  });
  boutonAfficher.addEventListener("click", () => jouerAffichage(item));
  if (audio && !affichage.audio && !CAPACITES.syntheseDisponible()) {
    boutonAfficher.disabled = true;
    refs.enonce.textContent = "La synthèse vocale est indisponible sur ce navigateur. Choisis le parcours Mots lus depuis l’accueil.";
  }
  refs.zoneMemo.replaceChildren(
    creerElement("div", { classe: "memo-actions" },
      boutonAfficher,
      creerElement("span", { classe: "memo-mention", texte: mention })
    )
  );
  refs.zoneMemo.hidden = false;
  reglerEtatBoutons();
  // Dans Au quotidien, Entrée déclenche l'action visible par le comportement natif du bouton.
  if (etat.theme?.id === "quotidien" && !boutonAfficher.disabled) boutonAfficher.focus();
}

function jouerAffichage(item) {
  CAPACITES.arreter();
  refs.ligneAudio.hidden = true;
  const affichage = item.contenu.affichage;
  const plateau = creerElement("div", { classe: "memo-plateau" });
  const indicateur = creerElement("p", { classe: "memo-points" });
  const boutonPasser = creerElement("button", {
    classe: "bouton bouton-secondaire",
    texte: "Passer",
    attributs: { type: "button" },
  });
  boutonPasser.addEventListener("click", () => afficherQuestion(item));
  refs.zoneMemo.replaceChildren(plateau, indicateur, boutonPasser);
  if (etat.theme?.id === "quotidien") boutonPasser.focus();

  if (affichage.modalite === "auditive") {
    jouerSeriesAudio(item, plateau, indicateur);
    return;
  }
  if (affichage.mode === "texte") {
    // Texte à lire (méthode PQRST) : affiché pendant la durée prévue, puis masqué.
    plateau.replaceChildren(
      creerElement("div", { classe: "memo-texte" },
        ...affichage.elements.map((paragraphe) => creerElement("p", { texte: paragraphe }))
      )
    );
    // Le stimulus devient « ce qui est affiché » : le bouton Écouter le relit à la
    // demande, et la lecture automatique le dit d'elle-même si elle est active.
    etat.enonceCourant = affichage.elements.join(". ");
    lireSiLectureAuto(etat.enonceCourant);
    etat.minuteriesMemo.push(
      setTimeout(() => jouerDelaiOuQuestion(item), affichage.duree_totale_ms)
    );
    return;
  }

  if (affichage.image) {
    const generation = etat.memoGeneration;
    const description = affichage.image;
    const image = creerElement("img", { classe: "scene-contexte", attributs: {
      width: description.width, height: description.height,
      alt: description.alt, decoding: "async",
      sizes: "(max-width: 640px) calc(100vw - 40px), 592px",
    } });
    const statut = creerElement("p", { classe: "ligne-discrete", texte: "Chargement de la scène…",
      attributs: { role: "status" } });
    plateau.replaceChildren(statut);
    const valide = () => generation === etat.memoGeneration && plateau.isConnected;
    let termine = false;
    const echec = () => {
      if (termine || !valide()) return;
      termine = true;
      const observation = observationContexte(item);
      if (observation) observation.incident_photo = true;
      clearTimeout(delaiChargement);
      statut.textContent = "La scène n’a pas pu être chargée. Tu peux réessayer ou terminer la séance.";
      const reessayer = creerElement("button", { classe: "bouton bouton-secondaire",
        texte: "Réessayer", attributs: { type: "button" } });
      reessayer.addEventListener("click", () => { annulerMemo(); refs.zoneMemo.hidden = false; jouerAffichage(item); });
      plateau.append(reessayer);
    };
    // Le rappel ne démarre jamais sans avoir effectivement montré la scène.
    boutonPasser.hidden = true;
    const delaiChargement = setTimeout(echec, 15000);
    etat.minuteriesMemo.push(delaiChargement);
    image.onerror = echec;
    image.onload = async () => {
      try { await image.decode(); } catch { echec(); return; }
      if (termine || !valide()) return;
      termine = true;
      clearTimeout(delaiChargement);
      // Une transcription du message reste lisible sur petit écran, sans nommer la source.
      const figure = creerElement("figure", { classe: "scene-source" }, image,
        creerElement("figcaption", { texte: description.alt, attributs: { "aria-hidden": "true" } }));
      plateau.replaceChildren(figure);
      const observation = observationContexte(item);
      if (observation) { observation.exposition_ms = Date.now(); observation.photo_chargee = true; }
      boutonPasser.hidden = false;
      // L’alternative et la voix donnent le message, jamais le contexte attendu.
      etat.enonceCourant = description.alt;
      lireSiLectureAuto(etat.enonceCourant);
      etat.minuteriesMemo.push(setTimeout(() => jouerDelaiOuQuestion(item), affichage.duree_totale_ms));
    };
    image.srcset = description.srcset;
    image.src = description.src;
    return;
  }

  if (affichage.mode === "liste") {
    const liste = creerElement("ul", { classe: "memo-liste" });
    for (const [gauche, droite] of affichage.elements) {
      liste.append(
        creerElement("li", { classe: "memo-paire" },
          creerElement("span", { texte: gauche }),
          creerElement("span", { texte: droite })
        )
      );
    }
    plateau.append(liste);
    // Le stimulus (paires, fiche) devient « ce qui est affiché ».
    etat.enonceCourant = affichage.elements
      .map(([gauche, droite]) => (droite ? `${gauche} : ${droite}` : gauche))
      .join(". ");
    lireSiLectureAuto(etat.enonceCourant);
    etat.minuteriesMemo.push(
      setTimeout(() => jouerDelaiOuQuestion(item), affichage.duree_totale_ms)
    );
    return;
  }

  // Séquence de chiffres/mots/lettres ou séries de mots : un élément à la fois,
  // suivi d'un blanc de deux secondes avant le suivant.
  const groupes = affichage.mode === "series" ? affichage.series : [affichage.elements];
  const blancMemoMs = affichage.pause_item_ms ?? BLANC_INTER_ITEM_MS;
  let delai = 0;
  groupes.forEach((groupe, indexGroupe) => {
    groupe.forEach((element, index) => {
      etat.minuteriesMemo.push(setTimeout(() => {
        if (affichage.mode === "series" && index === 0) {
          plateau.append(creerElement("p", {
            classe: "memo-serie-titre",
            texte: `Série ${indexGroupe + 1} / ${groupes.length}`,
          }));
        }
        plateau.append(creerElement("span", { classe: "memo-element", texte: element }));
        indicateur.textContent = affichage.mode === "series"
          ? `Série ${indexGroupe + 1} / ${groupes.length}`
          : `${index + 1} / ${groupe.length}`;
      }, delai));
      delai += affichage.duree_par_item_ms;
      if (index < groupe.length - 1) {
        etat.minuteriesMemo.push(setTimeout(() => {
          for (const noeud of plateau.querySelectorAll(".memo-element")) noeud.remove();
        }, delai));
        delai += blancMemoMs;
      }
    });
    if (indexGroupe < groupes.length - 1) {
      etat.minuteriesMemo.push(setTimeout(() => { plateau.replaceChildren(); }, delai));
      delai += Number(affichage.pause_serie_ms || 1500);
    }
  });
  if (affichage.pause_item_ms) {
    etat.minuteriesMemo.push(setTimeout(() => plateau.replaceChildren(), delai));
    delai += affichage.pause_item_ms;
  }
  etat.minuteriesMemo.push(setTimeout(() => jouerDelaiOuQuestion(item), delai));
}

function jouerSeriesAudio(item, plateau, indicateur) {
  const generation = etat.memoGeneration;
  const a = item.contenu.affichage;
  const mots = a.series.flatMap((serie, groupe) => serie.map((mot, index) => ({
    mot, groupe, dernier: index === serie.length - 1,
  })));
  const actif = () => generation === etat.memoGeneration;
  function jouer(index) {
    if (!actif()) return;
    if (index === mots.length) { jouerDelaiOuQuestion(item); return; }
    const { mot, groupe, dernier } = mots[index];
    plateau.textContent = "Écoute…";
    indicateur.textContent = `Série ${groupe + 1} / ${a.series.length}`;
    let termine = false;
    function erreur() {
      if (!actif() || termine) return;
      termine = true;
      CAPACITES.arreter();
      plateau.textContent = "Lecture interrompue. Tu peux réécouter la série depuis le début.";
      const reprendre = creerElement("button", { texte: "Réécouter depuis le début",
        classe: "bouton bouton-secondaire", attributs: { type: "button" } });
      reprendre.addEventListener("click", () => { annulerMemo(); afficherPhaseMemo(item); });
      plateau.append(reprendre);
    }
    const lireMot = a.audio?.[mot] ? CAPACITES.lireFichier : CAPACITES.lire;
    const disponible = lireMot(a.audio?.[mot] || mot, {
      onFin() {
        if (!actif() || termine) return;
        termine = true;
        plateau.textContent = "…";
        const pause = dernier && index < mots.length - 1 ? a.pause_serie_ms : a.pause_item_ms;
        etat.minuteriesMemo.push(setTimeout(() => jouer(index + 1), pause));
      },
      onErreur: erreur,
    });
    if (!disponible) erreur();
    // Un moteur muet ne doit pas laisser la séance bloquée indéfiniment.
    etat.minuteriesMemo.push(setTimeout(erreur, 15000));
  }
  jouer(0);
}

function jouerDelaiOuQuestion(item) {
  const delai = Number((item.contenu && item.contenu.delai_s) || 0);
  if (!delai) {
    afficherQuestion(item);
    return;
  }
  // Rappel différé : l'attente est affichée, pas cachée — et l'utilisateur
  // peut toujours passer (aucune contrainte de temps imposée).
  const restant = creerElement("p", { classe: "memo-attente" });
  const boutonPasser = creerElement("button", {
    classe: "bouton bouton-secondaire",
    texte: "Passer l'attente",
    attributs: { type: "button" },
  });
  boutonPasser.addEventListener("click", () => afficherQuestion(item));
  let secondes = Math.round(delai);
  const majTexte = () => { restant.textContent = `Encore ${secondes} s avant la question…`; };
  majTexte();
  refs.zoneMemo.replaceChildren(restant, boutonPasser);
  refs.zoneMemo.hidden = false;
  const intervalle = setInterval(() => {
    secondes -= 1;
    majTexte();
    if (secondes <= 0) afficherQuestion(item);
  }, 1000);
  etat.minuteriesMemo.push(intervalle);
}
