# better-comply
A Better compliance platform.



## Minio Artifacts
Structure:
```
raw/{source}/{yyyy}/{mm}/{dd}/{sha256}.bin
raw_meta/{sha256}.json
parsed/{doc_id}/{version_id}.json
diffs/{doc_id}/{version_id}.json
```

## Kafka Topics
```
subs.schedule - emit due subscriptions.
crawl.request - payload to fetch one URL or API call.
crawl.result - raw artifact refs (MinIO URI + headers + status).
parse.request - pointer to artifact needing extraction.
parse.result - normalized text + structure stored; emit pointer.
versioning.request - to compute new version vs last.
versioning.result - with version ids and diff refs.
delivery.request - downstream delivery jobs.
events.dlq - for poison messages.
```

### JSON format for Kafka messages
```
{
  "event_id": "uuid",
  "event_type": "crawl.result",
  "occurred_at": "2025-10-15T14:12:03Z",
  "trace_id": "uuid",
  "payload": { "...domain fields..." },
  "provenance": {
    "run_id": "run_123",
    "subscription_id": "sub_456",
    "upstream_event_id": "uuid"
  }
}
```