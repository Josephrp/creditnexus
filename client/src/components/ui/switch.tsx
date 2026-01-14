import * as React from "react"
import { cn } from "@/lib/utils"

export interface SwitchProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  checked: boolean
  onCheckedChange: (checked: boolean) => void
}

const Switch = React.forwardRef<HTMLButtonElement, SwitchProps>(
  ({ className, checked, onCheckedChange, ...props }, ref) => {
    return (
      <button
        ref={ref}
        role="switch"
        aria-checked={checked}
        onClick={() => onCheckedChange(!checked)}
        className={cn(
          "inline-flex h-6 w-11 items-center rounded-full transition-colors",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-ring)]",
          "disabled:cursor-not-allowed disabled:opacity-50",
          checked ? "bg-[var(--color-switch-active)]" : "bg-[var(--color-switch-inactive)]",
          className
        )}
        {...props}
      >
        <span 
          className={cn(
            "pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow-lg transition-transform",
            checked ? "translate-x-6" : "translate-x-1"
          )}
        />
      </button>
    )
  }
)
Switch.displayName = "Switch"

export { Switch }
