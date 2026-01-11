import { LoginForm } from '@/components/LoginForm';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';

export function LoginPage() {
  // #region agent log
  const logData5 = {location:'LoginPage.tsx:6',message:'LoginPage rendering',data:{timestamp:Date.now()},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'};
  console.log('[DEBUG]', logData5);
  fetch('http://127.0.0.1:7242/ingest/b4962ed0-f261-4fa9-86f3-a557335b330a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(logData5)}).catch((e)=>console.error('[DEBUG] Fetch failed:',e));
  // #endregion
  
  const [isOpen, setIsOpen] = useState(true);
  const navigate = useNavigate();
  const { user, isLoading } = useAuth();

  // #region agent log
  useEffect(() => {
    const logData6 = {location:'LoginPage.tsx:12',message:'LoginPage useEffect - auth state',data:{hasUser:!!user,isLoading},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'};
    console.log('[DEBUG]', logData6);
    fetch('http://127.0.0.1:7242/ingest/b4962ed0-f261-4fa9-86f3-a557335b330a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(logData6)}).catch((e)=>console.error('[DEBUG] Fetch failed:',e));
  }, [user, isLoading]);
  // #endregion

  // Redirect to dashboard if already logged in
  useEffect(() => {
    if (user) {
      // #region agent log
      const logData7 = {location:'LoginPage.tsx:20',message:'LoginPage redirecting to dashboard',data:{timestamp:Date.now()},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'};
      console.log('[DEBUG]', logData7);
      fetch('http://127.0.0.1:7242/ingest/b4962ed0-f261-4fa9-86f3-a557335b330a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(logData7)}).catch((e)=>console.error('[DEBUG] Fetch failed:',e));
      // #endregion
      navigate('/dashboard', { replace: true });
    }
  }, [user, navigate]);

  const handleClose = () => {
    // If user is logged in, navigate to dashboard
    if (user) {
      navigate('/dashboard', { replace: true });
    }
  };
  
  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center">
      <LoginForm isOpen={isOpen} onClose={handleClose} />
    </div>
  );
}
