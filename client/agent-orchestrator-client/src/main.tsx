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
import { ThemeProvider } from '@emotion/react';
import { createTheme, CssBaseline } from '@mui/material';
import { red, yellow } from '@mui/material/colors';
import { responsiveFontSizes } from '@mui/material/styles';

const theme = responsiveFontSizes(createTheme({
  palette: {
    primary: {
      main: red[500]
    },
    background: {
      default: yellow[50],
      paper: yellow[100]
    }
  }
}));

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <App />
        </ThemeProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
);
