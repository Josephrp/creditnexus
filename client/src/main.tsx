
import { createRoot } from 'react-dom/client'
import './index.css'
import { router } from './router/Routes'
import { RouterProvider } from 'react-router-dom'
import { FDC3Provider } from './context/FDC3Context'
import { AuthProvider } from './context/AuthContext'
import { WalletProvider } from './context/WalletContext'
import { ThemeProvider } from './context/ThemeContext'
import { ToastProvider } from './components/ui/toast'
import { ErrorBoundary } from './components/ErrorBoundary'

createRoot(document.getElementById('root')!).render(
  <ErrorBoundary>
    <ThemeProvider>
      <AuthProvider>
        <WalletProvider>
          <FDC3Provider>
            <ToastProvider>
              <RouterProvider router={router} />
            </ToastProvider>
          </FDC3Provider>
        </WalletProvider>
      </AuthProvider>
    </ThemeProvider>
  </ErrorBoundary>,
)
