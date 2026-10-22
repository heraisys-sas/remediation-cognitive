const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/ui',
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  workers: 2,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: 'http://127.0.0.1:18091',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium-bureau', use: { ...devices['Desktop Chrome'] } },
    { name: 'chromium-mobile', use: { ...devices['Pixel 5'] } },
    { name: 'webkit-mobile', use: { ...devices['iPhone SE'] } },
    { name: 'webkit-320', use: { ...devices['iPhone SE'], viewport: { width: 320, height: 568 } } },
  ],
  webServer: {
    command: `"${process.env.ORTHOGONE_TEST_PYTHON || 'python3'}" tools/serveur_tests_ui.py`,
    url: 'http://127.0.0.1:18091/ui/',
    reuseExistingServer: false,
    gracefulShutdown: { signal: 'SIGTERM', timeout: 5000 },
  },
});
