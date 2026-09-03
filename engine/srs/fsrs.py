"""Répétition espacée FSRS (successeur open-source de SM-2).

Implémentation : s'appuyer sur une bibliothèque FSRS éprouvée plutôt que
réimplémenter l'algorithme. Cette interface fixe le contrat attendu par le
moteur de session (decks : tables, vocabulaire, commandes Python).
"""


class CarteFSRS:
    """Item déclaratif (table, verbe, commande Python) et son état FSRS."""

    def __init__(self, item_id: str) -> None:
        self.item_id = item_id
        self.stabilite: float = 0.0
        self.difficulte: float = 5.0
        self.echeance: str | None = None  # ISO-8601
