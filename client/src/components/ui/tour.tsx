import * as React from "react"
import { cn } from "@/lib/utils"

interface TourStep {
  target: string
  title: string
  content: string
  position?: "top" | "bottom" | "left" | "right"
}

interface TourProps {
  steps: TourStep[]
  isOpen: boolean
  onClose: () => void
  onComplete: () => void
  className?: string
}

const Tour = React.forwardRef<HTMLDivElement, TourProps>(
  ({ steps, isOpen, onClose, onComplete, className }, ref) => {
    const [currentStep, setCurrentStep] = React.useState(0)

    if (!isOpen || currentStep >= steps.length) return null

    const current = steps[currentStep]

    return (
      <div className="fixed inset-0 z-50">
        <div 
          className="fixed inset-0 bg-[var(--color-tour-overlay)]"
          onClick={onClose}
        />
        
        <div 
          ref={ref}
          className={cn(
            "fixed z-50 bg-[var(--color-tour-bg)] text-[var(--color-tour-text)]",
            "rounded-lg p-4 shadow-xl max-w-xs",
            className
          )}
          style={getPositionStyle(current.position || "bottom")}
        >
          <h3 className="font-bold mb-2">{current.title}</h3>
          <p className="text-sm mb-4">{current.content}</p>
          <div className="flex justify-between">
            <button 
              onClick={() => setCurrentStep(prev => Math.max(0, prev - 1))}
              className="text-[var(--color-tour-button)]"
              disabled={currentStep === 0}
            >
              Back
            </button>
            <div className="text-xs">
              {currentStep + 1} of {steps.length}
            </div>
            <button 
              onClick={() => {
                if (currentStep === steps.length - 1) {
                  onComplete()
                } else {
                  setCurrentStep(prev => prev + 1)
                }
              }}
              className="text-[var(--color-tour-button)] font-medium"
            >
              {currentStep === steps.length - 1 ? "Finish" : "Next"}
            </button>
          </div>
        </div>
      </div>
    )
  }
)

function getPositionStyle(position: string) {
  switch(position) {
    case "top": return { top: "10%", left: "50%", transform: "translateX(-50%)" }
    case "bottom": return { bottom: "10%", left: "50%", transform: "translateX(-50%)" }
    case "left": return { left: "10%", top: "50%", transform: "translateY(-50%)" }
    case "right": return { right: "10%", top: "50%", transform: "translateY(-50%)" }
    default: return { bottom: "10%", left: "50%", transform: "translateX(-50%)" }
  }
}

Tour.displayName = "Tour"

export { Tour }
