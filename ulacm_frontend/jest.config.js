// File: ulacm_frontend/jest.config.js
// Purpose: Configuration for the Jest testing framework.

export default {
    preset: 'ts-jest', // Use ts-jest preset for TypeScript
    testEnvironment: 'jest-environment-jsdom', // Use jsdom environment for browser-like testing
    setupFilesAfterEnv: ['<rootDir>/jest.setup.js'], // Run setup file after environment is set up
    moduleNameMapper: {
      // Handle module path aliases
      '^@/(.*)$': '<rootDir>/src/$1',
      // Handle static assets (CSS, images) - could also use identity-obj-proxy for CSS
      '\\.(css|less|sass|scss)$': 'identity-obj-proxy', // Mock CSS modules
      '\\.(gif|ttf|eot|svg|png)$': '<rootDir>/__mocks__/fileMock.js', // Mock other static assets
    },
    transform: {
      // Use ts-jest for .ts and .tsx files
      '^.+\\.(ts|tsx)?$': ['ts-jest', {
          tsconfig: 'tsconfig.json', // Point to your main tsconfig
          // Optional: Add any specific ts-jest options here
      }],
      // Handle JS files if needed (e.g., from node_modules or JS components)
      '^.+\\.(js|jsx)$': 'babel-jest', // Requires babel-jest and babel config if you have complex JS
    },
    // Ignore node_modules except for specific ones if needed for transformation
    transformIgnorePatterns: [
      '/node_modules/',
      // Add exceptions here if a node_module needs transpiling, e.g.
      // '/node_modules/(?!some-es6-module)/'
    ],
    // Collect coverage information
    collectCoverage: true,
    coverageDirectory: 'coverage',
    coverageProvider: 'v8', // or 'babel'
    coveragePathIgnorePatterns: [
      '/node_modules/',
      '/__mocks__/',
      '/coverage/',
      '/dist/',
      '/build/',
      '\\.config\\.js$', // Ignore config files
      'main\\.tsx$', // Ignore main entry point typically
      'App\\.tsx$', // Ignore App setup unless specific tests needed
      '/src/types/', // Ignore type definition files
    ],
    // Optional: Configure test match patterns
    testMatch: [
      '**/__tests__/**/*.[jt]s?(x)',
      '**/?(*.)+(spec|test).[jt]s?(x)',
    ],
    // Verbose output in console
    verbose: true,
  };
