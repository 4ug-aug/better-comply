import { Card, CardContent } from "@/components/ui/card";
import { ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

type Section = {
    title: string;
    action?: {
        label: string;
        onClick: () => void;
    };
    content: React.ReactNode;
}
 
export function MultiSectionCard({ sections = [], className }: { sections: Section[], className?: string }) {
    return (
      <Card className={cn(className, "py-0")}>
        <CardContent className="p-0">
          <div className="grid gap-2 md:grid-cols-1 xl:grid-cols-3 xl:divide-x md:divide-y xl:divide-y-0">
            {sections.map((section, idx) => (
              <div key={idx} className="px-4 md:py-4 xl:py-4">
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="text-base font-semibold tracking-tight">
                    {section.title}
                  </h3>
                  {section.action && (
                    <button
                      type="button"
                      onClick={section.action.onClick}
                      className="text-sm text-muted-foreground hover:underline inline-flex items-center gap-1"
                    >
                      {section.action.label}
                      <ChevronRight className="h-4 w-4" aria-hidden />
                    </button>
                  )}
                </div>
                <div className="space-y-3">{section.content}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }
 