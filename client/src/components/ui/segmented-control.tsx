import * as React from "react"
import { cn } from "@/lib/utils"

interface SegmentedControlProps {
  options: { value: string; label: string }[]
  value: string
  onChange: (value: string) => void
  className?: string
}

const SegmentedControl = React.forwardRef<HTMLDivElement, SegmentedControlProps>(
  ({ options, value, onChange, className }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "inline-flex rounded-lg p-1 bg-[var(--color-segment-bg)]",
          className
        )}
      >
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            className={cn(
              "px-3 py-1 text-sm font-medium rounded-md transition-colors",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-ring)]",
              value === option.value
                ? "bg-[var(--color-segment-active)] text-[var(--color-segment-active-text)] shadow-sm"
                : "text-[var(--color-segment-inactive)] hover:bg-[var(--color-segment-hover)]"
            )}
          >
            {option.label}
          </button>
        ))}
      </div>
    )
  }
)
SegmentedControl.displayName = "SegmentedControl"

export { SegmentedControl }
