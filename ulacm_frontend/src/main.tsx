// File: ulacm_frontend/src/main.tsx
// Purpose: Renders the root React component into the DOM.

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css' // Imports global styles, including Tailwind base/components/utilities

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
