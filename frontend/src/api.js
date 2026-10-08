"use strict";
const API_BASE = "/api/entrainement";
const API_MISSIONS = "/api/missions";
const API_PROGRAMME = "/api/programme";

async function fetchJson(base, chemin, options = {}, tolereJson = false) {
  const entetes = { "Accept": "application/json" };
  if (options.body !== undefined) entetes["Content-Type"] = "application/json";
  let reponse;
  try {
    reponse = await fetch(base + chemin, { ...options, headers: entetes });
  } catch {
    const erreur = new Error("réseau indisponible");
    erreur.type = "reseau";
    throw erreur;
  }
  let donnees = null;
  if (tolereJson) {
    try { donnees = await reponse.json(); } catch { /* compatibilité entraînement */ }
  }
  if (!reponse.ok) {
    const erreur = new Error(`API ${reponse.status}`);
    erreur.type = "api";
    erreur.status = reponse.status;
    if (tolereJson) erreur.donnees = donnees;
    throw erreur;
  }
  return tolereJson ? donnees : reponse.json();
}

function apiFetch(chemin, options = {}) {
  return fetchJson(API_BASE, chemin, options, true);
}

function fetchMissions(chemin, options = {}) {
  return fetchJson(API_MISSIONS, chemin, options);
}
