import * as React from "react"
import { cn } from "@/lib/utils"

interface TreeNode {
  id: string
  label: string
  children?: TreeNode[]
}

interface TreeViewProps {
  nodes: TreeNode[]
  className?: string
  onNodeSelect?: (node: TreeNode) => void
}

const TreeView = React.forwardRef<HTMLDivElement, TreeViewProps>(
  ({ nodes, className, onNodeSelect }, ref) => {
    const renderNode = (node: TreeNode, level = 0) => (
      <div key={node.id} className="pl-4">
        <div 
          className={cn(
            "flex items-center py-1 px-2 rounded hover:bg-[var(--color-tree-hover)]",
            "cursor-pointer transition-colors"
          )}
          onClick={() => onNodeSelect?.(node)}
        >
          <span className="mr-2">{node.children ? '📂' : '📄'}</span>
          <span className="text-[var(--color-tree-text)]">{node.label}</span>
        </div>
        {node.children && (
          <div className="border-l border-[var(--color-tree-line)] ml-2">
            {node.children.map(child => renderNode(child, level + 1))}
          </div>
        )}
      </div>
    )

    return (
      <div ref={ref} className={cn("text-sm", className)}>
        {nodes.map(node => renderNode(node))}
      </div>
    )
  }
)
TreeView.displayName = "TreeView"

export { TreeView }
