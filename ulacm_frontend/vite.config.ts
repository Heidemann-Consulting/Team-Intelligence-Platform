// File: ulacm_frontend/vite.config.ts
// Purpose: Configuration file for Vite.
// Added increased timeout for the dev server proxy.
// Updated proxy target to use HTTPS if backend is served over HTTPS.

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path' // Import path module
import tsconfigPaths from 'vite-tsconfig-paths'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tsconfigPaths()
  ],
  server: {
    port: 4000, // Port for the development server
    // Configure HTTPS for the Vite dev server
    https: {
      key: path.resolve(__dirname, '../../certs/frontend/key.pem'), // Adjust path as necessary
      cert: path.resolve(__dirname, '../../certs/frontend/cert.pem'), // Adjust path as necessary
    },
    proxy: {
      // Proxy API requests to the backend during development
      '/api': {
        // Assuming backend runs on HTTPS on port 8443 now
        target: 'https://localhost:8443', // Backend API URL (HTTPS)
        changeOrigin: true, // Recommended for virtual hosted sites
        secure: false, // IMPORTANT: Allow self-signed certs for backend during dev
        // rewrite: (path) => path.replace(/^\/api/, '') // If backend doesn't expect /api prefix

        // *** ADDED/MODIFIED FOR TIMEOUT ***
        // Increase the timeout for proxied requests. Default is 30000 (30 seconds).
        // Setting to 300000ms (5 minutes) to accommodate long LLM calls.
        timeout: 300000
      }
    }
  },
  build: {
    rollupOptions: {
       input: path.resolve(__dirname, 'index.html')
    },
    outDir: 'build',
    sourcemap: true
  },
})
