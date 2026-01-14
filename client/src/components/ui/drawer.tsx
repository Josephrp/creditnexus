import * as React from "react"
import { cn } from "@/lib/utils"

interface DrawerProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  children: React.ReactNode
  side?: "left" | "right"
}

const Drawer = ({ open, onOpenChange, children, side = "left" }: DrawerProps) => {
  // Handle Escape key
  React.useEffect(() => {
    if (!open) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onOpenChange(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [open, onOpenChange]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50">
      <div 
        className="fixed inset-0 bg-[var(--color-overlay)] backdrop-blur-[8px]"
        onClick={() => onOpenChange(false)}
        aria-hidden="true"
      />
      <div className={cn(
        "fixed top-0 h-full w-80 bg-[var(--color-panel)] shadow-lg transition-transform duration-300 ease-in-out",
        side === "left" ? "left-0" : "right-0",
        open ? "translate-x-0" : side === "left" ? "-translate-x-full" : "translate-x-full"
      )}>
        {children}
      </div>
    </div>
  );
};

export { Drawer }
