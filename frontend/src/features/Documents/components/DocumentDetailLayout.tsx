import { type ReactNode } from 'react';

interface DocumentDetailLayoutProps {
  mainContent: ReactNode;
  sidebar: ReactNode;
}

export function DocumentDetailLayout({
  mainContent,
  sidebar,
}: DocumentDetailLayoutProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
      {/* Main content area */}
      <div className="lg:col-span-3 max-h-screen rounded-lg border">
        {mainContent}
      </div>

      {/* Right sidebar */}
      <div className="lg:col-span-2 space-y-4 h-fit sticky top-2">
        {sidebar}
      </div>
    </div>
  );
}
