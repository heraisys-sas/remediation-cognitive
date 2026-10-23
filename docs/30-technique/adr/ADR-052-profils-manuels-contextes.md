# ADR-052 — Deux profils manuels pour Contextes

Date : 23 octobre 2026. Statut : adopté pour le lot minimal, issue #34.

## Contexte

Les vingt scènes actuelles proposent dix items par séance. Les distracteurs historiques peuvent désigner des sources absentes de cette séance : une réponse peut alors profiter de la familiarité de la source sans récupérer son association au message. Ce constat justifie une condition supplémentaire, sans produire de photos ni créer des paliers prétendument validés.

## Décision

La nouvelle séance Contextes est étiquetée `contextes-source-v2` et porte le profil manuel `origine` (défaut, choix historiques) ou `sources-vues`. Le profil ne change ni sélection FSRS, ni quota dix, ni durée des photos, ni identifiants, ni banque. La progression continue de ne retenir que le rappel final (ADR-039). Aucun seuil de changement automatique de profil n’est introduit.

Pour `sources-vues`, le serveur construit `contenu.options_rappel` sur une copie des items sélectionnés : réponse correcte une seule fois, au plus trois autres sources distinctes des scènes de cette séance. Une petite sélection de moins de quatre sources distinctes garde moins de choix ; aucune source inédite ne complète le lot. La découverte et le rappel utilisent cette même liste de cohorte dans le profil `sources-vues` ; livrer deux listes différentes permettrait parfois de déduire la bonne source par leur intersection. Seul `origine` conserve les choix historiques. Le serveur refuse le rappel tant que chaque item sélectionné n’a pas une découverte acceptée ; chaque découverte exige les faits `photo_chargee: true` et `exposition_ms`. Ces faits déclarent un chargement et une exposition dans le client, pas une preuve de regard ou d’attention.

L’interface bloque déjà sur un échec de chargement : Réessayer ou Terminer. Après récupération, `photo_chargee` devient vrai, l’incident reste tracé. Un incident persistant ne permet donc pas de produire un rappel dans cette condition. Aucun repli silencieux vers le profil origine.

Le protocole est journalisé dès le démarrage. Chaque observation documentée porte sa copie du protocole et les `choix_proposes` réels, calculés par le serveur selon la passe. Les anciennes séances et historiques ne sont ni migrés ni réinterprétés. Les clients sans profil explicite restent sur origine.

## Conséquences

Les deux conditions sont descriptives, pas des niveaux cliniques, des scores comparables ou une promesse de généralisation. La banque et le moteur restent inchangés. Tests couvrent choix faux, unicité de la bonne source, sources familières, petite sélection, incident/récupération, défaut, journal et absence d’effet moteur de la découverte.
