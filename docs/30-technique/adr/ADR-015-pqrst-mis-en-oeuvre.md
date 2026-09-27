# ADR-015 — PQRST mis en œuvre : la méthode appliquée, pas seulement testée

**Statut** : accepté (2026-09-27) — arbitrages de l'orthophoniste appliqués.

## Contexte

Le palier PQRST existant **teste le résultat** de la méthode : le texte s'affiche 25 s, disparaît, puis deux questions de mémoire sont posées. La méthode est nommée dans la consigne, mais jamais mise en œuvre : personne n'est amené à survoler le texte, à se poser une question, ni à le reformuler. Constat d'usage confirmé : « les exercices de méthode sollicitent la mémoire plus que la stratégie ».

Or les deux étapes qui portent l'apprentissage (**écrire sa question**, **reformuler avec ses mots**) sont des productions — effet de génération et élaboration verbale. Elles manquaient.

## Décision

**1. Un palier supplémentaire : « PQRST mis en œuvre »** (palier 6 du thème méthodes), ajouté **après** les cinq paliers actuels. On découvre la méthode, puis on l'applique. Le palier de mesure du résultat est conservé.

**2. Un item = une séquence guidée complète**, sur un texte de **quatre phrases** du quotidien. La séquence ne doit pas être interrompue par d'autres exercices :

| Étape | Contenu | Jugé ? |
|---|---|---|
| 1. Parcours | le sujet du texte, avant lecture | oui (choix) |
| 2. Question | **écrire sa propre question** | **non** — une question modèle est montrée ensuite |
| 3. Lecture | le texte entier, **sans chronomètre**, la question de la personne restant sous ses yeux | — |
| 4. Reformulation | **redire le texte avec ses mots** | oui, à **4 idées-clés sur 5** ; résumé modèle montré dans tous les cas |
| 5. Test | deux questions de mémoire | oui (les deux ensemble) |

**3. La production n'est pas notée.** La question personnelle est une production active ; sa note n'aurait pas de sens et découragerait. Ce qui est vérifié, c'est qu'elle a été écrite — puis le modèle sert de repère (même logique que l'analyse de mot en évocation).

**4. Une seule réception, une correction par étape.** Les cinq étapes se répondent d'affilée et partent en un seul envoi ; le retour détaille chaque étape (parcours, question modèle, idées retrouvées et manquées, test). C'est la procédure entière qui est revue, comme elle se déroule dans la vie réelle.

**5. La fiche méthode est reprise en fin de séance** : les cinq étapes en cinq lignes, à garder hors écran.

**6. La faisabilité est vérifiée au dépôt.** Le validateur exige que **chaque idée-clé se retrouve dans le résumé modèle** — sans quoi une reformulation juste serait refusée. Ce contrôle a immédiatement attrapé un défaut réel : deux résumés modèles ne portaient pas toutes leurs idées.

## Conséquences

- (+) La stratégie est réellement entraînée : deux productions par texte, guidées par la méthode et non par un test de mémoire.
- (+) La séquence est indivisible : les cinq étapes d'un même texte se suivent dans la séance.
- (+) Rien n'est jugé qui ne doive l'être ; les tolérances habituelles s'appliquent (accents, variantes, dictée), et le seuil de reformulation est explicite (4/5).
- (+) Les nouveaux identifiants (`mt-6-…`) évitent tout héritage d'état de révision.
- (−) L'item est long (2 à 3 minutes) : quatre textes par palier, soit une séance de 8 à 12 minutes — dans le cadre, sans nouveau paramètre.
- (−) Le contenu est rédigé à la main (quatre séquences) : l'enrichir demandera du soin, chaque texte devant tenir ses cinq idées-clés.
- (−) Un type d'exercice de plus à maintenir (structure, correction, interface, contrôles).
