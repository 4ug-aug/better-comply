import { useState } from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import {
  Item,
  ItemActions,
  ItemContent,
  ItemTitle,
} from "@/components/ui/item"
import { Layers, AlertCircle, ChevronRightIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ParsedSection {
  id: number;
  level: number;
  heading: string;
  text: string;
  sha256: string;
  byte_offset_start: number;
  byte_offset_end: number;
  tables: Array<Record<string, unknown>>;
  language: string;
}

interface ParsedContent {
  source_url: string;
  published_date: string | null;
  language: string;
  fetch_timestamp: string;
  sections: ParsedSection[];
}

interface ParsedContentViewerProps {
  parsedContent: ParsedContent | null;
  isLoading: boolean;
  error: Error | null;
}

function SectionOutline({ sections, selectedId, onSelectSection }: { sections: ParsedSection[], selectedId: number, onSelectSection: (id: number) => void }) {
  if (!sections || sections.length === 0) {
    return (
      <div className="p-4 text-sm text-muted-foreground">
        No sections available
      </div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="flex w-full max-w-md flex-col gap-2 p-3">
        {sections.map((section: ParsedSection) => {
          return (
            <a href={`#section-${section.id}`} onClick={() => onSelectSection(section.id)}>
              <Item key={section.id} variant="outline" size="sm" className={cn(selectedId === section.id && 'bg-primary/10')}>              
                <ItemContent>
                  <ItemTitle>{section.heading}</ItemTitle>
                </ItemContent>
                <ItemActions>
                  <ChevronRightIcon className="size-4" />
                </ItemActions>
              </Item>
            </a>
          );
        })}
      </div>
    </ScrollArea>
  );
}

function SectionDetail({ section }: { section: ParsedSection }) {
  if (!section) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        <Layers className="h-12 w-12 mx-auto mb-4 opacity-50" />
        <p>Select a section to view details</p>
      </div>
    );
  }

  const headingLevel = Math.min(Math.max(section.level, 1), 6);
  const HeadingTag = `h${headingLevel}` as React.ElementType;

  return (
    <ScrollArea className="h-full border-l">
      <div className="space-y-6 p-6">
        {/* Section Header */}
        <div className="border-b pb-4">
          <div className="flex items-center gap-2 mb-2">
            <Badge variant="outline">Section {section.id}</Badge>
            <Badge variant="secondary">{`H${section.level}`}</Badge>
            <span className="text-xs text-muted-foreground">
              {section.byte_offset_start} - {section.byte_offset_end} bytes
            </span>
          </div>
          <HeadingTag className="text-2xl font-bold break-words">
            {section.heading}
          </HeadingTag>
        </div>

        {/* Section Content */}
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <p className="text-base text-foreground whitespace-pre-wrap break-words leading-relaxed">
            {section.text}
          </p>
        </div>

        {/* Section Metadata */}
        <div className="border-t pt-4">
          <h4 className="text-sm font-semibold mb-3">Metadata</h4>
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Content Hash:</dt>
              <dd className="font-mono text-xs">{section.sha256.slice(0, 12)}...</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Language:</dt>
              <dd>{section.language}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Byte Range:</dt>
              <dd className="font-mono text-xs">
                {section.byte_offset_start} - {section.byte_offset_end}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </ScrollArea>
  );
}

export function ParsedContentViewer({
  parsedContent,
  isLoading,
  error,
}: ParsedContentViewerProps) {
  const [selectedSectionId, setSelectedSectionId] = useState<number | null>(null);
  const sections = parsedContent?.sections || [];
  const selectedSection = sections.find((s) => s.id === selectedSectionId) || sections[0] || null;

  if (isLoading) {
    return (
      <div className="grid grid-cols-3 gap-4 h-full">
        <div className="space-y-2">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
        <div className="col-span-2 space-y-4">
          <Skeleton className="h-8 w-1/2" />
          <Skeleton className="h-32 w-full" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 flex flex-col items-center justify-center gap-4">
        <AlertCircle className="h-12 w-12 text-red-500" />
        <div>
          <p className="font-semibold text-red-500">Error loading content</p>
          <p className="text-sm text-muted-foreground">{error.message}</p>
        </div>
      </div>
    );
  }

  if (!parsedContent || sections.length === 0) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        <Layers className="h-12 w-12 mx-auto mb-4 opacity-50" />
        <p>No content available</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-3 h-full">
      {/* Left Sidebar - Section Overview */}
      <div className="col-span-1 bg-muted/20 overflow-hidden">
        <div className="p-3">
          <h3 className="font-semibold text-sm flex items-center gap-2">
            <Layers className="h-4 w-4" />
            Sections ({sections.length})
          </h3>
        </div>
        <SectionOutline
          sections={sections}
          selectedId={selectedSectionId || sections[0]?.id}
          onSelectSection={setSelectedSectionId}
        />
      </div>

      {/* Right Content Area - Section Detail */}
      <div className="col-span-2 overflow-hidden">
        <SectionDetail section={selectedSection} />
      </div>
    </div>
  );
}
