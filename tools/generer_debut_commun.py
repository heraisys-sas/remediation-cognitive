"""Corpus original de recherche d'un segment écrit commun (POC adulte)."""
from pathlib import Path
import unicodedata

try:
    from tools.generation import ecrire_json, arguments_generation
except ModuleNotFoundError:
    from generation import ecrire_json, arguments_generation

ROOT = Path(__file__).resolve().parent.parent
# Segment, fin 1, genre 1, définition 1, fin 2, genre 2, définition 2.
BANK = [
    [
        ('ca', 'fé', 'm', 'Boisson chaude obtenue à partir de grains torréfiés.', 'nard', 'm', 'Oiseau aquatique au bec large.'),
        ('cha', 'peau', 'm', 'Accessoire porté sur la tête pour se protéger du soleil.', 'riot', 'm', 'Véhicule à roues servant à transporter des charges.'),
        ('bou', 'gie', 'f', 'Objet en cire que l’on allume pour éclairer.', 'ton', 'm', 'Petite pièce qui ferme un vêtement.'),
        ('car', 'te', 'f', 'Document qui représente un territoire.', 'ton', 'm', 'Matière rigide utilisée pour fabriquer des emballages.'),
        ('pa', 'nier', 'm', 'Récipient à anse pour porter des courses.', 'quet', 'm', 'Ensemble d’objets enveloppés pour être transportés.'),
        ('mar', 'teau', 'm', 'Outil utilisé pour enfoncer un clou.', 'ché', 'm', 'Lieu où des commerçants vendent leurs produits sur des étals.'),
        ('cou', 'teau', 'm', 'Ustensile à lame pour couper les aliments.', 'ssin', 'm', 'Objet rembourré posé sur un siège pour le confort.'),
        ('pla', 'teau', 'm', 'Support plat pour transporter des verres.', 'card', 'm', 'Meuble fermé destiné au rangement.'),
        ('ri', 'deau', 'm', 'Pièce de tissu suspendue devant une fenêtre.', 'vière', 'f', 'Cours d’eau naturel qui rejoint un autre cours d’eau.'),
        ('ba', 'teau', 'm', 'Moyen de transport qui flotte sur l’eau.', 'lai', 'm', 'Instrument à manche pour nettoyer le sol.'),
        ('sa', 'von', 'm', 'Produit utilisé avec de l’eau pour se laver.', 'coche', 'f', 'Petit sac souvent muni d’une bandoulière.'),
        ('ta', 'pis', 'm', 'Pièce de tissu épais posée sur le sol.', 'ble', 'f', 'Meuble sur lequel on pose son repas.'),
    ],
    [
        ('jour', 'nal', 'm', 'Publication qui présente l’actualité.', 'née', 'f', 'Période comprise entre le matin et le soir.'),
        ('comp', 'te', 'm', 'Relevé bancaire associé à un titulaire.', 'as', 'm', 'Instrument à deux branches pour tracer des cercles.'),
        ('gar', 'age', 'm', 'Local destiné à abriter un véhicule.', 'dien', 'm', 'Personne chargée de surveiller un bâtiment.'),
        ('port', 'efeuille', 'm', 'Petit étui pour ranger billets et cartes.', 'ail', 'm', 'Grande porte à l’entrée d’une propriété.'),
        ('con', 'trat', 'm', 'Accord écrit qui engage ses signataires.', 'gé', 'm', 'Période d’absence autorisée du travail.'),
        ('four', 'chette', 'f', 'Ustensile à dents utilisé pour manger.', 'gon', 'm', 'Véhicule fermé destiné au transport de marchandises.'),
        ('mon', 'tre', 'f', 'Petit instrument porté au poignet pour lire l’heure.', 'naie', 'f', 'Pièces et billets utilisés pour payer.'),
        ('cou', 'rrier', 'm', 'Ensemble des lettres reçues ou envoyées.', 'loir', 'm', 'Passage intérieur qui dessert plusieurs pièces.'),
        ('pla', 'fond', 'm', 'Surface supérieure d’une pièce.', 'ge', 'f', 'Étendue de sable ou de galets au bord de l’eau.'),
        ('re', 'çu', 'm', 'Document attestant qu’un paiement a été effectué.', 'pas', 'm', 'Ensemble des aliments consommés à une même occasion.'),
        ('dé', 'pôt', 'm', 'Lieu où sont entreposées des marchandises.', 'lai', 'm', 'Temps accordé pour effectuer une démarche.'),
        ('épi', 'ce', 'f', 'Substance végétale aromatique utilisée pour assaisonner les aliments.', 'cerie', 'f', 'Commerce de proximité vendant des produits alimentaires courants.'),
    ],
    [
        ('pré', 'avis', 'm', 'Délai à respecter entre l’annonce d’un départ et sa prise d’effet.', 'caution', 'f', 'Mesure prise pour éviter un risque.'),
        ('ré', 'serve', 'f', 'Quantité conservée pour un besoin ultérieur.', 'cit', 'm', 'Présentation orale ou écrite d’événements.'),
        ('trans', 'port', 'm', 'Déplacement de personnes ou de marchandises.', 'ition', 'f', 'Passage progressif d’une situation à une autre.'),
        ('con', 'signe', 'f', 'Instruction précise à appliquer pour une tâche.', 'stat', 'm', 'Document qui décrit des faits observés, par exemple après un accident.'),
        ('dis', 'cours', 'm', 'Prise de parole structurée devant un public.', 'tance', 'f', 'Espace qui sépare deux lieux.'),
        ('pro', 'jet', 'm', 'Action que l’on prévoit de réaliser avec un objectif.', 'grès', 'm', 'Amélioration obtenue par rapport à une situation antérieure.'),
        ('ac', 'cord', 'm', 'Entente entre plusieurs personnes.', 'ompte', 'm', 'Premier versement effectué avant le règlement complet.'),
        ('ap', 'pel', 'm', 'Communication téléphonique que l’on établit.', 'port', 'm', 'Contribution fournie à une activité commune.'),
        ('dé', 'marche', 'f', 'Formalité entreprise pour obtenir un document ou un droit.', 'bat', 'm', 'Échange organisé d’arguments sur une question.'),
        ('ex', 'trait', 'm', 'Court passage tiré d’un texte plus long.', 'amen', 'm', 'Observation attentive destinée à vérifier un état ou une situation.'),
        ('sou', 'tien', 'm', 'Aide apportée à une personne face à une difficulté.', 'hait', 'm', 'Désir que quelque chose se réalise.'),
        ('com', 'promis', 'm', 'Accord obtenu grâce à des concessions réciproques.', 'merce', 'm', 'Activité d’achat et de vente de produits.'),
    ],
]


