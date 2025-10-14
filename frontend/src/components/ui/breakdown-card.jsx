import * as React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { AlertTriangle, ShieldCheck, Moon, ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"

/**
 * DeviceStatusSummaryCard (JSX) with urgency styles
 * ------------------------------------------------------------------
 * Adds `urgency` visual treatment.
 * - `urgency="default"` (previous look)
 * - `urgency="high"` (red, attention-grabbing header + white rows)
 */

const statusConfig = {
  alert: { icon: AlertTriangle, color: "text-red-600", text: "Need attention" },
  check: { icon: ShieldCheck, color: "text-green-600", text: "Compliant" },
  dormant: { icon: Moon, color: "text-gray-500", text: "Dormant" },
}

function Row({ item, accentColor, showChevron }) {
  const cfg = statusConfig[item.status] || {}
  const Icon = cfg.icon || ShieldCheck
  const isInteractive = Boolean(item.onClick)
  const color = accentColor || cfg.color || "text-foreground"

  return (
    <div
      role={isInteractive ? "button" : undefined}
      tabIndex={isInteractive ? 0 : -1}
      onClick={item.onClick}
      onKeyDown={(e) => {
        if (isInteractive && (e.key === "Enter" || e.key === " ")) {
          e.preventDefault()
          item.onClick?.()
        }
      }}
      className={[
        "flex items-center justify-between rounded-lg px-2 py-2",
        isInteractive && "cursor-pointer outline-none hover:bg-muted/50 focus-visible:ring-2 focus-visible:ring-ring/40",
      ].filter(Boolean).join(" ")}
      aria-label={`${item.label} — ${item.count}`}
    >
      <div className={`flex items-center gap-2 ${color}`}>
        <Icon className="h-4 w-4" aria-hidden />
        <span className="text-sm font-medium">{item.label}</span>
      </div>

      <div className="flex items-center gap-2">
        <span className={`text-sm font-semibold ${color}`}>{item.count}</span>
        {showChevron && <ChevronRight className={`h-4 w-4 ${color}`} aria-hidden />}
      </div>
    </div>
  )
}

export function DeviceStatusSummaryCard({
  total,
  items,
  title,
  onHeaderClick,
  className,
  urgency = "default", // "default" | "high"
  headerLabel, // optional override for header text
}) {
  const interactiveHeader = Boolean(onHeaderClick)
  const isHigh = urgency === "high"

  // Urgency-driven styles
  const cardClasses = [
    "overflow-hidden px-0 py-0 gap-0",
    isHigh ? "border border-red-700 bg-red-700 text-red-50" : "",
    className,
  ].filter(Boolean).join(" ")

  const headerTextClasses = [
    "flex items-center justify-between text-sm",
    isHigh ? "text-red-50" : "text-muted-foreground",
    interactiveHeader && "cursor-pointer rounded-lg focus-visible:ring-2 focus-visible:ring-ring/40",
  ].filter(Boolean).join(" ")

  // For high urgency, rows are on white with red accents
  const rowWrapperClasses = isHigh ? "bg-white rounded-xl divide-y divide-red-200 border border-red-200" : ""
  const rowAccentColor = isHigh ? "text-red-700" : undefined
  const showChevron = isHigh

  return (
    <Card className={cardClasses}>
      <CardHeader className={cn(isHigh, "px-3 py-2")}>
        <CardTitle>
          <div
            role={interactiveHeader ? "button" : undefined}
            tabIndex={interactiveHeader ? 0 : -1}
            onClick={onHeaderClick}
            onKeyDown={(e) => {
              if (interactiveHeader && (e.key === "Enter" || e.key === " ")) {
                e.preventDefault()
                onHeaderClick?.()
              }
            }}
            className={headerTextClasses}
            aria-label={`${total} monitored devices`}
          >
            <span className="flex items-center gap-2">
              {isHigh && <AlertTriangle className="h-4 w-4" aria-hidden />}
              {title ? title : `${total} monitored devices`}
            </span>
            {interactiveHeader && <ChevronRight className="h-4 w-4" aria-hidden />}
          </div>
        </CardTitle>
      </CardHeader>

      {!isHigh && <Separator />}

      <CardContent className={cn(isHigh, "px-1 py-1")}>
        <div className={isHigh ? rowWrapperClasses : "space-y-0"}>
          {items.map((item, idx) => (
            <Row key={idx} item={item} accentColor={rowAccentColor} showChevron={showChevron} />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}