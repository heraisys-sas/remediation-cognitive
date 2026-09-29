# Déduction — reprise directe Codex, 29 septembre 2026

Après les tentatives AutoClaw échouées sans code, Olivier demande l'implémentation directe. Travail dans `/Users/olivierhz/orthogone/deduction-corrections` seulement, branche d'essai `amelioration-deduction-20260927`, base 7400534.

Trois types de contraintes explicites, propagation sans hypothèse, contre-vérificateur d'unicité indépendant, 100 nouveaux items / cinq paliers / trois étapes. P4 3×3, P5 4×4. Aucune règle collective implicite. Anciennes cartes sans réaffectation ; palier conservé ; ancien historique séparé des nouvelles séances éligibles dans `historique_etapes`.

Régressions rencontrées et corrigées : cardinalité impossible sur « chaque » région ; contrôle JS qui gardait le champ `et` en testant un atome ; absence du verbe positif après une négation dans les phrases composées. Suite finale et mesures : CORRECTION_REPORT.md. Les deux familles de preuve (unicité / propagation) restent distinctes, sans calibration clinique.

Ne pas relancer AutoClaw sur les fichiers de déduction. Serveur du checkout AutoClaw non touché : pour essayer cette livraison, démarrer depuis le checkout de branche d'essai ou intégrer délibérément la branche plus tard. Aucun changement de main.
