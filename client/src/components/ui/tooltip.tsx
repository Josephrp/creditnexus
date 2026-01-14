import * as React from "react"
import { cn } from "@/lib/utils"

interface TooltipProps {
  children: React.ReactNode;
  content: string;
  side?: "top" | "bottom" | "left" | "right";
  className?: string;
  delay?: number;
  delayClose?: number;
}

export function Tooltip({ 
  children, 
  content, 
  side = "top", 
  className,
  delay = 300,
  delayClose = 200
}: TooltipProps) {
  const [isVisible, setIsVisible] = React.useState(false);
  let showTimeout: ReturnType<typeof setTimeout>;
  let hideTimeout: ReturnType<typeof setTimeout>;

  const handleMouseEnter = () => {
    clearTimeout(hideTimeout);
    showTimeout = setTimeout(() => setIsVisible(true), delay);
  };

  const handleMouseLeave = () => {
    clearTimeout(showTimeout);
    hideTimeout = setTimeout(() => setIsVisible(false), delayClose);
  };

  React.useEffect(() => {
    return () => {
      clearTimeout(showTimeout);
      clearTimeout(hideTimeout);
    };
  }, []);

  return (
    <div
      className="relative inline-block"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}
      {isVisible && (
        <div
          className={cn(
            "absolute z-50 px-3 py-2 text-sm text-[var(--color-tooltip-text)] bg-[var(--color-tooltip-bg)] border border-[var(--color-tooltip-border)] rounded-lg shadow-lg whitespace-nowrap",
            side === "top" && "bottom-full left-1/2 -translate-x-1/2 mb-2",
            side === "bottom" && "top-full left-1/2 -translate-x-1/2 mt-2",
            side === "left" && "right-full top-1/2 -translate-y-1/2 mr-2",
            side === "right" && "left-full top-1/2 -translate-y-1/2 ml-2",
            className
          )}
        >
          {content}
          <div
            className={cn(
              "absolute w-2 h-2 bg-[var(--color-tooltip-bg)] border border-[var(--color-tooltip-border)] rotate-45",
              side === "top" && "top-full left-1/2 -translate-x-1/2 -mt-1 border-t-0 border-l-0",
              side === "bottom" && "bottom-full left-1/2 -translate-x-1/2 -mb-1 border-b-0 border-r-0",
              side === "left" && "left-full top-1/2 -translate-y-1/2 -ml-1 border-l-0 border-b-0",
              side === "right" && "right-full top-1/2 -translate-y-1/2 -mr-1 border-r-0 border-t-0"
            )}
          />
        </div>
      )}
    </div>
  );
}
