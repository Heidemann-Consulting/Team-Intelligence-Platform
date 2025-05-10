// File: ulacm_frontend/tailwind.config.js
// Purpose: Configuration file for Tailwind CSS.

/** @type {import('tailwindcss').Config} */
export default {
    content: [
      "./index.html", // Scan HTML file for Tailwind classes
      "./src/**/*.{js,ts,jsx,tsx}", // Scan all JS/TS/JSX/TSX files in src directory
    ],
    theme: {
      extend: {
        // Extend Tailwind's default theme here if needed
        // For example, custom colors, fonts, spacing, etc.
        fontFamily: {
          sans: ['Inter', 'sans-serif'], // Set Inter as the default sans-serif font
        },
        colors: {
          // Example custom colors (adjust to your ULACM theme)
          'ulacm-primary': {
            light: '#60a5fa', // blue-400
            DEFAULT: '#3b82f6', // blue-500
            dark: '#2563eb',  // blue-600
          },
          'ulacm-secondary': {
            light: '#f472b6', // pink-400
            DEFAULT: '#ec4899', // pink-500
            dark: '#db2777',  // pink-600
          },
          'ulacm-gray': {
            50: '#f9fafb',
            100: '#f3f4f6',
            200: '#e5e7eb',
            300: '#d1d5db',
            400: '#9ca3af',
            500: '#6b7280',
            600: '#4b5563',
            700: '#374151',
            800: '#1f2937',
            900: '#111827',
          }
        }
      },
    },
    plugins: [
      // Add any Tailwind plugins here, e.g., @tailwindcss/forms, @tailwindcss/typography
    ],
  }
