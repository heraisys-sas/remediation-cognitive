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


def test_plans_documents_visibles_et_options_cliquables():
    items = json.loads((ROOT / 'content/entrainement/methodes/paliers/palier-04.json').read_text())
    documents = json.loads((ROOT / 'content/entrainement/methodes/paliers/palier-05.json').read_text())
    items = [entry for pair in zip(items, documents) for entry in pair] + items[:1]
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
function aideGeneriquePourItem(item) {return item.contenu.aide || ''}
function textePourLectureDeduction() {return ''}
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
  if (item.type === 'reperer-info') {
    assert.equal(nodes[0].tag, 'section');
    assert.equal(nodes[0].children[1].texte, item.contenu.document);
  } else {
    assert.equal(nodes[0].tag, 'ol');
    assert.deepEqual(nodes[0].children.map(x => x.texte), item.contenu.plan);
  }
  assert.equal(nodes.length, 4); // pas de document/plan résiduel du précédent item
  assert.deepEqual(nodes.slice(1).map(x => x.texte), item.contenu.options);
  nodes[1].click();
  assert.equal(valeur, item.contenu.options[0]);
}
'''
    node = shutil.which('node')
    assert node, 'Node requis pour vérifier le rendu réel des fonctions JS'
    subprocess.run([node, '-e', script], check=True, capture_output=True, text=True)


def test_indices_lexicaux_se_rendent_sans_variable_de_grille():
    """Un rappel avec indices doit démarrer même hors d'une grille de déduction."""
    item = next(
        item
        for path in (ROOT / 'content/entrainement/evocation/paliers').glob('palier-*.json')
        for item in json.loads(path.read_text())
        if item.get('contenu', {}).get('indices')
    )
    script = '''
const assert = require('node:assert/strict');
function creerElement(tag, attrs = {}, ...children) {
  return {tag, ...attrs, children,
    append(...c) {this.children.push(...c)},
    replaceChildren(...c) {this.children = c},
    addEventListener(event, cb) {this[event] = cb}};
}
const refs={zoneIndices:creerElement('div')};
const etat={repondu:false,actionEnCours:false,indicesReveles:0};
let soumis=false;
function soumettreValeur(){soumis=true}
'''
    script += '\nfunction rendreIndices(item) ' + corps_fonction(SOURCE, 'rendreIndices')
    script += '\nconst item=' + json.dumps(item) + ''';
rendreIndices(item);
const [statut,liste,bouton]=refs.zoneIndices.children;
assert.equal(bouton.texte,'Un indice');
assert.equal(liste.children.length,0);
bouton.click();
assert.equal(liste.children.length,1);
assert.equal(liste.children[0].texte,item.contenu.indices[0].texte);
assert.equal(soumis,false);
'''
    node = shutil.which('node')
    assert node, 'Node requis pour vérifier le rendu réel des fonctions JS'
    subprocess.run([node, '-e', script], check=True, capture_output=True, text=True)


def test_deduction_masque_le_coup_de_pouce_et_prepare_tous_les_indices_a_lire():
    item = json.loads(
        (ROOT / 'content/entrainement/deduction/paliers/palier-02.json').read_text()
    )[0]
    affichage = corps_fonction(SOURCE, 'afficherQuestion')
    assert 'aideGeneriquePourItem(item)' in affichage
    assert 'textePourLectureDeduction(contenu)' in affichage

    script = '''
const assert=require('node:assert/strict');
'''
    script += '\nfunction aideGeneriquePourItem(item) ' + corps_fonction(
        SOURCE, 'aideGeneriquePourItem'
    )
    script += '\nfunction textePourLectureDeduction(contenu, formateur) ' + corps_fonction(
        SOURCE, 'textePourLectureDeduction'
    )
    script += '\nconst item=' + json.dumps(item) + ''';
assert.equal(aideGeneriquePourItem(item),'');
assert.equal(aideGeneriquePourItem({type:'autre',contenu:{aide:'  Aide utile.  '}}),'Aide utile.');
let vus=[];
const texte=textePourLectureDeduction(item.contenu,(indice,n)=>{
  vus.push({indice,n}); return `Indice lu ${vus.length}.`;
});
assert.equal(vus.length,item.contenu.enonces.length);
assert.ok(vus.every(v=>v.n===item.contenu.figures.length));
assert.ok(texte.startsWith(item.contenu.consigne+' Indices.'));
for(let i=1;i<=vus.length;i++) assert.ok(texte.includes(`Indice lu ${i}.`));
'''
    node = shutil.which('node')
    assert node, 'Node requis pour vérifier le rendu réel des fonctions JS'
    subprocess.run([node, '-e', script], check=True, capture_output=True, text=True)
