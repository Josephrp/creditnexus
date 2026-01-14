import * as React from "react"
import { cn } from "@/lib/utils"

interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  required?: boolean
}

const Label = React.forwardRef<HTMLLabelElement, LabelProps>(
  ({ className, children, required, ...props }, ref) => {
    return (
      <label
        ref={ref}
        className={cn(
          "block text-sm font-medium text-[var(--color-label)] mb-1",
          required && "after:content-['*'] after:ml-0.5 after:text-[var(--color-label-required)]",
          className
        )}
        {...props}
      >
        {children}
      </label>
    )
  }
)
Label.displayName = "Label"

export { Label }
