import { useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { listDocumentsDocumentsGetOptions } from '@/queries/@tanstack/react-query.gen';
import { DocumentsTable } from '../components/DocumentsTable';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export function DocumentsPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const skip = parseInt(searchParams.get('skip') || '0');
  const limit = parseInt(searchParams.get('limit') || '10');

  const { data, isLoading, error } = useQuery(
    listDocumentsDocumentsGetOptions({
      query: { skip, limit },
    })
  );

  const handleRowClick = (docId: number) => {
    navigate(`/documents/${docId}`);
  };

  const handlePreviousPage = () => {
    setSearchParams({
      skip: Math.max(0, skip - limit).toString(),
      limit: limit.toString(),
    });
  };

  const handleNextPage = () => {
    setSearchParams({
      skip: (skip + limit).toString(),
      limit: limit.toString(),
    });
  };

  const documents = data?.items || [];
  const total = data?.total || 0;
  const currentPage = Math.floor(skip / limit) + 1;
  const totalPages = Math.ceil(total / limit);

  return (
    <div className="container mx-auto py-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Documents</h1>
        <p className="text-muted-foreground">
          Browse all parsed documents and their versions
        </p>
      </div>

      <DocumentsTable
        documents={documents as any}
        isLoading={isLoading}
        onRowClick={handleRowClick}
      />

      {error && (
        <div className="p-4 text-red-500 rounded-lg border border-red-200 bg-red-50">
          <p>Failed to load documents</p>
        </div>
      )}

      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          Page {currentPage} of {totalPages} (Total: {total} documents)
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handlePreviousPage}
            disabled={skip === 0}
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleNextPage}
            disabled={skip + limit >= total}
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
