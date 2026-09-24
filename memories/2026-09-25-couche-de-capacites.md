# 2026-09-25 — Couche de capacités du poste (local)

## La demande

« Fait le. On va rester en local et utiliser les capacités de l'OS. Ce devra être portable vers une autre plateforme type tablette plus tard. »

## Ce qui a été construit

- **`backend/app/domain/capacites.py`** : une couche où chaque besoin prend ce que le système fournit, puis un repli qui ne dépend de rien.
  - similarité : **empreintes de phrases d'Apple** (`NativeLanguage`/`NLEmbedding`, hors ligne) → sinon **lexical** (n-grammes + recouvrement de mots) ;
  - synthèse : **voix du système** (`say`+`afconvert` sur macOS, PowerShell/SAPI sur Windows, `espeak` sur Linux) ;
  - voix : **côté client** (le serveur ne capte pas le micro).
- **API** : `GET /api/capacites`, `POST /api/capacites/similarite`, `POST /api/capacites/synthese`.
- **Correction** : le **sens** entre désormais dans le jugement — synonyme accepté en accès lexical, formulation proche en prise de message. Une réponse éloignée reste refusée.
- **Interface** : `frontend/src/capacites.js` (dictée + synthèse, repli silencieux) et deux boutons (« Répondre à voix haute », « Écouter la consigne »), masqués si le poste ne les propose pas.

## Calibration et pièges

- **Seuil de similarité 0,78**, calibré sur des cas réels : paraphrases 0,80–0,90 (« le toubib »/« le médecin » 0,86 ; « la cave »/« la porte de la cave » 0,90), distracteurs 0,42–0,68 (« la boulangerie »/« le médecin » 0,60 ; « marteau »/« tournevis » 0,61). Les nombres se comparent mal par embeddings (« deux »/« 2 » = 0,33) mais la normalisation s'en charge déjà.
- **`say` est lent au premier appel** : la synthèse retente une fois avec un délai plus large — un échec transitoire ne doit pas se voir comme une capacité absente.
- **Dépendance optionnelle assumée** : `pyobjc-framework-NaturalLanguage` (macOS) active les empreintes ; ailleurs le repli lexical suffit, et l'ajout d'un moteur ONNX est la branche à écrire pour Windows/Linux.

## Portabilité (l'exigence)

Aucun paquet obligatoire, aucune connexion : le module détecte et se replie. Une enveloppe native (tablette) remplacera `capacites.js` sans toucher au reste — c'est justement pourquoi la dictée vit côté client.

## Contrôles

**811 items / 0 erreur**, **140 tests** (dont 6 sur les capacités, écrits pour être portables : ils s'adaptent au fournisseur disponible).
