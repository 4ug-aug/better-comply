import { format } from "date-fns";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import {
  Paperclip,
  GitCompare,
  Loader2,
} from "lucide-react";
import { cn } from "@/lib/utils";

type DocumentVersion = {
  id: number;
  parsed_uri: string;
  diff_uri: string;
  created_at: string;
  content_hash: string;
};

function formatDateSafe(dateString: string) {
  try {
    return format(new Date(dateString), "PPp");
  } catch (e) {
    return dateString || "Unknown date";
  }
}

// ---- Component ------------------------------------------------------------
export function DocumentVersionsList({
  versions,
  selectedVersionId,
  onVersionSelect,
  isLoading,
}: {
  versions: DocumentVersion[];
  selectedVersionId: number;
  onVersionSelect: (versionId: number) => void;
  isLoading: boolean;
}) {
  if (isLoading) {
    return (
      <div className="p-4 text-sm text-muted-foreground inline-flex items-center gap-2">
        <Loader2 className="h-4 w-4 animate-spin" /> Loading versions
      </div>
    );
  }

  if (!versions || versions.length === 0) {
    return <div className="p-4 text-sm text-muted-foreground">No versions</div>;
  }

  return (
    <div className="space-y-2">
      <div className="px-2">
        <h3 className="font-semibold text-sm">Versions</h3>
        <span className="text-xs text-muted-foreground">
            There are {versions.length} versions of this document.
            Click on a version to view the content.
        </span>
      </div>
      <ScrollArea className="h-[400px] rounded-xl border">
        <ul className="divide-y">
          {versions.map((v) => {
            const selected = selectedVersionId === v.id;

            return (
              <li
                key={v.id}
                className={cn(
                  "group relative flex items-center gap-3 px-3 py-3 cursor-pointer",
                  selected ? "bg-muted/60" : "hover:bg-muted/40",
                  "bg-muted/60"
                )}
                onClick={() => onVersionSelect && onVersionSelect(v.id)}
              >
                {/* Left accent for selected */}
                <span
                  className={cn(
                    "absolute left-0 top-0 h-full w-0.5 rounded-r bg-primary text-primary-foreground",
                    selected ? "bg-primary text-primary-foreground" : "bg-transparent text-transparent"
                  )}
                />

                {/* Leading icon */}
                <div className="shrink-0 grid place-items-center h-8 w-8 rounded-lg border bg-background">
                    <Paperclip className="h-4 w-4" />
                </div>

                {/* Main content */}
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="truncate text-sm font-medium">
                      {v.parsed_uri}
                    </p>
                    {v.diff_uri ? (
                      <Badge
                        variant="secondary"
                        className="rounded-full px-2 py-0 text-[11px] font-medium inline-flex items-center gap-1"
                        onClick={(e) => {
                          e.stopPropagation();
                          // consumer can handle via parent on row click or add a handler here
                        }}
                      >
                        <GitCompare className="h-3 w-3" /> diff
                      </Badge>
                    ) : null}
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    v{v.id} • {formatDateSafe(v.created_at)} • {String(v.content_hash || "").slice(0, 7)}
                  </p>
                </div>
              </li>
            );
          })}
        </ul>
      </ScrollArea>
    </div>
  );
}