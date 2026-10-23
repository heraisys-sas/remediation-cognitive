const { test, expect } = require('@playwright/test');

test('Contextes propose deux conditions et rappelle uniquement les sources découvertes', async ({ page }) => {
  await page.route('**/api/entrainement/evocation/sessions', route => route.continue({
    postData: JSON.stringify({ ...route.request().postDataJSON(), sans_limite_sessions: true }),
  }));
  await page.goto('/ui/');
  const carte = page.locator('[data-activite="evocation"]');
  await carte.getByText('Choisir le parcours', { exact: true }).click();
  await carte.getByRole('combobox', { name: /Parcours pour/ }).selectOption('memoire-source');
  const profil = carte.getByRole('combobox', { name: 'Choix du rappel Contextes', exact: true });
  await expect(profil).toHaveValue('origine');
  await profil.selectOption('sources-vues');
  const reponse = page.waitForResponse(r => r.url().endsWith('/evocation/sessions') && r.request().method() === 'POST');
  await carte.getByRole('button', { name: 'Commencer', exact: true }).click();
  const seance = await (await reponse).json();
  expect(seance.protocole_contextes.profil).toBe('sources-vues');
  expect(seance.items).toHaveLength(10);
  for (let i = 0; i < seance.items.length; i++) {
    await page.getByRole('button', { name: 'Afficher', exact: true }).click();
    await expect(page.locator('.scene-contexte')).toBeVisible();
    await page.getByRole('button', { name: 'Passer', exact: true }).click();
    const choix = page.locator('#zone-choix button');
    await expect(choix).toHaveText(seance.items[i].contenu.options);
    await choix.first().click();
    await page.locator('#bouton-suivant').click();
  }
  await expect(page.locator('#zone-choix button')).toHaveText(seance.items[0].contenu.options_rappel);
  await expect(page.locator('.scene-contexte')).toHaveCount(0);
  await expect(page.getByText('Rappel 1 sur 10', { exact: true })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1)).toBeTruthy();
});
