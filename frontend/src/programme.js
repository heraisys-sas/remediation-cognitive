"use strict";

const LIBELLES_REGLES = {
  progression: "Progression",
  fatigue: "Fatigue",
  jours_manques: "Journée manquée",
  alternance: "Alternance",
  duree: "Durée",
  recul: "Recul",
};

async function ouvrirProgramme() {
  refs.planJour.replaceChildren(creerElement("p", { classe: "ligne-discrete", texte: "Chargement…" }));
  refs.semainesProgramme.replaceChildren();
  refs.reglesProgramme.replaceChildren();
  afficherVue("programme");
  try {
    const [donnees, themes] = await Promise.all([
      fetchJson(API_PROGRAMME, ""),
      apiFetch("/themes"),
    ]);
    etat.themesParId = new Map((themes.themes || []).map((theme) => [theme.id, theme]));
    rendrePlanJour(donnees.aujourd_hui || {});
    rendreSemaines(donnees.programme || {});
    rendreRegles(donnees.regles || {});
    masquerBandeau();
  } catch {
    refs.planJour.replaceChildren();
    afficherBandeau("Le programme n’a pas pu être chargé pour le moment.", { retour: true });
  }
}

function rendrePlanJour(jour) {
  refs.planJour.replaceChildren();
  if (jour.type === "termine") {
    refs.planJour.append(
      creerElement("h3", { texte: "Programme terminé" }),
      creerElement("p", { texte: "Les huit semaines sont passées. Tu peux reprendre le programme quand tu veux, ou continuer librement." })
    );
    return;
  }
  if (jour.type === "a_venir") {
    refs.planJour.append(creerElement("p", { texte: "Le programme commencera à ta prochaine séance." }));
    return;
  }

  const type = jour.type === "repos"
    ? "Jour de repos"
    : jour.type === "legere" ? "Journée légère" : "Séance du jour";
  refs.planJour.append(
    creerElement("h3", { texte: `Semaine ${jour.semaine} · jour ${jour.jour}` }),
    creerElement("p", { classe: "jour-type", texte: `${type} — ${jour.duree_min} minutes` })
  );
  if (jour.type === "repos") {
    refs.planJour.append(
      creerElement("p", { texte: "Rien à faire aujourd’hui : le repos fait partie du programme." })
    );
    return;
  }

  const themes = jour.themes || [];
  if (themes.includes("au-choix")) {
    refs.planJour.append(
      creerElement("p", { texte: "Choisis ce qui te tente aujourd’hui — les thèmes Extra sont aussi possibles." })
    );
  }
  const plafonds = jour.plafond_palier || {};
  for (const identifiant of themes) {
    const theme = etat.themesParId.get(identifiant);
    if (!theme) continue;
    const plafond = plafonds[identifiant];
    let parcours = theme.parcours?.[0]?.id || null;
    const selecteurParcours = theme.parcours?.length > 1
      ? creerElement("select", { classe: "selecteur-palier",
          attributs: { "aria-label": `Parcours pour ${theme.nom}` } })
      : null;
    if (selecteurParcours) {
      for (const definition of theme.parcours) selecteurParcours.append(creerElement(
        "option", { texte: definition.nom, attributs: { value: definition.id } }
      ));
      selecteurParcours.addEventListener("change", () => { parcours = selecteurParcours.value; });
    }
    const bouton = creerElement("button", {
      classe: "bouton bouton-primaire",
      texte: "Commencer",
      attributs: { type: "button" },
    });
    bouton.addEventListener("click", () => demarrerSession(theme, null, parcours));
    refs.planJour.append(
      creerElement("div", { classe: "jour-theme" },
        creerElement("h4", { texte: theme.nom }),
        creerElement("p", {
          classe: "jour-detail",
          texte: `${jour.duree_min} min${plafond ? ` · palier ${plafond} au plus` : ""}`,
        }),
        selecteurParcours,
        bouton
      )
    );
  }
  refs.planJour.append(
    creerElement("p", {
      classe: "jour-note",
      texte: "Le palier indiqué est une borne de la semaine, jamais un objectif : c’est la maîtrise qui décide.",
    })
  );
}

function rendreSemaines(programme) {
  refs.semainesProgramme.replaceChildren();
  for (const semaine of programme.semaines || []) {
    const compte = { seance: 0, legere: 0, repos: 0 };
    for (const jour of semaine.jours || []) {
      if (compte[jour.type] !== undefined) compte[jour.type] += 1;
    }
    const plafonds = Object.entries(semaine.plafond_palier || {})
      .map(([theme, palier]) => `${nomTheme(theme)} ≤ ${palier}`)
      .join(" · ");
    refs.semainesProgramme.append(
      creerElement("article", { classe: "carte carte-semaine" },
        creerElement("h4", { texte: `Semaine ${semaine.semaine} — ${semaine.duree_min} min` }),
        creerElement("p", {
          texte: `${compte.seance} séances · ${compte.legere} journée légère · ${compte.repos} repos`,
        }),
        creerElement("p", { classe: "semaine-plafonds", texte: plafonds })
      )
    );
  }
}

function rendreRegles(regles) {
  refs.reglesProgramme.replaceChildren();
  const entrees = Object.entries(regles || {});
  if (!entrees.length) return;
  refs.reglesProgramme.append(creerElement("h3", { classe: "titre-note", texte: "Comment ça marche" }));
  const liste = creerElement("ul", { classe: "liste-regles" });
  for (const [cle, texte] of entrees) {
    liste.append(
      creerElement("li", {},
        creerElement("strong", { texte: `${LIBELLES_REGLES[cle] || cle} — ` }),
        document.createTextNode(texte)
      )
    );
  }
  refs.reglesProgramme.append(liste);
}

function nomTheme(identifiant) {
  const theme = etat.themesParId.get(identifiant);
  return theme ? theme.nom : identifiant;
}
