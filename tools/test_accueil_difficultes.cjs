const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
class Element {
  constructor(tag) { this.tag=tag; this.children=[]; this.dataset={}; this.events={}; this.hidden=false; this.checked=false; this.textContent=''; this.attributes={}; }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children=nodes; }
  setAttribute(key,value) { this.attributes[key]=value; }
  addEventListener(event,fn) { this.events[event]=fn; }
  querySelectorAll(tag) { return this.children.flatMap(n=>[...(n.tag===tag?[n]:[]),...n.querySelectorAll(tag)]); }
  querySelector(tag) { return this.querySelectorAll(tag)[0] || null; }
  focus() { this.focused=true; }
  change(checked) { this.checked=checked; this.events.change(); }
}
const allIds=['calcul-mental','anglais','python','memoire','rappel-series','actualiser-consigne','comparer-documents','reperer-essentiel','quotidien','deduction','methodes','garder-cap','evocation','memoires-immediates','strategies','nback'];
function setup(saved=null, ids=allIds) {
  const nodes=new Map(), data=new Map(), writes=[]; let refus=false;
  if(saved!==null)data.set('orthogone.accueil.difficultes.v1',saved);
  const get=id=>{if(!nodes.has(id))nodes.set(id,new Element('div'));return nodes.get(id);};
  for(const id of ['reglages-interface','reglages-difficultes'])get(id).append(new Element('summary'));
  for(const id of ids){const card=new Element('article');card.dataset.activite=id;const title=new Element('h3');title.textContent=id;card.append(title);get(['memoire','rappel-series','nback'].includes(id)?'liste-themes-evaluation':['anglais','python'].includes(id)?'liste-themes-extra':'liste-themes').append(card);}
  const storage={getItem:key=>data.get(key)??null,setItem(key,value){if(refus)throw Error('refus');data.set(key,value);writes.push([key,value]);}};
  const ctx={document:{getElementById:get,createElement:tag=>new Element(tag)},window:{localStorage:storage}};
  vm.createContext(ctx); vm.runInContext(fs.readFileSync('frontend/src/accueil-difficultes.js','utf8')+'\nthis.api=AccueilDifficultes;',ctx);
  ctx.api.initialiser();ctx.api.actualiser();
  return {api:ctx.api,get,data,writes,deny:()=>refus=true,inputs:()=>get('choix-difficultes').querySelectorAll('input'),button:text=>get('choix-difficultes').querySelectorAll('button').find(n=>n.textContent===text),cards:()=>['liste-themes','liste-themes-evaluation','liste-themes-extra'].flatMap(id=>get(id).children),visible:()=>['liste-themes','liste-themes-evaluation','liste-themes-extra'].flatMap(id=>get(id).children).filter(n=>!n.hidden).map(n=>n.dataset.activite)};
}
test('défaut : catalogue complet, correspondances explicites et aucune écriture',()=>{
 const e=setup();assert.equal(e.visible().length,allIds.length);assert.equal(e.inputs().length,9);assert.equal(e.writes.length,0);
 const covered=new Set(e.api.groupesPour(allIds.map(id=>({id}))).flatMap(g=>g.cartes));for(const id of allIds)assert(covered.has(id));
});
test('choix vide conservé après rechargement, sections cachées et accès aux réglages',()=>{
 const e=setup('[]');assert.equal(e.visible().length,0);assert.equal(e.get('accueil-filtre-vide').hidden,false);assert(e.get('section-extra').hidden);assert(e.get('section-evaluation').hidden);
 e.get('ouvrir-choix-difficultes').events.click();assert(e.get('reglages-interface').open);assert(e.get('reglages-difficultes').querySelector('summary').focused);
});
test('cocher immédiatement mémorise et affiche uniquement les cartes annoncées',()=>{
 const e=setup('[]');e.inputs().find(n=>n.value==='immediat').change(true);
 assert.deepEqual(e.visible().sort(),['memoires-immediates','memoire','rappel-series'].sort());assert.equal(e.writes.length,1);
 const reloaded=setup(e.writes[0][1]);assert.deepEqual(reloaded.visible(),e.visible());
});
test('recouvrements sans duplication et changements rapides sans recréer les cartes',()=>{
 const e=setup('[]'),cards=e.cards();e.inputs().find(n=>n.value==='attention').change(true);e.inputs().find(n=>n.value==='adaptation').change(true);
 assert.equal(e.visible().length,new Set(e.visible()).size);assert.deepEqual(e.cards(),cards);
 for(let i=0;i<10;i++)e.inputs().find(n=>n.value==='mots').change(i%2===0);
 assert(!e.visible().includes('evocation'));
});
test('stockage refusé : choix et cases restaurés, erreur visible, pas de progression touchée',()=>{
 const e=setup('["mots"]');e.deny();e.inputs().find(n=>n.value==='raisonnement').change(true);
 assert.deepEqual(e.visible(),['evocation']);assert(!e.inputs().find(n=>n.value==='raisonnement').checked);assert(!e.get('erreur-difficultes').hidden);assert.equal(e.writes.length,0);
});
test('catalogue incomplet et activité nouvelle : pas de carte fantôme ni omission par défaut',()=>{
 const e=setup(null,['deduction','nouveau']);assert.equal(e.inputs().length,2);assert(e.inputs().some(n=>n.value==='autres'));
 assert.deepEqual(e.visible(),['deduction','nouveau']);e.api.actualiser();assert.equal(e.inputs().length,2);
});
test('préférence corrompue revient au catalogue complet sans réécrire le stockage',()=>{
 for(const saved of ['invalid','{}','[1]']){const e=setup(saved);assert.equal(e.visible().length,allIds.length);assert.equal(e.writes.length,0);}
});
test('tout masquer/afficher et chargement sans carte restent utilisables',()=>{
 const e=setup();e.button('Tout masquer').events.click();assert.equal(e.visible().length,0);e.button('Tout afficher').events.click();assert.equal(e.visible().length,allIds.length);
 const empty=setup(null,[]);assert(empty.get('accueil-filtre-vide').hidden);assert.equal(empty.writes.length,0);
});
