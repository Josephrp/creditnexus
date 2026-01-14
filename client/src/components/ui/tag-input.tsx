import * as React from "react"
import { cn } from "@/lib/utils"

interface TagInputProps {
  tags: string[]
  onTagsChange: (tags: string[]) => void
  className?: string
  placeholder?: string
}

const TagInput = React.forwardRef<HTMLDivElement, TagInputProps>(
  ({ tags, onTagsChange, className, placeholder = "Add a tag..." }, ref) => {
    const [inputValue, setInputValue] = React.useState("")

    const handleKeyDown = (e: React.KeyboardEvent) => {
      if (["Enter", "Tab", ","].includes(e.key) && inputValue.trim()) {
        e.preventDefault()
        onTagsChange([...tags, inputValue.trim()])
        setInputValue("")
      }
    }

    const removeTag = (index: number) => {
      onTagsChange(tags.filter((_, i) => i !== index))
    }

    return (
      <div ref={ref} className={cn("flex flex-wrap gap-2 p-2 border rounded-lg", className)}>
        {tags.map((tag, index) => (
          <div 
            key={index}
            className="inline-flex items-center bg-[var(--color-tag-bg)] text-[var(--color-tag-text)] px-3 py-1 rounded-full text-sm"
          >
            {tag}
            <button 
              onClick={() => removeTag(index)}
              className="ml-2 text-[var(--color-tag-remove)]"
              aria-label={`Remove ${tag}`}
            >
              ×
            </button>
          </div>
        ))}
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="flex-1 min-w-[100px] outline-none bg-transparent"
        />
      </div>
    )
  }
)
TagInput.displayName = "TagInput"

export { TagInput }
