import * as React from "react"
import { cn } from "@/lib/utils"

export interface ChipProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "primary" | "success" | "warning" | "error"
  closable?: boolean
  onClose?: () => void
}

const Chip = React.forwardRef<HTMLDivElement, ChipProps>(
  ({ className, variant = "default", closable, onClose, children, ...props }, ref) => {
    const variantClasses = {
      default: "bg-[var(--color-chip-default)] text-[var(--color-chip-default-text)]",
      primary: "bg-[var(--color-chip-primary)] text-[var(--color-chip-primary-text)]",
      success: "bg-[var(--color-chip-success)] text-[var(--color-chip-success-text)]",
      warning: "bg-[var(--color-chip-warning)] text-[var(--color-chip-warning-text)]",
      error: "bg-[var(--color-chip-error)] text-[var(--color-chip-error-text)]"
    }

    return (
      <div
        ref={ref}
        className={cn(
          "inline-flex items-center rounded-full px-3 py-1 text-sm font-medium",
          variantClasses[variant],
          className
        )}
        {...props}
      >
        {children}
        {closable && (
          <button 
            onClick={(e) => {
              e.stopPropagation()
              onClose?.()
            }}
            className="ml-1.5 -mr-1 h-4 w-4 rounded-full opacity-70 hover:opacity-100"
            aria-label="Remove"
          >
            ×
          </button>
        )}
      </div>
    )
  }
)
Chip.displayName = "Chip"

export { Chip }
