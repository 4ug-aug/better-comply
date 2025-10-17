import * as React from "react"

import { cn } from "@/lib/utils"

const DescriptionContext = React.createContext({ type: "vertical" })

function Description({
  className,
  as: Comp = "dl",
  type = "vertical",
  ...props
}) {
  const gridClass = type === "horizontal" 
    ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4" 
    : "grid gap-4"
  
  return (
    <DescriptionContext.Provider value={{ type }}>
      <Comp
        data-slot="description"
        className={cn("bg-description text-description-foreground p-4 rounded-xl shadow-sm border border-border", gridClass, className)}
        {...props} />
    </DescriptionContext.Provider>
  );
}

function DescriptionItem({
  className,
  as: Comp = "div",
  ...props
}) {
  const { type } = React.useContext(DescriptionContext)
  
  const layoutClass = type === "horizontal"
    ? "flex flex-col gap-2"
    : "grid grid-cols-[120px_1fr] sm:grid-cols-[140px_1fr] items-start gap-x-4 gap-y-1"
  
  return (
    <Comp
      data-slot="description-item"
      className={cn(layoutClass, className)}
      {...props} />
  );
}

function DescriptionTerm({
  className,
  as: Comp = "dt",
  ...props
}) {
  const { type } = React.useContext(DescriptionContext)
  
  const termClass = type === "horizontal"
    ? "text-xs font-medium text-muted-foreground uppercase tracking-wide"
    : "text-sm font-medium leading-none"
  
  return (
    <Comp
      data-slot="description-term"
      className={cn(termClass, className)}
      {...props} />
  );
}

function DescriptionDetails({
  className,
  as: Comp = "dd",
  ...props
}) {
  const { type } = React.useContext(DescriptionContext)
  
  const detailsClass = type === "horizontal"
    ? "text-sm font-medium break-words overflow-wrap-anywhere min-w-0"
    : "text-muted-foreground text-sm break-words overflow-wrap-anywhere min-w-0"
  
  return (
    <Comp
      data-slot="description-details"
      className={cn(detailsClass, className)}
      {...props} />
  );
}

export {
  Description,
  DescriptionItem,
  DescriptionTerm,
  DescriptionDetails,
}


