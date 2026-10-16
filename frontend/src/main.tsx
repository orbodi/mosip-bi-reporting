import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider } from '@tanstack/react-router';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { Authentification } from './auth/Authentification';
import { routeur } from './routeur';
import './styles/global.css';

const client = new QueryClient({
  defaultOptions: { queries: { staleTime: 60_000, retry: 1, refetchOnWindowFocus: false } },
});

createRoot(document.getElementById('racine')!).render(
  <StrictMode>
    <Authentification>
      <QueryClientProvider client={client}>
        <RouterProvider router={routeur} />
      </QueryClientProvider>
    </Authentification>
  </StrictMode>,
);
