"""Correction orthographique stricte du segment commun, sans modèle sémantique."""
import unicodedata


def _normalize(value: str) -> str:
    return unicodedata.normalize('NFC', value.strip()).casefold()


def est_correct(item: dict, saisie: str) -> bool:
    """Accepte uniquement la réponse et les alternatives explicitement rédigées."""
    if not isinstance(saisie, str):
        return False
    response = item.get('reponse', {})
    expected = [response.get('valeur', ''), *response.get('variantes', [])]
    answer = _normalize(saisie)
    return bool(answer) and answer in {_normalize(word) for word in expected if isinstance(word, str)}
