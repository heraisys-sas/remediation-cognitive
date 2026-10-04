"""Couche de capacités du poste — chaque fonction choisit la meilleure
implémentation disponible, avec un repli qui ne dépend de rien.

Le logiciel reste **local** : aucune capacité ne sort de la machine. Pour que
besoin, on prend d'abord ce que le système fournit, puis un petit moteur
embarqué, puis un repli déterministe.

- `similarité` : **empreintes de phrases d'Apple** (`NaturalLanguage` /
  `NLEmbedding`, hors ligne, aucun modèle à embarquer) si disponibles ; sinon
  comparaison **lexicale** (n-grammes de caractères + recouvrement de mots) —
  toujours présente, sans dépendance.
- `synthèse` : déléguée à `domain.tts` (sécurisée, issue #2) — voix du
  système (`say` sur macOS, `powershell`/SAPI sur Windows, `espeak` sur Linux),
  renvoyée en WAV.
- `voix` (reconnaissance) : assurée par **côté client** (navigateur, ou OS de la
  tablette) — le serveur ne peut pas capturer le micro.

Portabilité : aucun paquet n'est obligatoire ; chaque fourni est détecté à
l'exécution. Ajouter une voix embarquée (ONNX Runtime + mini-modèle) revient
à ajouter une branche dans `_fournisseur_similarite` — voir
`docs/30-technique/pistes-extension-ia.md`.
"""

from __future__ import annotations

import math
import re
import unicodedata

from .tts import synthese  # noqa: F401  (ré-export, issue #2)

# Seuil d'acceptation d'une réponse ≈ proche (calibrer : paraphrases ≈ 0,80-0,90,
# distracteurs ≈ 0,42-0,68). S'applique aux réponses en texte libre uniquement.
SEUIL_SIMILARITE = 0.78

_EMBEDDINGS: object | None = None
_FOURNISSEUR: str | None = None


# --- Normalisation -------------------------------------------------------

def _normaliser(texte: str) -> str:
    sans_accent = unicodedata.normalize("NFD", str(texte or "").casefold())
    sans_accent = "".join(c for c in sans_accent if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^0-9a-z]+", " ", sans_accent).split())


def _ngrammes(texte: str, taille: int = 3) -> set[str]:
    plat = _normaliser(texte).replace(" ", "")
    if len(plat) < taille:
        return {plat} if plat else set()
    return {plat[i : i + taille] for i in range(len(plat) - taille + 1)}


# --- Similarité ----------------------------------------------------------

def _embeddings_apple():
    """Empreintes de phrases d'Apple, ou None si indisponibles (hors macOS)."""
    global _EMBEDDINGS
    if _EMBEDDINGS is None:
        try:
            import NaturalLanguage as nl  # pyobjc — macOS uniquement

            _EMBEDDINGS = nl.NLEmbedding.sentenceEmbeddingForLanguage_("fr") or False
        except Exception:
            _EMBEDDINGS = False
    return _EMBEDDINGS or None


def fournisseur_similarite() -> str:
    """Fournisseur retenu : `nle_embedding` (Apple) ou `lexical` (repli)."""
    global _FOURNISSEUR
    if _FOURNISSEUR is None:
        _FOURNISSEUR = "nle_embedding" if _embeddings_apple() is not None else "lexical"
    return _FOURNISSEUR


def _similarite_apple(a: str, b: str) -> float:
    embeddings = _embeddings_apple()
    va, vb = embeddings.vectorForString_(a), embeddings.vectorForString_(b)
    if va is None or vb is None:
        return 0.0
    va = [float(x) for x in va]
    vb = [float(x) for x in vb]
    na = math.sqrt(sum(x * x for x in va))
    nb = math.sqrt(sum(x * x for x in vb))
    if not na or not nb:
        return 0.0
    return max(0.0, min(1.0, sum(x * y for x, y in zip(va, vb)) / (na * nb)))


def _similarite_lexicale(a: str, b: str) -> float:
    na, nb = _normaliser(a), _normaliser(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    grammaire = _ngrammes(a) | _ngrammes(b)
    jacarand = len(_ngrammes(a) & _ngrammes(b)) / len(grammaire) if grammaire else 0.0
    mots_a, mots_b = set(na.split()), set(nb.split())
    recouvrement = len(mots_a & mots_b) / max(len(mots_a), len(mots_b))
    return round(0.5 * jacarand + 0.5 * recouvrement, 4)


def similarite(a: str, b: str) -> float:
    """Proximité de deux textes, de 0 (rien à voir) à 1 (identiques ou équivalents)."""
    if fournisseur_similarite() == "nle_embedding":
        return round(_similarite_apple(a, b), 4)
    return _similarite_lexicale(a, b)


def proche(reponse: str, attendues: list[str], seuil: float | None = None) -> bool:
    """La réponse est-elle ≈ assez proche de l'une des formulations attendues ?"""
    limite = SEUIL_SIMILARITE if seuil is None else seuil
    return any(similarite(reponse, attendue) >= limite for attendue in attendues if attendue)


# --- État des capacités --------------------------------------------------

def capacites() -> dict:
    """Ce que ce poste sait faire, et par quel moyen — pour l'interface et le diagnostic."""
    import platform

    return {
        "similarite": {"disponible": True, "fournisseur": fournisseur_similarite(),
                        "seuil": SEUIL_SIMILARITE},
        "synthese": {"disponible": True, "moyen": "voix du système"},
        "voix": {"disponible": None, "moyen": "client (navigateur ou OS de la tablette)"},
        "plateforme": platform.system(),
        "principe": "local — aucune donnée ne quitte le poste",
    }
