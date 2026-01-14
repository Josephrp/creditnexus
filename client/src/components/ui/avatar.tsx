import * as React from "react"
import { cn } from "@/lib/utils"

interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
  src?: string
  alt?: string
  size?: "sm" | "md" | "lg"
  fallback?: React.ReactNode
}

const Avatar = React.forwardRef<HTMLDivElement, AvatarProps>(
  ({ className, src, alt, size = "md", fallback, ...props }, ref) => {
    const sizeClasses = {
      sm: "h-8 w-8",
      md: "h-10 w-10",
      lg: "h-12 w-12"
    }

    return (
      <div
        ref={ref}
        className={cn(
          "relative flex items-center justify-center rounded-full bg-[var(--color-avatar-bg)] text-[var(--color-avatar-text)] overflow-hidden",
          sizeClasses[size],
          className
        )}
        {...props}
      >
        {src ? (
          <img 
            src={src} 
            alt={alt} 
            className="h-full w-full object-cover"
          />
        ) : (
          <span className="text-sm font-medium">
            {fallback}
          </span>
        )}
      </div>
    )
  }
)
Avatar.displayName = "Avatar"

export { Avatar }
