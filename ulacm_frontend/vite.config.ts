// File: ulacm_frontend/vite.config.ts
// Purpose: Configuration file for Vite.
// Added increased timeout for the dev server proxy.

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
    proxy: {
      // Proxy API requests to the backend during development
      '/api': {
        target: 'http://localhost:8000', // Backend API URL
        changeOrigin: true, // Recommended for virtual hosted sites
        // secure: false, // Set to false if backend uses self-signed SSL cert in dev
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
    // # !!! TODO: Change in PRODUCTION !!!
    sourcemap: true // <-- ADD THIS LINE FOR DEBUGGING
    // Consider increasing build-specific timeouts if needed, though less common for this issue
    // commonjsOptions: {
    //   transformMixedEsModules: true,
    // },
  },
  // Optional: Define a custom timeout for the dev server itself, though proxy timeout is more relevant here
  // server: {
  //   hmr: {
  //     timeout: 300000 // example
  //   }
  // }
})
