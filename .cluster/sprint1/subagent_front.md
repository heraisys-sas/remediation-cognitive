# Rapport — Interface web du module Entraînement (Sprint 1)

> Sous-agent frontend · 2026-09-03 · périmètre respecté : `frontend/` exclusivement
> (aucune modification backend/, engine/, content/ ; aucun commit ; aucun outil de build).

## Fichiers livrés

| Fichier | Rôle |
|---|---|
| `frontend/index.html` | Structure statique des 3 écrans (thèmes / séance / résumé) + bandeau d'incident ; aucune vue générée à la main hors DOM API. |
| `frontend/src/app.js` | SPA vanilla (~440 lignes, ES2020, `defer`, zéro dépendance) : état, couche API, rendu, gestion d'erreurs, a11y. |
| `frontend/src/styles.css` | Dark mode par défaut, palette oklch désaturée, focus visible, transitions couleur courtes uniquement. |

Servie par FastAPI sur `/ui` (montage attendu : `StaticFiles(directory="frontend", html=True)`, qui redirige `/ui` → `/ui/` ; les assets sont référencés en relatif au document, l'API en absolu `/api/entrainement/...` comme demandé).

## Choix de design (règles projet, photophobie SPC)

- **Dark mode seul** (`color-scheme: dark`, `theme-color` assorti) ; fond enveloppant `oklch(0.165 0.012 262)` avec un très léger dégradé radial statique en haut.
- **Une seule couleur d'accent** : sarcelle doux `oklch(0.78 0.075 190)` (boutons primaires, barre de progression, focus, notices, carte d'arrêt proposé). Le vert/rouge très désaturés n'apparaissent **que** dans le feedback correct/incorrect (sémantique, jamais décoratif), toujours doublés d'un libellé texte (« ✓ Bonne réponse ! » / « ✕ Pas tout à fait ») — la couleur ne porte jamais seule l'information.
- **Zéro scintillement** : aucune animation d'apparition, pas de pulse/flash/translation ; seules des transitions de couleur (0,18 s) et la largeur de la barre de progression (0,25 s) ; tout est neutralisé sous `prefers-reduced-motion`.
- **Contrastes AA vérifiés** (calculs oklch→Y) : texte principal ≈ 13,5:1, texte secondaire ≈ 7,8:1 sur carte, blanc jamais pur (0,90) pour éviter l'éblouissement ; tous les textes courants ≥ 7:1 (AA largeement couvert, AAA pour la plupart).
- **Faible densité** : colonne unique centrée (42rem), interlignage 1,65, énoncé en grand (clamp 1,55→2,3rem), champ de saisie 1,3rem (≥16 px, pas de zoom iOS), boutons ≥ 3,4rem de haut, radio de 12–16px, beaucoup d'air.
- **Aucune image, aucun emoji** ; glypes sobres ✓/✕ uniquement dans le feedback.
- Focus clavier visible (outline 2 px accent + offset), lien d'évitement, titres d'écran recevant le focus au changement de vue.

## Accessibilité

- Un seul champ, `label` visible « Ta réponse », `inputmode="numeric"` si `theme.id === "calcul-mental"` (sinon `text`), `autocomplete/spellcheck/autocapitalize` désactivés, `enterkeyhint="done"`.
- **Entrée = Valider** (soumission du formulaire) ; après validation, focus déplacé sur « Suivant » → Entrée enchaîne ; navigation 100 % clavier.
- Feedback et bandeau d'incident en `role="status" aria-live="polite"` ; progression en `role="progressbar"` (valuemin/max/now) + texte visible « Question n sur max ».
- Confirmation d'arrêt en deux temps (« Terminer la séance » → « Confirmer la fin ? », 5 s) sans fenêtre modale brusque.

## Mapping contrat → UI

| Contrat | Implémentation |
|---|---|
| `GET /themes` | Cartes (nom, description, « Commencer ») ; liste vide → notice calme. |
| `POST /{theme}/sessions` `201` | Items tenus côté client, affichage un par un ; `regles` ignorées à l'affichage (le max affiché = `items.length`, source de vérité réelle). `items` vide → séance clôturée silencieusement (`POST /fin` en tâche de fond, erreurs ignorées) + notice « Rien à réviser… ». |
| `POST .../reponses` | Corps `{item_id, reponse, temps_ms}` ; `temps_ms` mesuré depuis l'affichage de la question. `reponse` : nombre si thème calcul-mental et saisie numérique (accepte la virgule), sinon chaîne trimée. Réponse attendue **jamais devinée ni pré-chargée** : elle vient uniquement de la réponse du serveur (`attendue`), affichée après coup avec le `feedback` serveur (vocabulaire centralisé côté backend). |
| `POST .../fin` | Bouton « Terminer la séance » toujours visible + « Voir le résumé » après le dernier item ; `409` → bandeau « Cette séance est déjà terminée » + retour. |
| Résumé | `items`/`correctes`/`duree_s` (formatée « 1 min 35 s »)/`taux_reussite` (« 50 % ») en chiffres neutres, **aucun jugement, aucune norme** ; `arret_propose` → carte bienveillante avec le message exact requis + rappel « tu décides » ; `sessions_restantes_aujourdhui` → ligne douce facultative. |
| `429` | Message exact : « Trois séances déjà faites aujourd'hui — le repos fait partie de l'entraînement. », en notice calme sur l'écran des thèmes. |
| Erreurs réseau | Bandeau discret rechargeable (« Réessayer » relance l'action exacte, saisie conservée) ; `404/409` en séance → « Retour aux thèmes ». Anti double-soumission par verrou `actionEnCours` + états de boutons centralisés. |

## Vocabulaire

Neutre/chaleureux, modérément ludique : « Choisis ta séance », « Des séances courtes, à ton rythme », « Pas tout à fait », « Voir un coup de pouce », « Doucement, régulièrement — c'est ce qui compte ». Aucun terme clinique, aucun score présenté comme un diagnostic, aucune norme populationnelle ; les `feedback` serveur sont affichés tels quels (source unique : `backend/app/domain/messages.py`).

## Vérifications

- `node --check` OK ; cohérence IDs HTML/JS vérifiée automatiquement.
- **Test de fumée hors dépôt** (jsdom + fetch simulé, dans le tmp du workspace, rien d'ajouté au dépôt) : 43 vérifications passées — rendu des thèmes, inputmode, progression, aide conditionnelle, validation vide (indice, aucun POST), POST reponses avec corps et temps_ms corrects, feedback incorrect + attendue, enchaînement « Suivant », libellé « Voir le résumé », POST fin, résumé (stats, durée, taux), carte `arret_propose` avec message exact, séances restantes, retour thèmes, 429 (message exact, reste sur thèmes), erreur réseau → bandeau → Réessayer OK, « Terminer » en deux temps.
- Deux bugs d'état trouvés et corrigés grâce au test (boutons restant désactivés après validation / au retour sur la question suivante).

## Points d'attention pour l'agent API

- Monter `frontend/` en statique avec `html=True` sur `/ui` (redirection slash incluse).
- Le client poste `reponse` en `str|number` (nombre pour le calcul mental) — la correction serveur doit tolérer les deux, conformément au contrat.
