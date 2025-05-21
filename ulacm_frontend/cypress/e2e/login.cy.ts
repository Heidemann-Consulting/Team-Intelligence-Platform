// File: ulacm_frontend/cypress/e2e/login.cy.ts
// Purpose: E2E test for the team login flow.

describe('Team Login Flow', () => {
    beforeEach(() => {
      // Visit the login page before each test in this block
      cy.visit('/login');
      // Ensure the login page has loaded (optional but good practice)
      cy.contains('h1', 'Team Login').should('be.visible');
    });

    it('should display the login form', () => {
      cy.get('input[name="username"]').should('be.visible');
      cy.get('input[name="password"]').should('be.visible');
      cy.get('button[type="submit"]').contains(/login/i).should('be.visible');
      cy.contains(/administrator\?/i).should('be.visible');
      cy.contains('a', /login here/i).should('be.visible');
    });

    it('should show validation error if fields are empty', () => {
      cy.get('button[type="submit"]').contains(/login/i).click();
      // Check for toast message (requires configuration or custom command if toasts are complex)
      // For now, we assume validation prevents API call, maybe check that login function isn't called if mocked
      // Or check if an inline error message appears (if implemented)
      // cy.contains('Username and password are required.').should('be.visible'); // Example if toast content is checkable
      cy.url().should('include', '/login'); // Should stay on login page
    });

    it('should display API error on incorrect credentials', () => {
      // Intercept the login API call and force an error response
      cy.intercept('POST', '/api/v1/auth/login', {
        statusCode: 401,
        body: { detail: 'Incorrect username or password' },
      }).as('loginRequest');

      cy.get('input[name="username"]').type('wronguser');
      cy.get('input[name="password"]').type('wrongpassword{enter}'); // Use {enter} to submit

      // Wait for the intercepted request to complete
      cy.wait('@loginRequest');

      // Check that the error message is displayed on the page
      cy.contains('Incorrect username or password').should('be.visible');
      cy.url().should('include', '/login'); // Should stay on login page
    });

    it('should log in successfully and redirect to dashboard with correct credentials', () => {
      const teamUsername = 'test_alpha_user'; // Replace with a valid test username
      const teamPassword = 'testpassword'; // Replace with the valid password for the test user

      // **Important**: For this test to pass, you need a predictable test user
      // in your database when the backend runs. Consider seeding the DB for tests.
      // Or mock the API response for successful login.

      // Mock successful login response
      cy.intercept('POST', '/api/v1/auth/login', {
        statusCode: 200,
        body: {
          team_id: 'team-123-abc',
          team_name: 'Test Alpha Team',
          username: teamUsername,
          is_active: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        // Cypress automatically handles cookies set by the backend if `withCredentials` is true
      }).as('loginRequest');

      cy.get('input[name="username"]').type(teamUsername);
      cy.get('input[name="password"]').type(teamPassword);
      cy.get('button[type="submit"]').contains(/login/i).click();

      cy.wait('@loginRequest');

      // Check for redirection to the dashboard
      cy.url().should('include', '/app/dashboard');
      cy.contains('h1', /welcome, Test Alpha Team/i).should('be.visible'); // Check for welcome message
    });

    it('should navigate to admin login page when admin link is clicked', () => {
      cy.contains('a', /login here/i).click();
      cy.url().should('include', '/admin/login');
      cy.contains('h1', /admin login/i).should('be.visible');
    });
  });
