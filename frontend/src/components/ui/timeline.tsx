// Timeline Component
// - Uses Tailwind utility classes and lucide-react icons
// - Minimal, clean design matching modern UX patterns

import * as React from "react";
import { cn } from "@/lib/utils";
import { Check, AlertCircle, ChevronDown } from "lucide-react";

const statusConfig = {
  done: {
    icon: Check,
    iconBg: "bg-gray-300 text-white",
    lineBg: "bg-gray-200",
  },
  success: {
    icon: Check,
    iconBg: "bg-green-600 text-white",
    lineBg: "bg-green-200",
  },
  warning: {
    icon: AlertCircle,
    iconBg: "bg-orange-500 text-white",
    lineBg: "bg-orange-200",
  },
  pending: {
    icon: Check,
    iconBg: "bg-gray-200 text-gray-500",
    lineBg: "bg-gray-100",
  },
};

export function Timeline({ title, subtitle, className, children, ...props }: React.ComponentProps<"div"> & { title?: string, subtitle?: string, children?: React.ReactNode }) {
  return (
    <div className={cn("w-full", className)} {...props}>
      {(title || subtitle) && (
        <header className="mb-6 space-y-1">
          {title && <h2 className="text-lg font-semibold">{title}</h2>}
          {subtitle && <p className="text-sm text-gray-600">{subtitle}</p>}
        </header>
      )}

      <div className="relative space-y-0">
        {children}
      </div>
    </div>
  );
}

Timeline.Item = function Item({
  status = "pending",
  title,
  timestamp,
  section,
  className,
}: { status?: "done" | "success" | "warning" | "pending", title?: string, timestamp?: string, section?: React.ReactNode, className?: string }) {
  const [isExpanded, setIsExpanded] = React.useState(false);
  const config = statusConfig[status as keyof typeof statusConfig] ?? statusConfig.pending;
  const Icon = config.icon;
  const hasSection = !!section;

  return (
    <div className="relative pl-4 pb-4">
      {/* Status Icon */}
      <div
        className={cn(
          "absolute left-0 top-0.5 flex h-4 w-4 items-center justify-center rounded-full",
          config.iconBg
        )}
      >
        <Icon className="h-3 w-3" />
      </div>

      {/* Content */}
      <div className="flex flex-col">
        <div className="flex items-center justify-between gap-4 pl-3">
          <div className="flex-1">
            <button
              type="button"
              onClick={() => hasSection && setIsExpanded(!isExpanded)}
              className={cn(
                "flex items-center gap-2 text-left",
                hasSection && "cursor-pointer hover:text-gray-700"
              )}
            >
              <p className="text-sm">{title}</p>
              {hasSection && (
                <ChevronDown
                  className={cn(
                    "h-4 w-4 text-gray-500 transition-transform",
                    isExpanded && "rotate-180"
                  )}
                />
              )}
            </button>
          </div>

          {timestamp && (
            <span className="whitespace-nowrap text-sm text-gray-500">
              {timestamp}
            </span>
          )}
        </div>

        {/* Expanded Section */}
        {hasSection && isExpanded && (
          <div className="mt-2 rounded-lg border border-gray-200 bg-gray-50 p-2 ml-3">
            {section}
          </div>
        )}
      </div>
    </div>
  );
};