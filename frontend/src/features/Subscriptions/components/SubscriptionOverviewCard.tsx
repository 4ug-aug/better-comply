interface SubscriptionOverviewCardProps {
  status: string
  schedule: string
  lastRunAt: string | null
  nextRunAt: string | null
}

export function SubscriptionOverviewCard({
  status,
  schedule,
  lastRunAt,
  nextRunAt,
}: SubscriptionOverviewCardProps) {
  return (
    <div className="border rounded-lg p-4">
      <div className="text-sm font-medium mb-2">Overview</div>
      <div className="text-sm">Status: <span className="font-mono text-xs">{status}</span></div>
      <div className="text-sm">Schedule: <span className="font-mono text-xs">{schedule}</span></div>
      <div className="text-xs text-muted-foreground mt-1">Last: {lastRunAt ? new Date(lastRunAt).toLocaleString() : '-'}</div>
      <div className="text-xs text-muted-foreground">Next: {nextRunAt ? new Date(nextRunAt).toLocaleString() : '-'}</div>
    </div>
  )
}
