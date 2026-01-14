import * as React from "react"
import { cn } from "@/lib/utils"

interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: React.ReactNode
  variant?: 'default' | 'success' | 'error' | 'info'
}

const EmptyState = React.forwardRef<HTMLDivElement, EmptyStateProps>(
  ({ className, icon, title, description, action, variant = 'default', ...props }, ref) => {
    const variantStyles = {
      default: {
        icon: "text-[var(--color-empty-state-icon)]",
        title: "text-[var(--color-empty-state-title)]",
        description: "text-[var(--color-empty-state-description)]"
      },
      success: {
        icon: "text-[var(--color-success)]",
        title: "text-[var(--color-success)]",
        description: "text-[var(--color-muted-foreground)]"
      },
      error: {
        icon: "text-[var(--color-error)]",
        title: "text-[var(--color-error)]",
        description: "text-[var(--color-muted-foreground)]"
      },
      info: {
        icon: "text-[var(--color-info)]",
        title: "text-[var(--color-info)]",
        description: "text-[var(--color-muted-foreground)]"
      }
    }

    return (
      <div
        ref={ref}
        className={cn(
          "flex flex-col items-center justify-center py-12 text-center",
          className
        )}
        {...props}
      >
        {icon && (
          <div className={cn("mb-4 h-12 w-12", variantStyles[variant].icon)}>
            {icon}
          </div>
        )}
        <h3 className={cn("text-lg font-medium mb-2", variantStyles[variant].title)}>
          {title}
        </h3>
        {description && (
          <p className={cn("text-sm max-w-md", variantStyles[variant].description)}>
            {description}
          </p>
        )}
        {action && <div className="mt-6">{action}</div>}
      </div>
    )
  }
)
EmptyState.displayName = "EmptyState"

export { EmptyState }
