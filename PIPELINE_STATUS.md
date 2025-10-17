# Complete Pipeline Status

## Overview

The HTML parsing pipeline is now fully scaffolded end-to-end with all consumers, tasks, and event routing in place. Each stage emits appropriate Kafka events and handles errors by emitting `run.failed`.

## Complete Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        FULL PIPELINE ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────────────┘

[1] SUBSCRIPTION SCHEDULED
    subs.schedule event (subscription_id, run_id, trace_id)
         ↓
    SubscriptionScheduledConsumer
         ↓
    handle_subscription_scheduled()
         ├→ emit_run_started(run_id) → RUN: PENDING → RUNNING
         ├→ fetch subscription & source
         └→ emit crawl.request(url, source_id, run_id, trace_id)
         ├→ ✓ emit run.failed on exception → RUN: FAILED

[2] CRAWL REQUEST
    crawl.request event (url, source_id, run_id, trace_id, crawl_request_id)
         ↓
    CrawlRequestConsumer
         ↓
    crawl_url(url, source_id, run_id, trace_id, crawl_request_id)
         ├→ emit_run_started(run_id)
         ├→ download page from URL
         ├→ store raw artifact to MinIO: raw/{source_id}/{yyyy}/{mm}/{dd}/{sha256}.bin
         ├→ create Artifact record (blob_uri, content_type, fetch_hash)
         └→ emit crawl.result(artifact_id, blob_uri, source_url, source_id, run_id, trace_id)
         ├→ ✓ emit run.failed on exception → RUN: FAILED

[3] PARSE REQUEST (Crawl Result → Parse)
    crawl.result event (artifact_id, blob_uri, source_url, source_id, run_id, trace_id)
         ↓
    CrawlResultConsumer → routes to job_type="parse.content"
         ↓
    parse_crawled_content(artifact_id, blob_uri, source_url, source_id, run_id, trace_id)
         ├→ emit_run_started(run_id)
         ├→ download artifact from MinIO
         ├→ detect encoding (content-type → chardet)
         ├→ parse HTML with trafilatura
         ├→ extract sections with byte offsets
         ├→ create/get Document by source_url
         ├→ create DocumentVersion with content_hash
         ├→ store parsed JSON to MinIO: parsed/{doc_id}/{version_id}.json
         ├→ store raw metadata to MinIO: raw_meta/{sha256}.json
         └→ emit parse.result(doc_id, version_id, parsed_uri, section_count, run_id, trace_id)
         ├→ ✓ emit run.failed on exception → RUN: FAILED

[4] VERSIONING REQUEST (Parse Result → Versioning)
    parse.result event (doc_id, version_id, parsed_uri, run_id, trace_id)
         ↓
    ParseResultConsumer → routes to job_type="version.document"
         ↓
    version_document(doc_id, version_id, parsed_uri, run_id, trace_id)
         ├→ emit_run_started(run_id)
         ├→ [PLACEHOLDER] compare with previous version
         ├→ [PLACEHOLDER] compute diffs
         ├→ [PLACEHOLDER] store version metadata
         └→ [PLACEHOLDER] emit versioning.result(doc_id, version_id, run_id, trace_id)
         ├→ ✓ emit run.failed on exception → RUN: FAILED

[5] VERSIONING RESULT (Versioning → Delivery)
    versioning.result event (doc_id, version_id, run_id, trace_id)
         ↓
    VersioningResultConsumer → routes to job_type="deliver.document"
         ↓
    deliver_document(doc_id, version_id, run_id, trace_id)
         ├→ emit_run_started(run_id)
         ├→ [PLACEHOLDER] send to downstream systems
         ├→ [PLACEHOLDER] emit delivery notifications
         └→ [PLACEHOLDER] emit delivery.result(doc_id, version_id, run_id, trace_id)
         ├→ ✓ emit run.failed on exception → RUN: FAILED

