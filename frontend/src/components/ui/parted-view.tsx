import { CheckCircle, XCircle, CircleQuestionMark } from "lucide-react";
import type { ComponentType } from "react";

type PartedViewProps = {
  data: any[];
  className?: string;
  columns?: string[];
  evidenceIcons?: {
    check: ComponentType;
    cross: ComponentType;
    question: ComponentType;
  };
}

export function PartedView({
  data,
  className,
  columns = ["control", "description", "evidence"],
  evidenceIcons = {
    check: CheckCircle,
    cross: XCircle,
    question: CircleQuestionMark,
  },
}: PartedViewProps) {
  return (
    <div className={className}>
      <table className="w-full table-auto border-collapse">
        <thead>
          <tr className="text-left font-semibold text-sm">
            {columns.map((col, idx) => (
              <th key={idx} className="px-4 py-2">
                {col.charAt(0).toUpperCase() + col.slice(1)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item, idx) => (
            <tr key={idx} className="border-t">
              {columns.map((col, idx) => (
                <td
                  key={idx}
                  className="px-4 py-2 text-sm align-top"
                >
                  {col === "evidence" ? (
                    <div className="flex gap-2 flex-col">
                      {item.evidence.map((evid: { status: keyof typeof evidenceIcons; label: string }, idx: number) => {
                        const Icon = evidenceIcons[evid.status] || CircleQuestionMark;
                        return (
                          <div key={idx} className="flex items-center gap-1">
                            <Icon />
                            <span className="text-xs">{evid.label}</span>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    item[col]
                  )}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
 
 