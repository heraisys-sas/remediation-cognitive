#!/usr/bin/env python3
"""Prépare une fois les 48 mots avec la voix locale Thomas (macOS).

AAC mono 32 kbit/s, fichiers mutualisés par mot. L'application servie n'a plus
besoin de synthèse vocale pour les stimuli. Les fichiers existants sont conservés.
Changer PROFIL pour renouveler volontairement la voix/le débit du corpus.
"""

try:
    from tools.generation import ecrire_json
except ModuleNotFoundError:
    from generation import ecrire_json
import hashlib
import re
import subprocess
import tempfile
from pathlib import Path
from generer_rappel_series import MOTS

ROOT=Path(__file__).resolve().parents[1]
PROFIL='fr-thomas-155-v1'
BASE=ROOT/'frontend/audio/series'/PROFIL

def nom_fichier(mot):
    return hashlib.sha256(f'{PROFIL}:{mot}'.encode()).hexdigest()[:16]+'.m4a'

def main():
    BASE.mkdir(parents=True,exist_ok=True)
    entrees={}
    with tempfile.TemporaryDirectory(prefix='audio-series-') as tmp:
        for mot in MOTS:
            chemin=BASE/nom_fichier(mot)
            if not chemin.exists():
                aiff=Path(tmp)/'mot.aiff'
                subprocess.run(['say','-v','Thomas','-r','155','-o',str(aiff),mot],check=True)
                resultat=subprocess.check_output(['afinfo',str(aiff)],text=True)
                if 'audio bytes: 0' in resultat:
                    raise RuntimeError('La synthèse locale a produit un fichier vide ; vérifier les permissions audio du processus.')
                subprocess.run(['afconvert','-f','m4af','-d','aac','-b','32000','-c','1',str(aiff),str(chemin)],check=True)
            info=subprocess.check_output(['afinfo',str(chemin)],text=True)
            duree=float(re.search(r'estimated duration:\s*([0-9.]+)',info).group(1))
            if duree<=0: raise RuntimeError(f'Audio vide : {mot}')
            entrees[mot]={'fichier':nom_fichier(mot),'duree_s':duree,'octets':chemin.stat().st_size}
    manifest={'profil':PROFIL,'voix':'Thomas (fr-FR)','debit_mots_min':155,
              'codec':'AAC mono 32 kbit/s','mots':entrees}
    ecrire_json(BASE/'manifest.json', manifest)
    print(f'{len(entrees)} mots, {sum(e["octets"] for e in entrees.values())} octets audio')

if __name__=='__main__': main()
