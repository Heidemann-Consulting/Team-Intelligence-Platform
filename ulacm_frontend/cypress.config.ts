// File: ulacm_frontend/cypress.config.ts
// Purpose: Configuration for Cypress E2E testing.
// Updated baseUrl to use HTTPS.

import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    // Base URL for the application being tested.
    // Point this to where your frontend runs during testing (e.g., Vite dev server).
    baseUrl: 'https://localhost:4000', // Updated to HTTPS and matching Vite dev server port

    // Set default viewport size
    viewportWidth: 1280,
    viewportHeight: 720,

    // Optional: Turn off video recording to save space/time if not needed
    video: false,

    // Optional: Configure test retries
    // retries: {
    //   runMode: 2, // Number of retries for `cypress run`
    //   openMode: 0, // Number of retries for `cypress open`
    // },

    // Setup Node events if needed (e.g., for tasks, plugins)
    setupNodeEvents(on, config) {
      // implement node event listeners here
      // Example: `on('task', { myTask: () => { ... } })`
      // Make sure to return the config object
      return config;
    },

    // Support file (optional, for custom commands, etc.)
    // supportFile: 'cypress/support/e2e.ts',

    // Spec pattern (where your test files are located)
    // specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}', // Default pattern
  },

  // Component testing configuration (if you decide to use Cypress for component tests later)
  // component: {
  //   devServer: {
  //     framework: 'react',
  //     bundler: 'vite',
  //   },
  // },
});
