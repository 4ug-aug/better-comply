import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  getDocumentWithVersionsDocumentsDocIdVersionsGetOptions,
  getParsedDocumentDocumentsDocIdVersionsVersionIdParsedGetOptions,
} from '@/queries/@tanstack/react-query.gen';
import { useDocumentStore } from '../store/documentStore';
import { DocumentDetailLayout } from '../components/DocumentDetailLayout';
import { ParsedContentViewer } from '../components/ParsedContentViewer';
import { DocumentMetadata } from '../components/DocumentMetadata';
import { DocumentVersionsList } from '../components/DocumentVersionsList';
import { Button } from '@/components/ui/button';
import { ChevronLeft } from 'lucide-react';

export function DocumentDetailPage() {
  const { id } = useParams<{ id: string | undefined }>();
  const navigate = useNavigate();

  const { selectedVersionId, setSelectedVersion } = useDocumentStore();

  const { data: docData, isLoading: isLoadingDoc } = useQuery(
    getDocumentWithVersionsDocumentsDocIdVersionsGetOptions({
      path: { doc_id: parseInt(id || '0') },
    })
  );

  const document = docData as any;
  const versions = document?.versions || [];

  // Set default version on load
  const activeVersionId = selectedVersionId || (versions.length > 0 ? versions[0].id : null);

  const { data: parsedData, isLoading: isLoadingParsed, error: parseError } = useQuery(
    getParsedDocumentDocumentsDocIdVersionsVersionIdParsedGetOptions({
        path: { doc_id: parseInt(id || '0'), version_id: activeVersionId },
      })
    );

  const handleVersionSelect = (versionId: number) => {
    setSelectedVersion(versionId);
  };

  if (isLoadingDoc) {
    return (
      <div className="container mx-auto py-8">
        <p className="text-muted-foreground">Loading document...</p>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="container mx-auto py-8">
        <p className="text-red-500">Document not found</p>
      </div>
    );
  }

  return (
    <div className="max-h-screen">
      <div className="container mx-auto py-4">
        <Button
          variant="ghost"
          onClick={() => navigate('/documents')}
        >
          <ChevronLeft className="h-4 w-4 mr-2" />
          Back to Documents
        </Button>
      </div>

      <DocumentDetailLayout
        mainContent={
          <ParsedContentViewer
            parsedContent={parsedData as any}
            isLoading={isLoadingParsed}
            error={parseError as any}
          />
        }
        sidebar={
          <div className="space-y-4">
            <DocumentMetadata document={document} />
            <DocumentVersionsList
              versions={versions}
              selectedVersionId={activeVersionId}
              onVersionSelect={handleVersionSelect}
              isLoading={isLoadingDoc}
            />
          </div>
        }
      />
    </div>
  );
}