# Aides supplémentaires : associations de sens, puis contexte du second nom.
HINTS = [
    [('On peut le boire avec du lait.', 'On le rencontre sur un étang.'),
     ('Il peut avoir un bord et une calotte.', 'On le pousse dans un magasin.'),
     ('Elle possède une mèche.', 'Il passe dans une boutonnière.'),
     ('Elle peut être routière.', 'On en fait des boîtes de déménagement.'),
     ('On peut y mettre des fruits.', 'On peut le remettre à la poste.'),
     ('Sa tête frappe le clou.', 'On y achète des légumes à un étal.'),
     ('On l’utilise avec une fourchette.', 'On le place parfois derrière son dos.'),
     ('On y pose des tasses avant de servir.', 'On y range des vêtements sur des étagères.'),
     ('On le tire pour masquer la lumière.', 'Elle coule entre deux rives.'),
     ('Il peut avoir une voile.', 'On le passe avant la serpillière.'),
     ('Il mousse quand on le frotte.', 'Elle se porte sur l’épaule.'),
     ('Il peut couvrir un parquet.', 'Elle comporte souvent quatre pieds.')],
    [('On peut le lire chaque matin.', 'Elle dure du lever au coucher du soleil.'),
     ('On y consulte son solde.', 'Une branche porte une pointe, l’autre un crayon.'),
     ('On y gare sa voiture.', 'Il veille aux accès de l’immeuble.'),
     ('On le glisse souvent dans une poche.', 'On l’ouvre pour entrer avec sa voiture.'),
     ('On le signe avant de commencer certains emplois.', 'On peut en prendre pour partir en vacances.'),
     ('Elle accompagne le couteau à table.', 'Il possède un espace de chargement à l’arrière.'),
     ('Elle comporte un cadran.', 'On peut en rendre après un achat payé en espèces.'),
     ('Le facteur le distribue.', 'Les portes des chambres peuvent donner sur lui.'),
     ('On lève les yeux pour le voir.', 'On peut y installer un parasol.'),
     ('On le garde comme preuve de règlement.', 'Le déjeuner en est un exemple.'),
     ('On peut y stocker du matériel.', 'Il peut expirer à une date fixée.'),
     ('Le cumin en est une.', 'On peut y acheter de l’huile et des pâtes.')],
    [('Il peut précéder la fin d’un bail.', 'Vérifier une issue avant de partir en est une.'),
     ('On y puise quand les provisions courantes manquent.', 'Il peut raconter un voyage.'),
     ('Il peut être ferroviaire.', 'Elle relie deux étapes différentes.'),
     ('On la lit avant de commencer.', 'Deux conducteurs peuvent le remplir ensemble.'),
     ('Un orateur le prononce.', 'On peut la mesurer en kilomètres.'),
     ('On le prépare avant de passer à l’action.', 'On en fait quand on maîtrise mieux une tâche.'),
     ('On peut le conclure après une discussion.', 'On le déduit du montant restant à payer.'),
     ('On peut le recevoir sur son téléphone.', 'Chacun peut fournir le sien à un projet collectif.'),
     ('On peut l’effectuer en mairie.', 'Les participants y défendent leurs points de vue.'),
     ('On peut le citer entre guillemets.', 'Il peut porter sur un dossier ou une demande.'),
     ('Un proche peut l’apporter dans une période difficile.', 'On peut le formuler pour l’avenir.'),
     ('Chaque partie y renonce à une partie de ses demandes.', 'Une boutique permet de l’exercer.')],
]


