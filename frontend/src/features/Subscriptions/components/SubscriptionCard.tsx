import { Link } from 'react-router-dom'

export type SubscriptionSummary = {
  id: number
  schedule: string
  last_run_at?: string | null
  next_run_at?: string | null
  status: string
}

export function SubscriptionCard({ sub }: { sub: SubscriptionSummary }) {
  return (
    <Link to={`/subscriptions/${sub.id}`} className="block border rounded-lg p-4 hover:bg-muted/30 transition">
      <div className="flex items-center justify-between mb-2">
        <div className="text-sm text-muted-foreground">ID #{sub.id}</div>
        <span className="text-xs px-2 py-0.5 rounded border">{sub.status}</span>
      </div>
      <div className="text-sm">Schedule: <span className="font-mono">{sub.schedule}</span></div>
      <div className="text-xs text-muted-foreground mt-1">Last: {new Date(sub.last_run_at ?? '').toLocaleString()}</div>
      <div className="text-xs text-muted-foreground">Next: {new Date(sub.next_run_at ?? '').toLocaleString()}</div>
    </Link>
  )
}

export default SubscriptionCard


