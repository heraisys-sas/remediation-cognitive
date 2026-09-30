"""Les contenus à propositions doivent être jouables, notamment les plans GMT."""
import json
import re
import shutil
import subprocess
from pathlib import Path

from tools.verifier_interface import corps_fonction

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'frontend/src/app.js').read_text()
CHOIX = re.search(r'const TYPES_A_CHOIX = new Set\(\[(.*?)\]\);', SOURCE, re.S).group(0)


def test_tous_les_types_avec_options_sont_rendus_en_choix():
    types = set(re.findall(r'"([^"]+)"', CHOIX))
    for path in (ROOT / 'content').rglob('*.json'):
        data = json.loads(path.read_text())
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get('contenu', {}).get('options'):
                    assert item['type'] in types, (path, item['id'])


def test_huit_plans_visibles_et_options_cliquables():
    items = json.loads((ROOT / 'content/entrainement/methodes/paliers/palier-04.json').read_text())
    script = CHOIX + '\n' + '''
const assert = require('node:assert/strict');
function element(tag, attrs = {}, ...children) {
  return {tag, ...attrs, children, hidden: false,
    append(...c) {this.children.push(...c)},
    replaceChildren(...c) {this.children = c},
    setAttribute() {}, focus() {},
    addEventListener(event, cb) {this[event] = cb},
    querySelector() {return null}};
}
const creerElement = element;
const refs = new Proxy({}, {get(obj,key) {return obj[key] ??= element('div')}});
const etat = {consignesVues: new Set(), theme: {id:'methodes'}};
const CAPACITES = {arreter(){}, syntheseDisponible(){return false}, voixDisponible(){return false}};
const THEMES_SANS_DICTEE = new Set();
function annulerMemo() {}
function viderZonesReponse() {refs.zoneChoix.replaceChildren()}
function lireSiLectureAuto() {}
function inputmodePour() {return 'text'}
function reglerEtatBoutons() {}
let valeur;
function soumettreValeur(v) {valeur = v}
'''
    for name in ('afficherQuestion', 'rendreOptions'):
        args = 'item' if name == 'afficherQuestion' else 'options, item'
        script += f'\nfunction {name}({args}) ' + corps_fonction(SOURCE, name)
    script += '\nconst items = ' + json.dumps(items) + ''';
for (const item of items) {
  afficherQuestion(item);
  assert.equal(refs.formulaire.hidden, true);
  assert.equal(refs.zoneChoix.hidden, false);
  const nodes = refs.zoneChoix.children[0].children;
  assert.equal(nodes[0].tag, 'ol');
  assert.deepEqual(nodes[0].children.map(x => x.texte), item.contenu.plan);
  assert.deepEqual(nodes.slice(1).map(x => x.texte), item.contenu.options);
  nodes[1].click();
  assert.equal(valeur, item.contenu.options[0]);
}
'''
    node = shutil.which('node')
    assert node, 'Node requis pour vérifier le rendu réel des fonctions JS'
    subprocess.run([node, '-e', script], check=True, capture_output=True, text=True)
