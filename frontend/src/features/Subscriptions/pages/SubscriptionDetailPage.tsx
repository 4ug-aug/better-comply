import { useParams, Link } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { client } from '@/queries/client.gen'
import {
  enableSubscriptionSchedulingSubscriptionsSubIdEnablePostMutation,
  disableSubscriptionSchedulingSubscriptionsSubIdDisablePostMutation,
  runSubscriptionNowSchedulingSubscriptionsSubIdRunPostMutation,
  readSubscriptionSchedulingSubscriptionsSubIdGetOptions,
} from '@/queries/@tanstack/react-query.gen'
import { SubscriptionOverviewCard } from '../components/SubscriptionOverviewCard'
import { SubscriptionTargetCard } from '../components/SubscriptionTargetCard'
import { SubscriptionSelectorsCard } from '../components/SubscriptionSelectorsCard'
import { Button } from '@/components/ui/button'
import { toast } from 'sonner'

export default function SubscriptionDetailPage() {
  const params = useParams()
  const id = Number(params.id)

  const { data, isLoading, isError, refetch } = useQuery(
    readSubscriptionSchedulingSubscriptionsSubIdGetOptions({
      client,
      path: { sub_id: id },
    })
  )

  const enable = useMutation(
    enableSubscriptionSchedulingSubscriptionsSubIdEnablePostMutation({ client })
  )
  const disable = useMutation(
    disableSubscriptionSchedulingSubscriptionsSubIdDisablePostMutation({
      client,
    })
  )
  const runNow = useMutation(
    runSubscriptionNowSchedulingSubscriptionsSubIdRunPostMutation({ client }),
  )

  const handleDisable = () => {
    try {
      disable.mutate({ path: { sub_id: id }, body: { status: 'DISABLED' } as any, client }, { onSuccess: () => {
        toast.success('Subscription disabled')
        refetch()
      } })
    } catch (error) {
      toast.error('Failed to disable subscription')
    }
  }

  const handleEnable = () => {
    try {
      enable.mutate({ path: { sub_id: id }, body: { status: 'ACTIVE' } as any, client }, { onSuccess: () => {
        toast.success('Subscription enabled')
        refetch()
      } })
    } catch (error) {
      toast.error('Failed to enable subscription')
    }
  }

  const handleRunNow = () => {
    try {
      runNow.mutate({ path: { sub_id: id }, client }, { onSuccess: () => {
      toast.success('Subscription run now')
      refetch()
      }, onError: () => {
        toast.error('Failed to run subscription now')
      } })
    } catch (error) {
      toast.error('Failed to run subscription now')
    }
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs text-muted-foreground">
            <Link to="/subscriptions" className="underline">
              Subscriptions
            </Link>
            {' '}/ #{id}
          </div>
          <h1 className="text-lg font-semibold">Subscription #{id}</h1>
        </div>
        <div className="space-x-2">
          {data?.status === 'ACTIVE' ? (
            <Button variant="outline" onClick={handleDisable}>Disable</Button>
          ) : (
            <Button variant="outline" onClick={handleEnable}>Enable</Button>
          )}
          <Button variant="default" onClick={handleRunNow}>Run Now</Button>
        </div>
      </div>

      {isLoading && (
        <div className="text-sm text-muted-foreground">Loading...</div>
      )}
      {isError && <div className="text-sm text-red-500">Failed to load</div>}

      {data && (
        <div className="space-y-4">
          <SubscriptionOverviewCard
            status={data.status}
            schedule={data.schedule}
            lastRunAt={data.last_run_at ?? null}
            nextRunAt={data.next_run_at ?? null}
          />
          <SubscriptionTargetCard
            sourceId={data.source_id}
            jurisdiction={data.jurisdiction}
          />
          <SubscriptionSelectorsCard selectors={data.selectors} />
        </div>
      )}
    </div>
  )
}


