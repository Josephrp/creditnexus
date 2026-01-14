import * as React from "react"
import { cn } from "@/lib/utils"

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-md border border-[var(--color-input-border)]",
          "bg-[var(--color-input-bg)] px-3 py-2 text-sm ring-offset-[var(--color-input-ring-offset)]",
          "placeholder:text-[var(--color-input-placeholder)] focus-visible:outline-none",
          "focus-visible:ring-2 focus-visible:ring-[var(--color-input-ring)]",
          "disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }
