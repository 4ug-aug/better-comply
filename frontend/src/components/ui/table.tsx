import * as React from "react"
const TableContext = React.createContext({ density: "comfortable", stickyHeader: false })
import { cn } from "@/lib/utils"
import { ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react"

interface TableProps extends React.TableHTMLAttributes<HTMLTableElement> {
  className?: string;
  density?: "comfortable" | "compact";
  striped?: boolean;
  stickyHeader?: boolean;
  children?: React.ReactNode;
}

function Table({
  className,
  density = "comfortable",
  striped = false,
  stickyHeader = false,
  children,
  ...props
}: TableProps) {
  return (
    <div
      data-slot="table-container"
      className={cn(
        "relative w-full overflow-x-auto overflow-y-auto rounded-xl border border-border bg-card shadow-sm",
        className
      )}
    >
      <TableContext.Provider value={{ density, stickyHeader }}>
        <table data-slot="table" className="w-full caption-bottom text-sm" {...props}>
          {children}
        </table>
      </TableContext.Provider>
    </div>
  )
}
function TableHeader({ className, ...props }: React.HTMLAttributes<HTMLTableSectionElement>) {
  const { stickyHeader } = React.useContext(TableContext)
  return (
    <thead
      data-slot="table-header"
      className={cn(
        "bg-muted/40 text-muted-foreground border-b border-border",
        stickyHeader && "sticky top-0 z-10",
        className
      )}
      {...props}
    />
  )
}
function TableBody({ className, striped = false, ...props }: React.HTMLAttributes<HTMLTableSectionElement> & { striped?: boolean }) {
  return (
    <tbody
      data-slot="table-body"
      className={cn(
        "bg-card divide-y divide-border",
        striped && "[&>tr:nth-child(odd)]:bg-muted/30",
        className
      )}
      {...props}
    />
  )
}
function TableFooter({ className, ...props }: React.HTMLAttributes<HTMLTableSectionElement>) {
  return (
    <tfoot
      data-slot="table-footer"
      className={cn(
        "bg-muted/40 text-muted-foreground border-t border-border font-medium [&>tr]:last:border-b-0",
        className
      )}
      {...props}
    />
  )
}
function TableRow({ className, ...props }: React.HTMLAttributes<HTMLTableRowElement>) {
  return (
    <tr
      data-slot="table-row"
      className={cn("transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted", className)}
      {...props}
    />
  )
}
function TableHead({ className, sortable = false, sortDirection = "asc", onSort, children, ...props }: React.HTMLAttributes<HTMLTableCellElement> & { sortable?: boolean, sortDirection?: "asc" | "desc", onSort?: () => void }) {
  const { density } = React.useContext(TableContext)
  const pad = density === "compact" ? "px-2 py-1" : "px-3 py-2"
  const ariaSort = sortable ? (sortDirection === "asc" ? "ascending" : sortDirection === "desc" ? "descending" : "none") : undefined

  return (
    <th
      data-slot="table-head"
      aria-sort={ariaSort}
      className={cn(
        `${pad} text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground border-r border-border last:border-r-0 align-middle`,
        sortable && "select-none",
        className
      )}
      {...props}
    >
      {sortable ? (
        <button
          type="button"
          onClick={onSort}
          className="group inline-flex items-center gap-1.5 text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-ring/40 rounded cursor-pointer"
        >
          <span>{children}</span>
          <ArrowUpDown className="h-3.5 w-3.5 text-muted-foreground group-hover:text-foreground" />
          {sortDirection === "asc" && <ArrowUp className="h-3.5 w-3.5" />}
          {sortDirection === "desc" && <ArrowDown className="h-3.5 w-3.5" />}
        </button>
      ) : (
        children
      )}
    </th>
  )
}
function TableCell({ className, ...props }: React.HTMLAttributes<HTMLTableCellElement>) {
  const { density } = React.useContext(TableContext)
  const pad = density === "compact" ? "px-2 py-1" : "px-3 py-4"
  return (
    <td
      data-slot="table-cell"
      className={cn(`${pad} text-foreground border-r border-border last:border-r-0 align-middle`, className)}
      {...props}
    />
  )
}
function TableCaption({ className, ...props }: React.HTMLAttributes<HTMLTableCaptionElement> & { className?: string }) {
  return (
    <caption data-slot="table-caption" className={cn("mt-3 text-sm text-muted-foreground", className)} {...props} />
  )
}

export {
  Table,
  TableHeader,
  TableBody,
  TableFooter,
  TableHead,
  TableRow,
  TableCell,
  TableCaption,
}
