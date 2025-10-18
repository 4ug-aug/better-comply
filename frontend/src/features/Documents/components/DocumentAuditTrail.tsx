import { useQuery } from '@tanstack/react-query';
import { getVersionAuditTrailDocumentsDocIdVersionsVersionIdAuditTrailGetOptions } from '@/queries/@tanstack/react-query.gen';
import { Timeline } from '@/components/ui/timeline';
import { Loader2 } from 'lucide-react';
import { format } from 'date-fns';
import { formatDistanceToNow } from 'date-fns';
import type { AuditTrailEventOut } from '@/queries/types.gen';
import { useEffect } from 'react';

interface DocumentAuditTrailProps {
  docId: number;
  versionId: number;
  isLoading?: boolean;
}

function getStatusForTimeline(status: string): 'done' | 'success' | 'warning' | 'pending' {
  if (status === 'COMPLETED' || status === 'PUBLISHED') {
    return 'success';
  }
  if (status === 'FAILED') {
    return 'warning';
  }
  if (status === 'PENDING' || status === 'RUNNING') {
    return 'pending';
  }
  return 'done';
}

function formatEventTitle(eventType: string): string {
  // Convert event types like "versioning.result" to "Versioning Result"
  return eventType
    .split('.')
    .map(part => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

function formatTimestamp(timestamp: string | Date): string {
  try {
    const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
    return formatDistanceToNow(date, { addSuffix: true });
  } catch {
    return 'Unknown time';
  }
}

function EventDetails({ event }: { event: AuditTrailEventOut }) {
  return (
    <div className="space-y-3 text-xs">
      <div className="grid grid-cols-2 gap-2">
        <div>
          <span className="font-semibold text-gray-700">Event ID:</span>
          <p className="text-gray-600">{event.event_id}</p>
        </div>
        <div>
          <span className="font-semibold text-gray-700">Status:</span>
          <p className="text-gray-600">{event.status}</p>
        </div>
      </div>

      {event.run_id && (
        <div className="grid grid-cols-2 gap-2">
          <div>
            <span className="font-semibold text-gray-700">Run ID:</span>
            <p className="text-gray-600">{event.run_id}</p>
          </div>
          {event.run_kind && (
            <div>
              <span className="font-semibold text-gray-700">Run Kind:</span>
              <p className="text-gray-600">{event.run_kind}</p>
            </div>
          )}
        </div>
      )}

      {event.artifact_ids.length > 0 && (
        <div>
          <span className="font-semibold text-gray-700">Artifact IDs:</span>
          <p className="text-gray-600">{event.artifact_ids.join(', ')}</p>
        </div>
      )}

      {event.artifact_uris.length > 0 && (
        <div>
          <span className="font-semibold text-gray-700">Artifact URIs:</span>
          <div className="space-y-1">
            {event.artifact_uris.map((uri, idx) => (
              <p key={idx} className="text-gray-600 break-all text-xs">{uri}</p>
            ))}
          </div>
        </div>
      )}

      {event.version_id && (
        <div className="grid grid-cols-2 gap-2">
          <div>
            <span className="font-semibold text-gray-700">Version ID:</span>
            <p className="text-gray-600">{event.version_id}</p>
          </div>
          {event.content_hash && (
            <div>
              <span className="font-semibold text-gray-700">Content Hash:</span>
              <p className="text-gray-600 font-mono text-xs">{event.content_hash.slice(0, 7)}</p>
            </div>
          )}
        </div>
      )}

      {event.parsed_uri && (
        <div>
          <span className="font-semibold text-gray-700">Parsed URI:</span>
          <p className="text-gray-600 break-all text-xs">{event.parsed_uri}</p>
        </div>
      )}

      {event.diff_uri && (
        <div>
          <span className="font-semibold text-gray-700">Diff URI:</span>
          <p className="text-gray-600 break-all text-xs">{event.diff_uri}</p>
        </div>
      )}

      {event.error && (
        <div className="bg-red-50 border border-red-200 rounded p-2">
          <span className="font-semibold text-red-700">Error:</span>
          <p className="text-red-600 text-xs mt-1">{event.error}</p>
        </div>
      )}

      <div className="text-xs text-gray-500 pt-2 border-t border-gray-200">
        {format(new Date(event.timestamp), 'PPp')}
      </div>
    </div>
  );
}

export function DocumentAuditTrail({ docId, versionId, isLoading: externalLoading }: DocumentAuditTrailProps) {
  const { data: auditData, isLoading, refetch } = useQuery(
    getVersionAuditTrailDocumentsDocIdVersionsVersionIdAuditTrailGetOptions({
      path: { doc_id: docId, version_id: versionId },
    })
  );

  // Refetch audit trail when version changes
  useEffect(() => {
    refetch();
  }, [versionId, refetch]);

  const loading = externalLoading || isLoading;
  const events = (auditData as any)?.events || [];

  if (loading) {
    return (
      <div className="p-4 text-sm text-muted-foreground inline-flex items-center gap-2">
        <Loader2 className="h-4 w-4 animate-spin" /> Loading audit trail
      </div>
    );
  }

  if (!events || events.length === 0) {
    return (
      <div className="p-4 text-sm text-muted-foreground">
        No audit trail events for this version
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="px-2">
        <h3 className="font-semibold text-sm">Audit Trail</h3>
        <span className="text-xs text-muted-foreground">
          Processing history for v{versionId}
        </span>
      </div>
      <div className="rounded-xl border bg-white p-4">
        <Timeline subtitle="">
          {events.map((event: AuditTrailEventOut) => (
            <Timeline.Item
              key={`${event.event_type}-${event.event_id}`}
              status={getStatusForTimeline(event.status)}
              title={formatEventTitle(event.event_type)}
              timestamp={formatTimestamp(event.timestamp)}
              section={<EventDetails event={event} />}
            />
          ))}
        </Timeline>
      </div>
    </div>
  );
}
