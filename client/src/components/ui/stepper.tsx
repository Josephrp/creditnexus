import * as React from "react"
import { cn } from "@/lib/utils"

interface StepperProps {
  steps: { label: string; description?: string }[]
  currentStep: number
  className?: string
  orientation?: "horizontal" | "vertical"
}

const Stepper = React.forwardRef<HTMLDivElement, StepperProps>(
  ({ steps, currentStep, className, orientation = "horizontal" }, ref) => {
    return (
      <div 
        ref={ref}
        className={cn(
          orientation === "horizontal" ? "flex items-center justify-between" : "flex flex-col items-start",
          className
        )}
      >
        {steps.map((step, index) => (
          <div 
            key={index} 
            className={cn(
              "flex",
              orientation === "vertical" && "mb-4",
              orientation === "vertical" && index < steps.length - 1 && "pb-4 border-l-2 border-[var(--color-stepper-line)] ml-4"
            )}
          >
            <div className="flex flex-col items-center">
              <div className={cn(
                "h-8 w-8 rounded-full flex items-center justify-center",
                "border-2 border-[var(--color-stepper-border)]",
                index <= currentStep 
                  ? "bg-[var(--color-stepper-active)] text-[var(--color-stepper-active-text)]"
                  : "bg-[var(--color-stepper-inactive)] text-[var(--color-stepper-inactive-text)]"
              )}>
                {index + 1}
              </div>
            </div>
            <div className={cn(
              "ml-3",
              orientation === "vertical" && "mt-1"
            )}>
              <span className={cn(
                "text-sm font-medium",
                index <= currentStep 
                  ? "text-[var(--color-stepper-active-text)]"
                  : "text-[var(--color-stepper-inactive-text)]"
              )}>
                {step.label}
              </span>
              {step.description && (
                <p className="text-xs text-[var(--color-stepper-description)] mt-1">
                  {step.description}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    )
  }
)
Stepper.displayName = "Stepper"

export { Stepper }
