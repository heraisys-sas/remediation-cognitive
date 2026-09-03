# Sécurité et conformité

## Données

- **Chiffrement au repos** des fichiers de sessions/scores (deux dépôts séparés, ADR-002).
- **Droit à l'effacement** + export patient natif (JSON lisible machine).
- **DPIA** à produire avant toute exposition au-delà de l'usage familial.
- Les données de bilan sont des données de santé (RGPD art. 9) : base légale à documenter.

## Règles codées en dur

1. Aucune donnée de bilan cognitif ne transite par un service tiers non-HDS.
2. Séparation physique/logique des stockages entraînement vs bilan.
3. Aucun score présenté comme un diagnostic dans l'UI patient.

## Clés et secrets

- Jamais de clé en clair dans le dépôt (ni code, ni docs, ni config).
- Gestion des clés de chiffrement : ADR à produire au premier sprint backend.

## Journalisation

- Accès aux données de bilan journalisés (qui, quoi, quand) dès la Phase 2.
- Export PDF/JSON journalisé lui aussi.

## HDS

- Requis si stockage de données de bilan à caractère médical — expérience OVHcloud HDS / Eclairion à capitaliser.
- Périmètre borné par la séparation ADR-002.
