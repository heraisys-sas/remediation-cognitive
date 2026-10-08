"use strict";

async function ouvrirMissions() {
  etat.missionActive = null;
  refs.zoneNoteMission.hidden = true;
  refs.messageNote.hidden = true;
  refs.listeMissions.replaceChildren();
  refs.journalMissions.replaceChildren(
    creerElement("p", { classe: "ligne-discrete", texte: "Chargement…" })
  );
  afficherVue("missions");
  try {
    const donnees = await fetchMissions("");
    etat.missions = donnees.missions || [];
    rendreMissions(etat.missions, donnees.ressentis || []);
    masquerBandeau();
    await chargerJournal();
  } catch {
    refs.journalMissions.replaceChildren();
    afficherBandeau("Les missions n’ont pas pu être chargées pour le moment.", { retour: true });
  }
}

function rendreMissions(missions, ressentis) {
  refs.champRessenti.replaceChildren(
    creerElement("option", { texte: "—", attributs: { value: "" } }),
    ...ressentis.map((ressenti) =>
      creerElement("option", { texte: ressenti, attributs: { value: ressenti } })
    )
  );
  refs.listeMissions.replaceChildren();
  if (!missions.length) {
    refs.listeMissions.append(
      creerElement("p", { classe: "ligne-discrete", texte: "Aucune mission proposée pour le moment." })
    );
    return;
  }
  for (const mission of missions) {
    const bouton = creerElement("button", {
      classe: "bouton bouton-secondaire",
      texte: "Mission faite — noter",
      attributs: { type: "button" },
    });
    bouton.addEventListener("click", () => ouvrirNoteMission(mission));
    refs.listeMissions.append(
      creerElement("article", { classe: "carte carte-mission" },
        creerElement("h3", { texte: mission.titre }),
        creerElement("p", { classe: "mission-pourquoi", texte: mission.pourquoi }),
        creerElement("ol", { classe: "mission-etapes" },
          ...mission.etapes.map((etape) => creerElement("li", { texte: etape }))
        ),
        creerElement("p", { classe: "mission-repere", texte: `Repère de réussite : ${mission.repere}` }),
        bouton
      )
    );
  }
}

function ouvrirNoteMission(mission) {
  etat.missionActive = mission;
  refs.titreNote.textContent = `Noter : ${mission.titre}`;
  refs.champNote.value = "";
  refs.champRessenti.value = "";
  refs.messageNote.hidden = true;
  refs.zoneNoteMission.hidden = false;
  refs.champNote.focus();
}

async function enregistrerNote() {
  if (etat.actionEnCours || !etat.missionActive) return;
  const texte = refs.champNote.value.trim();
  if (!texte) {
    refs.messageNote.hidden = false;
    refs.messageNote.textContent = "Écris quelques mots avant d’enregistrer.";
    return;
  }
  etat.actionEnCours = true;
  refs.boutonEnregistrerNote.disabled = true;
  try {
    await fetchMissions("/journal", {
      method: "POST",
      body: JSON.stringify({
        mission_id: etat.missionActive.id,
        texte,
        ressenti: refs.champRessenti.value || null,
      }),
    });
    masquerBandeau();
    refs.zoneNoteMission.hidden = true;
    refs.messageNote.hidden = false;
    refs.messageNote.textContent = "Note enregistrée — elle reste sur cet appareil.";
    etat.missionActive = null;
    await chargerJournal();
  } catch {
    afficherBandeau("La note n’a pas pu être enregistrée pour le moment.", {
      reessayer: enregistrerNote,
    });
  } finally {
    etat.actionEnCours = false;
    refs.boutonEnregistrerNote.disabled = false;
  }
}

async function chargerJournal() {
  try {
    const donnees = await fetchMissions("/journal");
    const entrees = (donnees.entrees || []).slice().reverse();
    refs.journalMissions.replaceChildren();
    if (!entrees.length) {
      refs.journalMissions.append(
        creerElement("p", { classe: "ligne-discrete", texte: "Aucune note pour l’instant." })
      );
      return;
    }
    for (const entree of entrees) {
      const mission = etat.missions.find((m) => m.id === entree.mission_id);
      const details = [formaterDate(entree.date), entree.ressenti].filter(Boolean).join(" · ");
      refs.journalMissions.append(
        creerElement("article", { classe: "carte carte-note" },
          creerElement("p", { classe: "note-titre", texte: mission ? mission.titre : entree.mission_id }),
          creerElement("p", { classe: "note-texte", texte: entree.texte }),
          creerElement("p", { classe: "note-meta", texte: details })
        )
      );
    }
  } catch {
    refs.journalMissions.replaceChildren(
      creerElement("p", { classe: "ligne-discrete", texte: "Carnet indisponible pour le moment." })
    );
  }
}

function formaterDate(iso) {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
}
