"use strict";

const CLE_SANS_LIMITE = "remediation.sansLimiteSessions";

const CLE_MODE_DEROGATOIRE = "orthogone.modeDerogatoire";

const CLE_LECTURE_AUTO = "remediation.lectureAuto";

function lectureAutoActivee() {
  try { return window.localStorage.getItem(CLE_LECTURE_AUTO) !== "off"; }
  catch { return true; }
}

function definirLectureAuto(active) {
  try { window.localStorage.setItem(CLE_LECTURE_AUTO, active ? "on" : "off"); } catch { /* stockage indisponible */ }
}

function preferenceLocale(cle, repli = "") {
  try { return window.localStorage.getItem(cle) ?? repli; } catch { return repli; }
}

function garderPreference(cle, valeur) {
  try { window.localStorage.setItem(cle, valeur); } catch { /* stockage indisponible */ }
}

function modeDerogatoireActif() {
  // Migration : une dérogation déjà activée reste disponible.
  return preferenceLocale(CLE_MODE_DEROGATOIRE,
    preferenceLocale("remediation.sansLimiteSessions") === "on" ? "on" : "off") === "on";
}

function sansLimiteActivee() {
  try { return modeDerogatoireActif() && window.localStorage.getItem(CLE_SANS_LIMITE) === "on"; }
  catch { return false; }
}

function definirSansLimite(active) {
  try { window.localStorage.setItem(CLE_SANS_LIMITE, active ? "on" : "off"); } catch { /* stockage indisponible */ }
}

const CLE_REJOUER_PALIER = "orthogone.rejouerPalier";
function rejouerPalierActive() {
  return modeDerogatoireActif() && preferenceLocale(CLE_REJOUER_PALIER) === "on";
}
