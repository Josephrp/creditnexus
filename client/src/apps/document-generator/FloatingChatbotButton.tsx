/**
 * Floating Action Button for Chatbot
 * 
 * Fixed bottom-right button that opens the chatbot in a modal.
 * Only visible on the Document Generator tab.
 */

import { MessageSquare, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface FloatingChatbotButtonProps {
  isOpen: boolean;
  onClick: () => void;
  className?: string;
  badgeCount?: number;
}

export function FloatingChatbotButton({
  isOpen,
  onClick,
  className = '',
  badgeCount = 0,
}: FloatingChatbotButtonProps) {
  return (
    <div
      className={cn(
        'fixed bottom-6 right-6 z-40',
        className
      )}
    >
      <Button
        onClick={onClick}
        className={cn(
          'h-14 w-14 rounded-full shadow-lg',
          'bg-emerald-600 hover:bg-emerald-700',
          'text-white border-0',
          'transition-all duration-200',
          'hover:scale-110 active:scale-95',
          isOpen && 'bg-emerald-700'
        )}
        aria-label={isOpen ? 'Close chatbot' : 'Open chatbot'}
        title={isOpen ? 'Close chatbot' : 'Open chatbot'}
      >
        <div className="relative">
          {isOpen ? (
            <X className="h-6 w-6" />
          ) : (
            <MessageSquare className="h-6 w-6" />
          )}
          {badgeCount > 0 && !isOpen && (
            <span
              className={cn(
                'absolute -top-2 -right-2',
                'h-5 w-5 rounded-full',
                'bg-red-500 text-white',
                'text-xs font-bold',
                'flex items-center justify-center',
                'border-2 border-slate-900'
              )}
            >
              {badgeCount > 9 ? '9+' : badgeCount}
            </span>
          )}
        </div>
      </Button>
    </div>
  );
}
