const { test, expect } = require('@playwright/test');

test('commandes audio compactes : micro dans le champ et état visible', async ({ page }, info) => {
  await page.addInitScript(() => {
    localStorage.setItem('remediation.lectureAuto', 'off');
    localStorage.setItem('remediation.sansLimiteSessions', 'on');
    localStorage.setItem('orthogone.rejouerPalier', 'on');
  });
  await page.goto('/ui/');
  await expect(page.getByRole('heading', { name: 'Calcul mental', exact: true })).toBeVisible();
  await page.evaluate(() => {
    CAPACITES.voixDisponible = () => true;
    CAPACITES.syntheseDisponible = () => true;
    CAPACITES.dicter = callbacks => {
      callbacks.onDebut();
      return { stop() { callbacks.onFin(); } };
    };
  });
  await page.locator('.carte-theme').filter({ has: page.getByRole('heading', { name: 'Calcul mental', exact: true }) }).getByRole('button', { name: 'Commencer', exact: true }).click();
  const micro = page.locator('#bouton-dicter');
  await expect(micro).toBeVisible();
  await expect(micro).toHaveAccessibleName(/Répondre à voix haute|Dicter/);
  const inputBox = await page.locator('#champ-reponse').boundingBox();
  const micBox = await micro.boundingBox();
  expect(micBox.x).toBeGreaterThan(inputBox.x);
  expect(micBox.x + micBox.width).toBeLessThanOrEqual(inputBox.x + inputBox.width);
  expect(micBox.width).toBeGreaterThanOrEqual(44);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1)).toBeTruthy();
  await page.screenshot({ path: info.outputPath('commandes-audio.png'), fullPage: true });
  await micro.click();
  await expect(page.locator('#statut-dictee')).toHaveText('Parle maintenant · Terminer la dictée');
  await page.screenshot({ path: info.outputPath('dictee-active.png'), fullPage: true });
  await micro.click();
  await expect(page.locator('#statut-dictee')).toBeHidden();
  const audio = page.locator('#bouton-ecouter');
  await expect(audio).toBeVisible();
  await expect(audio).toHaveAccessibleName('Écouter');
  expect((await audio.boundingBox()).width).toBeLessThanOrEqual(64);
  const iconWidth = await audio.evaluate(el => parseFloat(getComputedStyle(el, '::before').width));
  expect(iconWidth).toBeGreaterThanOrEqual(20);
  await page.screenshot({ path: info.outputPath('commandes-verifiees.png'), fullPage: true });
});
