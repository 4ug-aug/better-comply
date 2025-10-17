import { format } from 'date-fns';
import {
  Description,
  DescriptionItem,
  DescriptionTerm,
  DescriptionDetails,
} from '@/components/ui/description';

interface DocumentMetadataProps {
  document: {
    id: number;
    source_id: number;
    source_url: string;
    published_date: string | null;
    language: string;
    created_at: string;
    updated_at: string;
  };
}

export function DocumentMetadata({ document }: DocumentMetadataProps) {
  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), 'PPp');
    } catch {
      return dateString;
    }
  };

  return (
    <Description type="vertical">
      <DescriptionItem>
        <DescriptionTerm>Document ID</DescriptionTerm>
        <DescriptionDetails>{document.id}</DescriptionDetails>
      </DescriptionItem>

      <DescriptionItem>
        <DescriptionTerm>Source ID</DescriptionTerm>
        <DescriptionDetails>{document.source_id}</DescriptionDetails>
      </DescriptionItem>

      <DescriptionItem>
        <DescriptionTerm>Source URL</DescriptionTerm>
        <DescriptionDetails className="break-all">
          <a
            href={document.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            {document.source_url}
          </a>
        </DescriptionDetails>
      </DescriptionItem>

      <DescriptionItem>
        <DescriptionTerm>Language</DescriptionTerm>
        <DescriptionDetails>{document.language.toUpperCase()}</DescriptionDetails>
      </DescriptionItem>

      {document.published_date && (
        <DescriptionItem>
          <DescriptionTerm>Published Date</DescriptionTerm>
          <DescriptionDetails>{document.published_date}</DescriptionDetails>
        </DescriptionItem>
      )}

      <DescriptionItem>
        <DescriptionTerm>Created</DescriptionTerm>
        <DescriptionDetails>{formatDate(document.created_at)}</DescriptionDetails>
      </DescriptionItem>

      <DescriptionItem>
        <DescriptionTerm>Updated</DescriptionTerm>
        <DescriptionDetails>{formatDate(document.updated_at)}</DescriptionDetails>
      </DescriptionItem>
    </Description>
  );
}
