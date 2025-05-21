// File: ulacm_frontend/cypress/e2e/admin_team_management.cy.ts
// Purpose: E2E test for basic admin login and viewing teams.

describe('Admin Team Management Flow', () => {
    // Function to perform admin login
    const adminLogin = (password: string) => {
      cy.visit('/admin/login');
      cy.get('input[name="password"]').type(password);
      cy.get('button[type="submit"]').click();
      // Wait for successful login indication (e.g., URL change, dashboard element visible)
      cy.url().should('include', '/admin/dashboard');
      cy.contains('h1', /Administrator Dashboard/i).should('be.visible');
    };

    beforeEach(() => {
      // **Important**: Set the correct admin password here.
      // Ideally, use Cypress environment variables (cypress.env.json)
      // const adminPassword = Cypress.env('ADMIN_PASSWORD') || 'supersecretadminpass'; // Example
      const adminPassword = 'supersecretadminpass'; // Hardcoded for example, use env var in real tests!

      // Mock successful admin login
      cy.intercept('POST', '/api/v1/admin/auth/login', {
        statusCode: 200,
        body: { message: 'Admin login successful.' },
      }).as('adminLoginRequest');

      // Mock fetching the initial list of teams for the management page
      cy.intercept('GET', '/api/v1/admin/teams?offset=0&limit=10', {
        statusCode: 200,
        body: {
          total_count: 2, // Example count
          offset: 0,
          limit: 10,
          teams: [
            { team_id: 'team-1', team_name: 'Team Alpha', username: 'alpha_user', is_active: true, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
            { team_id: 'team-2', team_name: 'Team Beta', username: 'beta_user', is_active: false, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
          ],
        },
      }).as('getTeamsRequest');

      // Perform login
      adminLogin(adminPassword);
      // Navigate to the team management page
      cy.contains('a', /Team Management/i).click();
      // Wait for the teams list to be fetched
      cy.wait('@getTeamsRequest');
      cy.contains('h1', /Team Management/i).should('be.visible'); // Verify page loaded
    });

    it('should display the list of teams', () => {
      // Check table headers
      cy.contains('th', /Team Name/i).should('be.visible');
      cy.contains('th', /Username/i).should('be.visible');
      cy.contains('th', /Status/i).should('be.visible');
      cy.contains('th', /Actions/i).should('be.visible');

      // Check if mock data teams are displayed
      cy.contains('td', 'Team Alpha').should('be.visible');
      cy.contains('td', '@alpha_user').should('be.visible');
      cy.contains('span', 'Active').should('be.visible'); // Assuming status is shown like this

      cy.contains('td', 'Team Beta').should('be.visible');
      cy.contains('td', '@beta_user').should('be.visible');
      cy.contains('span', 'Inactive').should('be.visible');

      // Check for action buttons (at least one set)
      cy.get('button[title="Edit Team"]').should('have.length.gte', 1);
      cy.get('button[title*="eactivate Team"]').should('have.length.gte', 1); // Covers Activate/Deactivate
      cy.get('button[title="Delete Team"]').should('have.length.gte', 1);
    });

    it('should open the Create Team modal when "Create Team" button is clicked', () => {
      cy.get('button').contains(/Create Team/i).click();
      // Check if the modal appears (look for modal title or specific input)
      cy.contains('h3', /Create New Team/i).should('be.visible');
      cy.get('input[id="teamName"]').should('be.visible'); // Check for an input within the modal
    });

    // Add more tests for Edit, Deactivate, Reactivate, Delete flows.
    // These often require more complex mocking of the API calls within the test itself.
    // Example structure for testing Deactivate:
    // it('should deactivate an active team', () => {
    //   cy.intercept('POST', '/api/v1/admin/teams/team-1/deactivate', {
    //     statusCode: 200,
    //     body: { team_id: 'team-1', is_active: false, message: 'Success' }
    //   }).as('deactivateRequest');
    //
    //   // Find the row for Team Alpha and click its deactivate button
    //   cy.contains('tr', 'Team Alpha')
    //     .find('button[title="Deactivate Team"]')
    //     .click();
    //
    //   cy.wait('@deactivateRequest');
    //
    //   // Verify the status changes in the UI (might need a refetch mock or check text)
    //   cy.contains('tr', 'Team Alpha')
    //     .find('span:contains("Inactive")')
    //     .should('be.visible');
    // });
  });
