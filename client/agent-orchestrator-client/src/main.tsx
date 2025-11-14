import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

// For Robotto font.
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';

import './index.css';

import App from './App.tsx';

import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './auth/useAuth.tsx';
import { CustomThemeProvider } from './pages/themes/useCustomTheme.tsx';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <CustomThemeProvider>
          <App />
        </CustomThemeProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
);
