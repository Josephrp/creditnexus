import * as React from "react"
import { cn } from "@/lib/utils"

interface MediaPlayerProps {
  src: string
  type: "audio" | "video"
  className?: string
  controls?: boolean
}

const MediaPlayer = React.forwardRef<HTMLMediaElement, MediaPlayerProps>(
  ({ src, type, className, controls = true }, ref) => {
    return (
      <div className={cn(
        "relative rounded-lg overflow-hidden bg-[var(--color-media-bg)]",
        className
      )}>
        {type === "audio" ? (
          <audio 
            ref={ref as React.Ref<HTMLAudioElement>}
            src={src}
            controls={controls}
            className="w-full"
          />
        ) : (
          <video
            ref={ref as React.Ref<HTMLVideoElement>}
            src={src}
            controls={controls}
            className="w-full"
          />
        )}
      </div>
    )
  }
)
MediaPlayer.displayName = "MediaPlayer"

export { MediaPlayer }
