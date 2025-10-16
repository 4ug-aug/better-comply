import { useParams, Link } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { client } from '@/queries/client.gen'
import {
  enableSubscriptionSchedulingSubscriptionsSubIdEnablePostMutation,
  disableSubscriptionSchedulingSubscriptionsSubIdDisablePostMutation,
  runSubscriptionNowSchedulingSubscriptionsSubIdRunPostMutation,
} from '@/queries/@tanstack/react-query.gen'

// Temporary fetcher until openapi is regenerated for read endpoint
async function fetchSubscription(subId: number) {
  const res = await fetch(`${client.getConfig().baseURL}/scheduling/subscriptions/${subId}`, {
    credentials: 'include',
  })
  if (!res.ok) throw new Error('Failed to load subscription')
  return res.json()
}

export default function SubscriptionDetailPage() {
  const params = useParams()
  const id = Number(params.id)

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['subscription', id],
    queryFn: () => fetchSubscription(id),
    enabled: Number.isFinite(id),
  })

  const enable = useMutation(enableSubscriptionSchedulingSubscriptionsSubIdEnablePostMutation({ client }))
  const disable = useMutation(disableSubscriptionSchedulingSubscriptionsSubIdDisablePostMutation({ client }))
  const runNow = useMutation(runSubscriptionNowSchedulingSubscriptionsSubIdRunPostMutation({ client }))

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs text-muted-foreground"><Link to="/subscriptions" className="underline">Subscriptions</Link> / #{id}</div>
          <h1 className="text-lg font-semibold">Subscription #{id}</h1>
        </div>
        <div className="space-x-2">
          <button className="px-2 py-1 border rounded" onClick={() => enable.mutate({ path: { sub_id: id }, client }, { onSuccess: refetch })}>Enable</button>
          <button className="px-2 py-1 border rounded" onClick={() => disable.mutate({ path: { sub_id: id }, client }, { onSuccess: refetch })}>Disable</button>
          <button className="px-2 py-1 border rounded" onClick={() => runNow.mutate({ path: { sub_id: id }, client }, { onSuccess: refetch })}>Run Now</button>
        </div>
      </div>

      {isLoading && <div className="text-sm text-muted-foreground">Loading...</div>}
      {isError && <div className="text-sm text-red-500">Failed to load</div>}

      {data && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="border rounded-lg p-4">
            <div className="text-sm font-medium mb-2">Overview</div>
            <div className="text-sm">Status: <span className="font-mono text-xs">{data.status}</span></div>
            <div className="text-sm">Schedule: <span className="font-mono text-xs">{data.schedule}</span></div>
            <div className="text-xs text-muted-foreground mt-1">Last: {data.last_run_at ?? '-'}</div>
            <div className="text-xs text-muted-foreground">Next: {data.next_run_at ?? '-'}</div>
          </div>
          <div className="border rounded-lg p-4">
            <div className="text-sm font-medium mb-2">Target</div>
            <div className="text-sm">Source ID: {data.source_id}</div>
            <div className="text-sm">Jurisdiction: {data.jurisdiction}</div>
          </div>
          <div className="border rounded-lg p-4 overflow-auto">
            <div className="text-sm font-medium mb-2">Selectors</div>
            <pre className="text-xs bg-muted/40 p-2 rounded overflow-auto">{JSON.stringify(data.selectors, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  )
}


