import * as React from "react"
import { cn } from "@/lib/utils"

interface ContextMenuProps {
  items: {
    label: string
    onClick: () => void
    icon?: React.ReactNode
    disabled?: boolean
  }[]
  className?: string
}

const ContextMenu = React.forwardRef<HTMLDivElement, ContextMenuProps>(
  ({ items, className }, ref) => {
    return (
      <div 
        ref={ref}
        className={cn(
          "min-w-[200px] rounded-lg border border-[var(--color-menu-border)]",
          "bg-[var(--color-menu-bg)] shadow-lg py-1 z-50",
          className
        )}
      >
        {items.map((item, index) => (
          <button
            key={index}
            onClick={item.onClick}
            disabled={item.disabled}
            className={cn(
              "w-full text-left px-4 py-2 text-sm flex items-center gap-2",
              "hover:bg-[var(--color-menu-hover)] transition-colors",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "text-[var(--color-menu-text)]"
            )}
          >
            {item.icon && <span className="text-[var(--color-menu-icon)]">{item.icon}</span>}
            {item.label}
          </button>
        ))}
      </div>
    )
  }
)
ContextMenu.displayName = "ContextMenu"

export { ContextMenu }
