"""Ajouts originaux v3 : charge et règles inchangées, contextes renouvelés."""
import unicodedata


AJOUTS = {parcours: [] for parcours in ('plan', 'rappel', 'message', 'temps')}


def ajouter(parcours, **contenu):
    index = len(AJOUTS[parcours]) + 4
    AJOUTS[parcours].append({'id': f'strategie-{parcours}-simulation-{index}-v3', **contenu})


# Les IDs historiques désignent les rôles : préparation, finalisation, ajout.
# Les deux préparations restent indépendantes ; chacune précède la finalisation.
for but, labels, initial, nouvelle in [
    ('Préparer une boîte cadeau avec son message.', ['Mettre le cadeau dans la boîte', 'Fermer la boîte', 'Ajouter la carte dans la boîte'], 'Mettre le cadeau dans la boîte avant de la fermer.', 'Ajouter la carte dans la boîte avant de la fermer.'),
    ('Envoyer les informations pour une promenade de groupe.', ['Rédiger le message', 'Envoyer le message', 'Joindre le plan du rendez-vous'], 'Rédiger le message avant de l’envoyer.', 'Joindre le plan du rendez-vous avant d’envoyer le message.'),
    ('Publier une annonce pour vendre un meuble.', ['Rédiger la description', 'Publier l’annonce', 'Ajouter la photo du meuble'], 'Rédiger la description avant de publier l’annonce.', 'Ajouter la photo avant de publier l’annonce.'),
    ('Préparer un enregistrement de lecture à voix haute.', ['Tester le microphone', 'Démarrer l’enregistrement', 'Poser le texte sur le pupitre'], 'Tester le microphone avant de démarrer l’enregistrement.', 'Poser le texte sur le pupitre avant de démarrer l’enregistrement.'),
    ('Préparer une partie de jeu de société.', ['Déplier le plateau', 'Commencer la partie', 'Distribuer les cartes aux joueurs'], 'Déplier le plateau avant de commencer la partie.', 'Distribuer les cartes avant de commencer la partie.'),
    ('Préparer une sortie de courses avec un bon de réduction.', ['Écrire la liste de courses', 'Partir faire les courses', 'Mettre le bon de réduction dans le portefeuille'], 'Écrire la liste avant de partir faire les courses.', 'Mettre le bon de réduction dans le portefeuille avant de partir faire les courses.'),
    ('Préparer un sac de livres à rapporter à la bibliothèque.', ['Mettre les livres dans le sac', 'Fermer le sac', 'Ajouter la carte de bibliothèque dans le sac'], 'Mettre les livres dans le sac avant de le fermer.', 'Ajouter la carte de bibliothèque dans le sac avant de le fermer.'),
    ('Préparer une demande de réparation d’un appareil.', ['Compléter la demande', 'Envoyer la demande', 'Joindre la photo de l’appareil'], 'Compléter la demande avant de l’envoyer.', 'Joindre la photo de l’appareil avant d’envoyer la demande.'),
    ('Préparer une table pour un atelier de dessin.', ['Poser les feuilles sur la table', 'Commencer l’atelier', 'Disposer les crayons sur la table'], 'Poser les feuilles avant de commencer l’atelier.', 'Disposer les crayons avant de commencer l’atelier.'),
]:
    ajouter('plan', but=but, actions=[{'id': key, 'texte': label} for key, label in zip(('remplir', 'signer', 'joindre'), labels)], contraintes=[initial, 'Les trois actions sont nécessaires.'], nouvelle_contrainte=nouvelle)


for index, (signal, target, other, actions) in enumerate([
    ('Colis prêt', ('retour', 'Bon de retour'), ('notice', 'Notice du produit'), [('adresse', 'Vérifier l’adresse du destinataire'), ('reference', 'Vérifier la référence du colis')]),
    ('Sortie confirmée', ('trajet', 'Plan du trajet'), ('menu', 'Menu du restaurant'), [('date', 'Vérifier la date de la sortie'), ('participants', 'Vérifier le nombre de participants')]),
    ('Commande validée', ('retrait', 'Bon de retrait'), ('catalogue', 'Page du catalogue'), [('article', 'Vérifier le nom de l’article'), ('quantite', 'Vérifier la quantité commandée')]),
    ('Atelier confirmé', ('materiel', 'Liste du matériel à apporter'), ('tarifs', 'Tarifs des autres ateliers'), [('lieu', 'Vérifier le lieu de l’atelier'), ('horaire', 'Vérifier l’heure de début')]),
    ('Réunion prête', ('ordre', 'Ordre du jour'), ('compte_rendu', 'Compte rendu de la réunion précédente'), [('date', 'Vérifier la date de la réunion'), ('participants', 'Vérifier la liste des participants')]),
    ('Prêt accepté', ('notice', 'Notice de l’outil prêté'), ('catalogue', 'Catalogue des outils'), [('reference', 'Vérifier la référence de l’outil'), ('retour', 'Vérifier la date de retour prévue')]),
    ('Visite confirmée', ('billet', 'Billet d’entrée'), ('programme', 'Programme des expositions'), [('date', 'Vérifier la date de la visite'), ('heure', 'Vérifier l’heure d’entrée')]),
    ('Réparation terminée', ('depot', 'Ticket de dépôt'), ('catalogue', 'Catalogue des appareils'), [('appareil', 'Vérifier le nom de l’appareil'), ('numero', 'Vérifier le numéro du dossier')]),
    ('Concert confirmé', ('reservation', 'Confirmation de réservation'), ('affiche', 'Affiche du concert'), [('salle', 'Vérifier le nom de la salle'), ('date', 'Vérifier la date du concert')]),
]):
    pieces = (other, target) if index % 2 == 0 else (target, other)
    ajouter('rappel', signal=signal, attendu_piece=target[0], consigne=f'Quand « {signal} » apparaît, joignez : {target[1]}.', pieces=[{'id': key, 'texte': text} for key, text in pieces], actions_intercalees=[{'id': key, 'texte': text} for key, text in actions])


