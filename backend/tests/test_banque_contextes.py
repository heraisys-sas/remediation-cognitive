"""Banque illustrée : assets légers, archives stables et régénération."""
import hashlib
import json
from pathlib import Path

from tools import generer_evocation

ROOT = Path(__file__).resolve().parents[2]


def test_banque_contextes_images_et_regeneration():
    items = json.loads((ROOT / 'content/entrainement/evocation/paliers/palier-04.json').read_text())
    scenes = json.loads((ROOT / 'frontend/images/contextes/manifest.json').read_text())['scenes']
    assert len(items) == len(scenes) == 20
    assert len({item['id'] for item in items}) == 20
    assert hashlib.sha256(json.dumps(items[:10], ensure_ascii=False, sort_keys=True).encode()).hexdigest() == '7df3a058cf891fe364798caced860a667bfa7c15f695ac5665c6bfb42d241d9c'
    for item, scene in zip(items, scenes, strict=True):
        assert item['id'] == scene['id']
        assert item['reponse']['valeur'] == scene['contexte']
        assert item['contenu']['affichage']['elements'] == [['', scene['message']]]
        assert item['contenu']['affichage']['image'] == scene['image']
        assert len(set(item['contenu']['options'])) == 4
        assert item['reponse']['valeur'] in item['contenu']['options']
        image = ROOT / 'frontend' / scene['image']['src']
        assert hashlib.sha256(image.read_bytes()).hexdigest() == scene['image']['sha256']
        for width in (640, 960):
            version = 'v1' if scene['numero'] <= 10 else 'v2'
            path = ROOT / f"frontend/images/contextes/source-{scene['numero']:02d}-{version}-{width}.webp"
            assert path.stat().st_size == scene[f'poids_{width}']
            assert path.read_bytes()[:4] == b'RIFF'
            if version == 'v2':
                assert path.stat().st_size <= (45000 if width == 640 else 75000)
    generer_evocation._RNG_FAMILLES.clear()
    generated = [item for item in generer_evocation.items_evocation() if item['palier'] == 4]
    assert generated == items
