# Observability Dashboard

A live dashboard that streams real-time data about outbox entries and runs using Server-Sent Events (SSE).

## Architecture

### Backend Implementation

**Files Created:**
- `backend/observability/services/observability_service.py` - Service for querying outbox and runs data
- `backend/observability/api/router.py` - FastAPI router with SSE endpoint
- `backend/observability/__init__.py` - Package initialization

**Endpoint:**
- `GET /observability/stream` - Server-Sent Events stream that sends snapshots every 3 seconds

**How it works:**
1. Queries the database for recent outbox entries and runs
2. Packages data into JSON format
3. Streams via SSE to connected clients
4. Updates every 3 seconds with new data
5. Handles client disconnections gracefully

### Frontend Implementation

**Files Created:**
- `frontend/src/features/Observability/pages/ObservabilityPage.tsx` - Main observability page component

**Features:**
- Real-time SSE connection with connection status indicator
- Two live tables displaying:
  - **Outbox**: ID, Event Type, Status, Created At, Attempts
  - **Runs**: ID, Run Kind, Status, Subscription ID, Started At, Ended At
- Color-coded status badges (Pending, Running, Published, Completed, Failed, Cancelled)
- Auto-refreshing with each SSE update

### Integration

- Registered observability router in `backend/main.py`
- Added route `/observability` in `frontend/src/App.tsx`
- Added navigation link in `frontend/src/layouts/sidebar.tsx` with Activity icon

## Data Flow

1. Frontend opens EventSource connection to `/observability/stream`
2. Backend queries database and sends initial snapshot
3. Backend continues to send updates every 3 seconds
4. Frontend parses each event and updates tables
5. User sees live updates as data changes

## Display Specifications

### Outbox Table Columns
- **ID**: Outbox entry ID
- **Event Type**: Type of event (e.g., `subs.schedule`)
- **Status**: PENDING, PUBLISHED, or FAILED (color-coded)
- **Created At**: Formatted timestamp
- **Attempts**: Number of dispatch attempts

### Runs Table Columns
- **ID**: Run ID
- **Run Kind**: CRAWL, PARSE, NORMALIZE, or SCHEDULE
- **Status**: PENDING, RUNNING, COMPLETED, FAILED, or CANCELLED (color-coded)
- **Subscription ID**: Related subscription (if any)
- **Started At**: Formatted timestamp
- **Ended At**: Formatted timestamp or "-" if not finished

## Styling

- Uses shadcn/ui Card components for sections
- Tables with hover effects for interactivity
- Status badges with semantic colors:
  - Yellow for PENDING
  - Blue for RUNNING
  - Green for PUBLISHED/COMPLETED
  - Red for FAILED
  - Gray for CANCELLED

## Future Enhancements

- Add filtering by status or event type
- Add pagination for large datasets
- Add sorting controls
- Add error details modal
- Add auto-scroll to newest entries
- Add pause/resume functionality
