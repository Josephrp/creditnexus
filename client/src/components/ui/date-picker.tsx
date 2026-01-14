import * as React from "react"
import { cn } from "@/lib/utils"

export interface DatePickerProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  onDateChange?: (date: Date) => void
}

const DatePicker = React.forwardRef<HTMLInputElement, DatePickerProps>(
  ({ className, onDateChange, onChange, ...props }, ref) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (onDateChange && e.target.value) {
        onDateChange(new Date(e.target.value))
      }
      if (onChange) {
        onChange(e)
      }
    }

    return (
      <input
        type="date"
        className={cn(
          "flex h-10 w-full rounded-md border border-[var(--color-input-border)] bg-[var(--color-input-bg)] px-3 py-2 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-[var(--color-muted-foreground)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-ring)] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        ref={ref}
        onChange={handleChange}
        {...props}
      />
    )
  }
)
DatePicker.displayName = "DatePicker"

export { DatePicker }