def items_debut_commun():
    """Retourne 36 paires inédites ; aucune transformation orthographique implicite."""
    items = []
    for level, rows in enumerate(BANK, 1):
        for number, (start, end1, gender1, clue1, end2, gender2, clue2) in enumerate(rows, 1):
            words = [start + end1, start + end2]
            assert all(unicodedata.normalize('NFC', word) == word for word in words)
            length = f' Le début contient {len(start)} lettres.' if level == 1 else ''
            items.append({
                'id': f'dc-{level}-{number:02d}', 'module': 'entrainement',
                'theme': 'debut-commun', 'type': 'rappel-indice', 'palier': level,
                'fonctions_ciblees': ['acces-lexical', 'recuperation'],
                'contenu': {
                    'consigne': 'Écris le même début devant les deux fins pour former deux noms. Les aides donnent leurs sens.',
                    'enonce': f'…{end1} (nom {"masculin" if gender1 == "m" else "féminin"})\n…{end2} (nom {"masculin" if gender2 == "m" else "féminin"})' + length,
                    'aide': None,
                    'methode': 'Cherche un premier nom, puis vérifie le même début avec l’autre fin et le genre indiqué. Utilise une aide de sens si nécessaire. Les accents comptent.',
                    'debut_commun': {'terminaisons': [end1, end2], 'mots': words,
                                     'genres': [gender1, gender2], 'definitions': [clue1, clue2]},
                    'indices': [
                        {'type': 'semantique', 'texte': clue1 + ' ' + HINTS[level - 1][number - 1][0]},
                        {'type': 'semantique', 'texte': clue2 + ' ' + HINTS[level - 1][number - 1][1]},
                        {'type': 'orthographique', 'texte': f'Le début recherché commence par « {start[0]} ».'},
                    ],
                },
                'reponse': {'valeur': start, 'variantes': []},
                'prerequis': [], 'cap_complexite': 'Deux noms et un segment écrit ; recherche sans chronomètre.',
                'meta': {'auteur': 'redaction-assistee (corpus original debut commun)',
                         'date_creation': '2026-10-22', 'relecture_ortho': {'statut': 'a_revoir'}},
            })
    return items


def ecrire(dry_run=False):
    for level in range(1, 4):
        ecrire_json(ROOT / f'content/entrainement/debut-commun/paliers/palier-{level:02d}.json',
                    [item for item in items_debut_commun() if item['palier'] == level], dry_run=dry_run)


if __name__ == '__main__':
    ecrire(arguments_generation(__doc__).dry_run)
