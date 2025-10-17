import { format } from 'date-fns';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';

interface DocumentRow {
  id: number;
  source_url: string;
  language: string;
  published_date: string | null;
  created_at: string;
}

interface DocumentsTableProps {
  documents: DocumentRow[];
  isLoading: boolean;
  onRowClick: (docId: number) => void;
}

export function DocumentsTable({
  documents,
  isLoading,
  onRowClick,
}: DocumentsTableProps) {
  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), 'PPp');
    } catch {
      return dateString;
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-2 p-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        <p>No documents found</p>
      </div>
    );
  }

  return (
    <div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Source URL</TableHead>
            <TableHead>Language</TableHead>
            <TableHead>Published Date</TableHead>
            <TableHead>Created</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {documents.map((doc) => (
            <TableRow
              key={doc.id}
              className="cursor-pointer hover:bg-muted/50"
              onClick={() => onRowClick(doc.id)}
            >
              <TableCell className="max-w-xs truncate break-all truncate-words">
                  {doc.source_url}
              </TableCell>
              <TableCell>{doc.language.toUpperCase()}</TableCell>
              <TableCell className="text-sm text-muted-foreground">
                {doc.published_date || '-'}
              </TableCell>
              <TableCell className="text-sm text-muted-foreground">
                {formatDate(doc.created_at)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
