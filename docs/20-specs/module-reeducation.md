# Spécification — Module Rééducation ciblée (usage strictement familial)

Un sous-module par fonction. Ordre de priorité : **attention soutenue → attention divisée → mémoire de travail → flexibilité/inhibition → planification**.

## Structure commune à chaque sous-module

- Paliers de difficulté **très fins** (inspiration Kumon) avec critère de maîtrise explicite avant progression : 90 % de réussite sur 3 sessions consécutives.
- Mode **errorless en entrée de palier** ; bascule vers l'essai-erreur guidé une fois la fatigabilité réduite (paramètre modifiable avec garde-fou).
- Séances courtes **5–10 min** ; limite de sessions/jour paramétrable.
- **Alerte de fatigue** si le temps de réaction se dégrade en cours de session (indicateur objectif de fatigabilité, fréquent en SPC) → proposition d'arrêt.

## Épreuves par fonction

| Fonction | Type d'épreuve | Dossier contenu |
|---|---|---|
| Attention soutenue | Temps de réaction continu (type CPT) | `content/reeducation/attention-soutenue/` |
| Attention divisée | Double tâche simple | `content/reeducation/attention-divisee/` |
| Mémoire de travail | Empan, n-back léger | `content/reeducation/memoire-travail/` |
| Flexibilité | Trail Making adapté | `content/reeducation/flexibilite/` |
| Inhibition | Stroop adapté | `content/reeducation/inhibition/` |
| Planification | Multi-étapes (type Tour de Londres adaptée) | `content/reeducation/planification/` |

## Contraintes

- Usage strictement familial — aucune diffusion à des tiers professionnels.
- Aucune norme populationnelle affichée à l'utilisateur.
- Vocabulaire sobre (ni clinique, ni ludique) — cf. `backend/app/domain/messages.py`.
- Garde-fous : voir [moteur-adaptatif.md](moteur-adaptatif.md).
