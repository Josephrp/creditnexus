import { LoginForm } from '@/components/LoginForm';
import { useState } from 'react';

export function LoginPage() {
  const [isOpen, setIsOpen] = useState(true);
  
  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center">
      <LoginForm isOpen={isOpen} onClose={() => {}} />
    </div>
  );
}