def formes(*valeurs):
    return [''.join(c for c in unicodedata.normalize('NFD', valeur.lower()) if not unicodedata.combining(c)) for valeur in valeurs]


for index, (imperatif, target, text, heure, distracteurs) in enumerate([
    ('Déposez le colis', 'deposer', 'Déposer le colis', '15', [('peser', 'Peser le colis'), ('ouvrir', 'Ouvrir le colis')]),
    ('Arrosez les plantes', 'arroser', 'Arroser les plantes', '10', [('tailler', 'Tailler les plantes'), ('deplacer', 'Déplacer les plantes')]),
    ('Fermez les volets', 'fermer', 'Fermer les volets', '18', [('ouvrir', 'Ouvrir les volets'), ('nettoyer', 'Nettoyer les volets')]),
    ('Réservez la salle', 'reserver', 'Réserver la salle', '15', [('visiter', 'Visiter la salle'), ('nettoyer', 'Nettoyer la salle')]),
    ('Apportez le livre', 'apporter', 'Apporter le livre', '10', [('lire', 'Lire le livre'), ('ranger', 'Ranger le livre')]),
    ('Photographiez le meuble', 'photographier', 'Photographier le meuble', '18', [('mesurer', 'Mesurer le meuble'), ('deplacer', 'Déplacer le meuble')]),
    ('Branchez la tablette', 'brancher', 'Brancher la tablette', '15', [('eteindre', 'Éteindre la tablette'), ('ranger', 'Ranger la tablette')]),
    ('Notez le numéro de suivi', 'noter', 'Noter le numéro de suivi', '10', [('dicter', 'Dicter le numéro de suivi'), ('effacer', 'Effacer le numéro de suivi')]),
    ('Rangez les outils', 'ranger', 'Ranger les outils', '18', [('nettoyer', 'Nettoyer les outils'), ('photographier', 'Photographier les outils')]),
]):
    actions = list(distracteurs)
    actions.insert((index + 1) % 3, (target, text))
    ajouter('message', message=f'{imperatif} à {heure} heures.', attendu_action=target, attendu_quoi=text, attendu_heure=heure, formes_quoi=formes(text, imperatif, f'Je dois {text.lower()}'), actions=[{'id': key, 'texte': label} for key, label in actions], heures=['15 h', '10 h', '18 h'])


for consigne, categories, documents, expected in [
    ('Classez les plans dans Plan et les horaires dans Horaire.', ['plan', 'horaire'], ['Horaires du bus', 'Plan du quartier', 'Plan de la gare', 'Horaires de la piscine'], ['horaire', 'plan', 'plan', 'horaire']),
    ('Classez les recettes dans Recette et les listes de courses dans Courses.', ['recette', 'courses'], ['Recette de gratin', 'Recette de compote', 'Liste de courses du marché', 'Liste de courses de la boulangerie'], ['recette', 'recette', 'courses', 'courses']),
    ('Classez les inscriptions aux ateliers dans Atelier et les inscriptions aux sorties dans Sortie.', ['atelier', 'sortie'], ['Inscription à la sortie au musée', 'Inscription à l’atelier de dessin', 'Inscription à la sortie au jardin', 'Inscription à l’atelier de couture'], ['sortie', 'atelier', 'sortie', 'atelier']),
    ('Classez les notices dans Notice et les garanties dans Garantie.', ['notice', 'garantie'], ['Garantie du grille-pain', 'Garantie de la lampe', 'Notice du ventilateur', 'Notice de la radio'], ['garantie', 'garantie', 'notice', 'notice']),
    ('Classez les factures dans Facture et les devis dans Devis.', ['facture', 'devis'], ['Facture du plombier', 'Devis du peintre', 'Devis du menuisier', 'Facture du serrurier'], ['facture', 'devis', 'devis', 'facture']),
    ('Classez les invitations dans Invitation et les attestations dans Attestation.', ['invitation', 'attestation'], ['Invitation à la fête du quartier', 'Attestation de présence à l’atelier', 'Invitation à une inauguration', 'Attestation de participation à la sortie'], ['invitation', 'attestation', 'invitation', 'attestation']),
    ('Classez les programmes de concerts dans Concert et les programmes de matchs dans Match.', ['concert', 'match'], ['Programme du match de basket', 'Programme du concert de jazz', 'Programme du concert de piano', 'Programme du match de volley'], ['match', 'concert', 'concert', 'match']),
    ('Classez les billets de transport dans Transport et les cartes postales dans Carte.', ['transport', 'carte'], ['Billet de tramway', 'Carte postale de la montagne', 'Carte postale de la mer', 'Billet d’autocar'], ['transport', 'carte', 'carte', 'transport']),
    ('Classez les fiches de jardinage dans Jardin et les fiches de bricolage dans Bricolage.', ['jardin', 'bricolage'], ['Fiche de bricolage : réparer un tiroir', 'Fiche de jardinage : semer des radis', 'Fiche de bricolage : peindre une étagère', 'Fiche de jardinage : tailler un rosier'], ['bricolage', 'jardin', 'bricolage', 'jardin']),
]:
    ajouter('temps', consigne=consigne, categories=categories, documents=[{'id': f'd{i + 1}', 'texte': text} for i, text in enumerate(documents)], attendu_classement={f'd{i + 1}': value for i, value in enumerate(expected)})
