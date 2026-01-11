
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

// #region agent log
const rootElement = document.getElementById('root');
const logData1 = {location:'main.tsx:13',message:'Main entry point executing',data:{rootExists:!!rootElement,rootInnerHTML:rootElement?.innerHTML?.substring(0,50)||'N/A',timestamp:Date.now()},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'};
console.log('[DEBUG]', logData1);
fetch('http://127.0.0.1:7242/ingest/b4962ed0-f261-4fa9-86f3-a557335b330a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(logData1)}).catch((e)=>console.error('[DEBUG] Fetch failed:',e));

if (!rootElement) {
  console.error('[DEBUG] CRITICAL: Root element not found!');
  document.body.innerHTML = '<div style="padding:20px;color:red;font-family:monospace;background:yellow;z-index:99999;position:fixed;top:0;left:0;right:0;">ERROR: Root element #root not found. Check index.html</div>';
  throw new Error('Root element not found');
} else {
  // Add visible test marker to verify script is running
  const testDiv = document.createElement('div');
  testDiv.id = 'debug-test-marker';
  testDiv.style.cssText = 'position:fixed;top:10px;right:10px;background:red;color:white;padding:10px;z-index:99999;font-family:monospace;font-size:12px;';
  testDiv.textContent = 'SCRIPT LOADED';
  document.body.appendChild(testDiv);
  
  // #region agent log
  const logData12 = {location:'main.tsx:24',message:'Test marker added to DOM',data:{timestamp:Date.now()},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'G'};
  console.log('[DEBUG]', logData12);
  fetch('http://127.0.0.1:7242/ingest/b4962ed0-f261-4fa9-86f3-a557335b330a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(logData12)}).catch((e)=>console.error('[DEBUG] Fetch failed:',e));
  // #endregion
}
// #endregion

// #region agent log
const logData10 = {location:'main.tsx:28',message:'About to render React root',data:{timestamp:Date.now()},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'};
console.log('[DEBUG]', logData10);
fetch('http://127.0.0.1:7242/ingest/b4962ed0-f261-4fa9-86f3-a557335b330a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(logData10)}).catch((e)=>console.error('[DEBUG] Fetch failed:',e));
// #endregion

// Add visible debug panel
const debugPanel = document.createElement('div');
debugPanel.id = 'react-debug-panel';
debugPanel.style.cssText = 'position:fixed;bottom:10px;left:10px;background:rgba(0,0,0,0.8);color:lime;padding:10px;font-family:monospace;font-size:11px;z-index:99998;border:2px solid lime;max-width:400px;max-height:200px;overflow:auto;';
debugPanel.innerHTML = '<div>React Debug Panel</div><div id="debug-status">Initializing...</div>';
document.body.appendChild(debugPanel);

const updateDebugStatus = (msg: string) => {
  const statusEl = document.getElementById('debug-status');
  if (statusEl) {
    statusEl.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
    console.log('[DEBUG PANEL]', msg);
  }
};

updateDebugStatus('Starting React render...');

try {
  updateDebugStatus('Creating React root...');
  createRoot(rootElement).render(
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
  
  updateDebugStatus('React render call completed');
  
  // #region agent log
  const logData11 = {location:'main.tsx:45',message:'React root render call completed',data:{timestamp:Date.now()},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'};
  console.log('[DEBUG]', logData11);
  fetch('http://127.0.0.1:7242/ingest/b4962ed0-f261-4fa9-86f3-a557335b330a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(logData11)}).catch((e)=>console.error('[DEBUG] Fetch failed:',e));
  // #endregion
  
  // Check if React actually rendered after a short delay
  setTimeout(() => {
    const rootContent = rootElement.innerHTML.trim();
    if (rootContent.length < 10) {
      updateDebugStatus('WARNING: Root element appears empty after render!');
      console.error('[DEBUG] Root element is empty:', rootElement);
    } else {
      updateDebugStatus(`React rendered (${rootContent.length} chars in root)`);
    }
  }, 1000);
  
} catch (renderError) {
  updateDebugStatus(`ERROR: ${renderError instanceof Error ? renderError.message : String(renderError)}`);
  // #region agent log
  const errorLog2 = {location:'main.tsx:50',message:'CRITICAL: React render threw error',data:{error:renderError instanceof Error?renderError.message:String(renderError),errorStack:renderError instanceof Error?renderError.stack?.substring(0,500):'N/A'},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'F'};
  console.error('[DEBUG] CRITICAL RENDER ERROR:', errorLog2);
  fetch('http://127.0.0.1:7242/ingest/b4962ed0-f261-4fa9-86f3-a557335b330a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(errorLog2)}).catch((e)=>console.error('[DEBUG] Fetch failed:',e));
  // #endregion
  
  // Show error on screen
  rootElement.innerHTML = `
    <div style="padding: 40px; font-family: monospace; background: #1e1e1e; color: #ff4444; min-height: 100vh;">
      <h1 style="color: #ff6666;">CRITICAL ERROR: React Failed to Render</h1>
      <pre style="background: #000; padding: 20px; border-radius: 4px; overflow: auto; max-width: 800px;">
${renderError instanceof Error ? renderError.message : String(renderError)}
${renderError instanceof Error ? renderError.stack : ''}
      </pre>
      <p style="color: #aaa; margin-top: 20px;">Check the browser console (F12) for more details.</p>
    </div>
  `;
}

// #region agent log
const logData2 = {location:'main.tsx:27',message:'React root rendered',data:{timestamp:Date.now()},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'};
console.log('[DEBUG]', logData2);
fetch('http://127.0.0.1:7242/ingest/b4962ed0-f261-4fa9-86f3-a557335b330a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(logData2)}).catch((e)=>console.error('[DEBUG] Fetch failed:',e));
// #endregion
