const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const path = require('node:path');

function original(theme, item) {
  const file = path.join(__dirname, '../../content/entrainement', theme, 'paliers', `palier-${String(item.palier).padStart(2, '0')}.json`);
  return JSON.parse(fs.readFileSync(file, 'utf8')).find(i => i.id === item.id);
}
async function start(page, theme, title) {
  await page.addInitScript(() => {
    localStorage.setItem('remediation.lectureAuto', 'off');
    // Serveur éphémère partagé par les quatre projets navigateur : rejouer explicitement.
    localStorage.setItem('remediation.sansLimiteSessions', 'on');
    localStorage.setItem('orthogone.rejouerPalier', 'on');
  });
  await page.goto('/ui/');
  const response = page.waitForResponse(r => r.url().endsWith(`/${theme}/sessions`) && r.request().method() === 'POST');
  await page.locator('.carte-theme').filter({ has: page.getByRole('heading', { name: title, exact: true }) }).getByRole('button', { name: 'Commencer', exact: true }).click();
  return (await (await response).json()).items[0];
}

test('segment écrit : clavier, correction et question suivante', async ({ page }) => {
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  const item = await start(page, 'debut-commun', 'Débuts de mots communs');
  expect(item.palier).toBe(2);
  expect(item.contenu.debut_commun.mots).toBeUndefined();
  await page.locator('#champ-reponse').fill(original('debut-commun', item).reponse.valeur);
  await page.locator('#bouton-valider').click();
  await expect(page.locator('#carte-feedback')).toBeVisible();
  await expect(page.locator('#bouton-suivant')).toBeVisible();
  await page.locator('#bouton-suivant').click();
  await expect(page.locator('#champ-reponse')).toHaveValue('');
  expect(errors).toEqual([]);
});

test('logigramme : liens réversibles, doublons signalés et correction', async ({ page }) => {
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  const item = await start(page, 'logigrammes', 'Croiser les indices');
  const solution = original('logigrammes', item).reponse.associations;
  const [anchor, ...categories] = item.contenu.categories;
  const button = page.getByRole('button', { name: 'Vérifier mes liens' });
  await expect(button).toBeDisabled();
  for (const row of anchor.valeurs) {
    for (const cat of categories) {
      await page.getByRole('combobox', { name: `${row} — ${cat.label}`, exact: true }).selectOption(solution[row][cat.id]);
    }
  }
  const first = page.getByRole('combobox', { name: `${anchor.valeurs[0]} — ${categories[0].label}`, exact: true });
  await first.selectOption(solution[anchor.valeurs[1]][categories[0].id]);
  await expect(page.locator('#zone-sequence [role=status]')).toContainText(/plusieurs|doublon|fois/i);
  await first.selectOption(solution[anchor.valeurs[0]][categories[0].id]);
  await button.click();
  await expect(page.locator('#carte-feedback')).toBeVisible();
  await expect(page.locator('#bouton-suivant')).toBeVisible();
  await expect(first).toBeDisabled();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1)).toBeTruthy();
  expect(errors).toEqual([]);
});
