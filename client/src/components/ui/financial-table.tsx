import * as React from "react"
import { cn } from "@/lib/utils"

interface FinancialTableProps {
  headers: string[]
  rows: Array<{
    cells: React.ReactNode[]
    highlight?: boolean
  }>
  footer?: React.ReactNode
  className?: string
}

const FinancialTable = React.forwardRef<HTMLDivElement, FinancialTableProps>(
  ({ headers, rows, footer, className }, ref) => {
    return (
      <div ref={ref} className={cn("overflow-x-auto", className)}>
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b border-[var(--color-table-border)]">
              {headers.map((header, i) => (
                <th 
                  key={i}
                  className={cn(
                    "text-left py-3 px-4 text-sm font-medium text-[var(--color-table-header)]",
                    i === 0 && "pl-0",
                    i === headers.length - 1 && "pr-0"
                  )}
                >
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr 
                key={rowIndex}
                className={cn(
                  "border-b border-[var(--color-table-border)]",
                  row.highlight && "bg-[var(--color-table-highlight)]"
                )}
              >
                {row.cells.map((cell, cellIndex) => (
                  <td
                    key={cellIndex}
                    className={cn(
                      "py-3 px-4 text-sm",
                      cellIndex === 0 && "pl-0",
                      cellIndex === row.cells.length - 1 && "pr-0"
                    )}
                  >
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
          {footer && (
            <tfoot>
              <tr className="bg-[var(--color-table-footer)]">
                <td 
                  colSpan={headers.length}
                  className="py-3 px-4 text-sm font-medium"
                >
                  {footer}
                </td>
              </tr>
            </tfoot>
          )}
        </table>
      </div>
    )
  }
)
FinancialTable.displayName = "FinancialTable"

export { FinancialTable }
