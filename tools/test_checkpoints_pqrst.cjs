// node --test tools/test_checkpoints_pqrst.cjs
const { test } = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const source = require('./frontend_source')();
function environnement(apiFetch) {
  const reponse = { '5': [], _pqrst: { phase: 'R' } };
  const c = { etat: { theme: { id: 'methodes' }, session: { session_id: 'session', items: [{ id: 'item', type: 'pqrst-mise-en-oeuvre' }] },
    indexItem: 0, checkpointsPqrst: new Map() }, snapshotPqrst: () => JSON.parse(JSON.stringify(reponse)), apiFetch };
  vm.createContext(c);
  vm.runInContext(source.slice(source.indexOf('function conserverCheckpointPqrst('), source.indexOf('function observationContexte(')), c);
  return { c, reponse };
}
test('snapshot avant nettoyage conservé après échec réseau puis envoyé au réessai', async () => {
  const appels = [];
  let echec = true;
  const { c, reponse } = environnement(async (url, options) => {
    appels.push({ url, corps: JSON.parse(options.body) });
    if (echec) throw { type: 'reseau' };
    return { enregistree: true };
  });
  c.conserverCheckpointPqrst();
  const checkpoint = [...c.etat.checkpointsPqrst.values()][0];
  await assert.rejects(checkpoint.promesse);
  c.snapshotPqrst = () => null;
  reponse._pqrst.phase = 'fin';
  assert.equal(c.etat.checkpointsPqrst.size, 1);
  echec = false;
  await c.sauvegarderCheckpointsPqrst();
  assert.equal(c.etat.checkpointsPqrst.size, 0);
  assert.deepEqual(appels[0], appels[1]);
  assert.equal(appels[1].corps.reponse._pqrst.phase, 'R');
});
test('la clôture attend le checkpoint déjà en cours', async () => {
  let terminer, appels = 0, fini = false;
  const { c } = environnement(() => { appels++; return new Promise(resolve => { terminer = resolve; }); });
  c.conserverCheckpointPqrst();
  const sauvegarde = c.sauvegarderCheckpointsPqrst().then(() => { fini = true; });
  await Promise.resolve();
  assert.equal(fini, false);
  assert.equal(appels, 1);
  terminer({ enregistree: true });
  await sauvegarde;
  assert.equal(fini, true);
});
