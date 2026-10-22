const { test, expect } = require('@playwright/test');

const cartes = page => page.locator('#vue-themes .carte-theme:visible h3');
async function reglages(page) {
  await page.locator('#reglages-interface > summary').click();
  await page.locator('#reglages-difficultes > summary').click();
  await expect(page.getByRole('checkbox', { name: 'Mémoire immédiate', exact: true })).toBeVisible();
}
async function aucunDebordement(page) {
  const mesures = await page.evaluate(() => ({
    largeur: document.documentElement.clientWidth,
    contenu: document.documentElement.scrollWidth,
  }));
  expect(mesures.contenu).toBeLessThanOrEqual(mesures.largeur + 1);
}

test.beforeEach(async ({ page }) => {
  await page.goto('/ui/');
  await expect(page.getByRole('heading', { name: 'Déduction', exact: true })).toBeVisible();
});

test('catalogue complet, cases nommées et absence de débordement', async ({ page, request }, info) => {
  const reponse = await request.get('/api/entrainement/themes');
  expect(reponse.ok()).toBeTruthy();
  const { themes } = await reponse.json();
  const noms = themes.filter(t => t.id !== 'series-entendues').map(t => t.nom);
  expect((await cartes(page).allTextContents()).sort()).toEqual([
    ...noms, 'Mémoires immédiates', 'Application des stratégies', 'N-back : comparer les formes',
  ].sort());
  await aucunDebordement(page);
  await reglages(page);
  const cases = page.locator('#choix-difficultes input');
  await expect(cases).toHaveCount(9);
  for (const champ of await cases.all()) {
    await expect(champ).toBeChecked();
    await expect(champ).toHaveAccessibleName(/.+/);
    await expect(champ).toHaveAccessibleDescription(/Cartes :/);
  }
  await aucunDebordement(page);
  await page.screenshot({ path: info.outputPath('reglages.png'), fullPage: true });
});

test('sélection exacte, rechargement et rubriques préservées', async ({ page }, info) => {
  const mutations = [];
  page.on('request', req => {
    if (req.url().includes('/api/') && !['GET', 'HEAD'].includes(req.method())) mutations.push(req.url());
  });
  await reglages(page);
  await page.getByRole('button', { name: 'Tout masquer', exact: true }).click();
  await page.getByRole('checkbox', { name: 'Mémoire immédiate', exact: true }).check();
  const noms = ['Mémoires immédiates', 'Retenir et manipuler', 'Mémoriser des séries'];
  expect(await cartes(page).allTextContents()).toEqual(noms);
  await expect(page.locator('#section-evaluation')).toBeVisible();
  await expect(page.locator('#section-extra')).toBeHidden();
  await page.reload();
  await expect(cartes(page)).toHaveCount(3);
  expect(await cartes(page).allTextContents()).toEqual(noms);
  await aucunDebordement(page);
  await page.screenshot({ path: info.outputPath('accueil-filtre.png'), fullPage: true });
  expect(mutations).toEqual([]);
});

test('choix vide persistant avec accès direct aux réglages', async ({ page }) => {
  await reglages(page);
  await page.getByRole('button', { name: 'Tout masquer', exact: true }).click();
  await expect(cartes(page)).toHaveCount(0);
  await page.reload();
  await expect(page.locator('#accueil-filtre-vide')).toBeVisible();
  await expect(cartes(page)).toHaveCount(0);
  await page.getByRole('button', { name: 'Choisir mes activités' }).click();
  await expect(page.locator('#reglages-difficultes > summary')).toBeFocused();
  await page.getByRole('button', { name: 'Tout afficher', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Déduction', exact: true })).toBeVisible();
});

test('stockage refusé : dernier choix appliqué et erreur lisible', async ({ page }) => {
  await reglages(page);
  await page.getByRole('button', { name: 'Tout masquer', exact: true }).click();
  await page.getByRole('checkbox', { name: 'Trouver ses mots', exact: true }).check();
  // Panne synthétique, limitée à cette clé et à ce contexte de navigateur jetable.
  await page.evaluate(() => {
    const sauvegarder = Storage.prototype.setItem;
    Storage.prototype.setItem = function (cle, valeur) {
      if (cle === 'orthogone.accueil.difficultes.v1') throw new DOMException('Refus synthétique', 'QuotaExceededError');
      return sauvegarder.call(this, cle, valeur);
    };
  });
  await page.getByRole('checkbox', { name: 'Raisonner et calculer', exact: true }).click();
  await expect(page.getByRole('checkbox', { name: 'Raisonner et calculer', exact: true })).not.toBeChecked();
  await expect(page.locator('#erreur-difficultes')).toBeVisible();
  expect(await cartes(page).allTextContents()).toEqual(['Retrouver des mots et leur contexte', 'Débuts de mots communs']);
  await page.reload();
  await expect(cartes(page)).toHaveCount(2);
  expect(await cartes(page).allTextContents()).toEqual(['Retrouver des mots et leur contexte', 'Débuts de mots communs']);
});

test('recouvrements et interactions rapides sans doublons', async ({ page }) => {
  await reglages(page);
  await page.getByRole('button', { name: 'Tout masquer', exact: true }).click();
  const attention = page.getByRole('checkbox', { name: 'Concentration et attention', exact: true });
  const adaptation = page.getByRole('checkbox', { name: 'S’adapter et vérifier ses actions', exact: true });
  await attention.check(); await adaptation.check();
  for (let i = 0; i < 3; i++) { await attention.uncheck(); await attention.check(); }
  const noms = await cartes(page).allTextContents();
  expect(noms.length).toBe(new Set(noms).size);
  expect(noms.sort()).toEqual(['Méthodes pour retenir et s’organiser', 'Actualiser une consigne', 'Comparer deux documents', 'Repérer l’essentiel', 'Garder le cap', 'Application des stratégies'].sort());
});

test('commande native au clavier et aucune erreur JavaScript', async ({ page }) => {
  const erreurs = [];
  page.on('pageerror', erreur => erreurs.push(erreur.message));
  await reglages(page);
  await page.getByRole('button', { name: 'Tout masquer', exact: true }).click();
  const champ = page.getByRole('checkbox', { name: 'Trouver ses mots', exact: true });
  await champ.focus(); await champ.press('Space');
  await expect(champ).toBeChecked();
  await expect(champ).toBeFocused();
  expect(await cartes(page).allTextContents()).toEqual(['Retrouver des mots et leur contexte', 'Débuts de mots communs']);
  expect(erreurs).toEqual([]);
});