[6] DELIVERY RESULT (Terminal Event - Marks Run as COMPLETED)
    delivery.result event (doc_id, version_id, run_id, trace_id, result)
         ↓
    DeliveryResultConsumer (TERMINAL - doesn't dispatch, directly handles)
         ├→ emit_run_completed(run_id) → RUN: RUNNING → COMPLETED
         └→ ✓ pipeline successfully completes!

┌─────────────────────────────────────────────────────────────────────────┐
│                         RUN STATUS UPDATES                              │
├─────────────────────────────────────────────────────────────────────────┤
│ Each event → run.status event emitted                                    │
│     ↓                                                                     │
│ RunStatusConsumer listens to run.status topic                            │
│     ↓                                                                     │
│ update_run_status task updates Run record in database                    │
│                                                                           │
│ RUN LIFECYCLE:                                                            │
│   PENDING  → RUNNING (first task starts)                                │
│   RUNNING → COMPLETED (final delivery.result received)                  │
│   RUNNING → FAILED (any exception in pipeline)                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Kafka Topics

| Topic | Producer | Consumer | Purpose |
|-------|----------|----------|---------|
| subs.schedule | Scheduler | SubscriptionScheduledConsumer | Trigger subscriptions |
| crawl.request | handle_subscription_scheduled | CrawlRequestConsumer | Request URL crawling |
| crawl.result | crawl_url | CrawlResultConsumer | Route to parsing |
| parse.result | parse_crawled_content | ParseResultConsumer | Route to versioning |
| versioning.result | version_document | VersioningResultConsumer | Route to delivery |
| delivery.result | deliver_document | DeliveryResultConsumer | Complete pipeline |
| run.status | All tasks (via emit_run_*) | RunStatusConsumer | Update run status |

## MinIO Artifact Structure

```
Raw Artifacts:
  raw/{source_id}/{yyyy}/{mm}/{dd}/{sha256}.bin
  raw_meta/{sha256}.json

Parsed Artifacts:
  parsed/{doc_id}/{version_id}.json
  diffs/{doc_id}/{version_id}.json (future)
```

## Database Schema

### Documents Table
- `id` - Primary key
- `source_id` - Foreign key to Sources
- `source_url` - Unique canonical URL
- `published_date` - Extracted from page
- `language` - Detected language (default: "en")
- `created_at`, `updated_at` - Timestamps

### Document Versions Table
- `id` - Primary key
- `document_id` - Foreign key to Documents
- `parsed_uri` - s3://artifacts/parsed/{doc_id}/{version_id}.json
- `diff_uri` - s3://artifacts/diffs/{doc_id}/{version_id}.json (nullable)
- `content_hash` - SHA256 of parsed JSON
- `created_at` - Timestamp

### Artifacts Table (existing)
- Stores raw crawled content metadata
- Links to Run for pipeline tracking

### Runs Table (existing)
- `status` - PENDING → RUNNING → COMPLETED/FAILED
- Updated by `update_run_status` task via `run.status` events

## Files Created/Modified

### Created
- ✅ `backend/models/document.py` - Document and DocumentVersion models
- ✅ `backend/jobs_engine/schemas/parse_schemas.py` - Parse event schemas
- ✅ `backend/jobs_engine/utils/minio_artifact_handler.py` - MinIO utilities
- ✅ `backend/jobs_engine/utils/html_parser.py` - HTML parsing with trafilatura
- ✅ `backend/jobs_engine/consumers/parse_result.py` - Parse → Versioning
- ✅ `backend/jobs_engine/consumers/versioning_result.py` - Versioning → Delivery
- ✅ `backend/jobs_engine/consumers/delivery_result.py` - Terminal consumer

### Modified
- ✅ `backend/jobs_engine/tasks/crawl_tasks.py` - Updated signatures & error handling
- ✅ `backend/jobs_engine/consumers/crawl_result.py` - Added source_id extraction
- ✅ `backend/jobs_engine/events_handler_worker.py` - Registered new consumers
- ✅ `backend/jobs_engine/utils/html_parser.py` - Enhanced with trafilatura + fallback

## Task Signatures

### handle_subscription_scheduled
```python
def handle_subscription_scheduled(
    subscription_id: int,
    run_id: int,
    trace_id: str = None,
    **kwargs
)
```

### crawl_url
```python
def crawl_url(
    url: str,
    source_id: int,
    run_id: int,
    crawl_request_id: str,
    trace_id: str,
    **kwargs
)
```

### parse_crawled_content ✅ IMPLEMENTED
```python
def parse_crawled_content(
    artifact_id: int,
    blob_uri: str,
    run_id: int,
    trace_id: str,
    source_url: str = None,
    source_id: int = None,
    **kwargs
)
```

### version_document ✅ SCAFFOLDED
```python
def version_document(
    doc_id: int,
    version_id: int,
    parsed_uri: str,
    run_id: int,
    trace_id: str,
    **kwargs
)
```

### deliver_document ✅ SCAFFOLDED
```python
def deliver_document(
    doc_id: int,
    version_id: int,
    run_id: int,
    trace_id: str,
    **kwargs
)
```

### update_run_status
```python
def update_run_status(
    run_id: int,
    status: str,  # RUNNING, COMPLETED, FAILED
    error_message: Optional[str] = None,
    error_traceback: Optional[str] = None,
    trace_id: Optional[str] = None,
    **kwargs
)
```

## Implementation Status

| Phase | Component | Status |
|-------|-----------|--------|
| 1 | Subscription Scheduling | ✅ Complete |
| 2 | URL Crawling | ✅ Complete |
| 3 | HTML Parsing | ✅ Complete |
| 4 | Versioning | 🔶 Scaffolded |
| 5 | Delivery | 🔶 Scaffolded |
| 6 | Run Status Tracking | ✅ Complete |

## Next Steps

1. Implement `version_document()` to compute document diffs
2. Implement `deliver_document()` to send documents to downstream systems
3. Both should emit their `.result` events before completion
4. Add comprehensive integration tests
5. Monitor pipeline latency and optimize as needed

## Error Handling

Every task:
- Emits `run.started` at beginning
- Catches exceptions and emits `run.failed` with traceback
- Failures immediately halt the pipeline
- run.failed events mark the run as FAILED
