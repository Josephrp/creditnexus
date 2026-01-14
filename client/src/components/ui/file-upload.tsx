import * as React from "react"
import { cn } from "@/lib/utils"

interface FileUploadProps {
  onFilesSelected: (files: File[]) => void
  accept?: string
  multiple?: boolean
  className?: string
}

const FileUpload = React.forwardRef<HTMLDivElement, FileUploadProps>(
  ({ onFilesSelected, accept, multiple = false, className }, ref) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files) {
        onFilesSelected(Array.from(e.target.files))
      }
    }

    return (
      <div 
        ref={ref}
        className={cn(
          "border-2 border-dashed border-[var(--color-upload-border)] rounded-lg p-6 text-center",
          "hover:bg-[var(--color-upload-hover)] transition-colors",
          className
        )}
      >
        <input
          type="file"
          onChange={handleChange}
          accept={accept}
          multiple={multiple}
          className="hidden"
          id="file-upload"
        />
        <label 
          htmlFor="file-upload" 
          className="cursor-pointer flex flex-col items-center justify-center gap-2"
        >
          <div className="text-[var(--color-upload-icon)] text-2xl">
            📁
          </div>
          <p className="text-sm text-[var(--color-upload-text)]">
            Drag & drop files here or click to browse
          </p>
          <p className="text-xs text-[var(--color-upload-hint)]">
            {accept ? `Allowed: ${accept}` : "Any file type"}
          </p>
        </label>
      </div>
    )
  }
)
FileUpload.displayName = "FileUpload"

export { FileUpload }
