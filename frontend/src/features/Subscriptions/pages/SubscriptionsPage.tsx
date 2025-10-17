import { useQuery } from '@tanstack/react-query'
import { client } from '@/queries/client.gen'
import { listSubscriptionsSchedulingSubscriptionsGetOptions } from '@/queries/@tanstack/react-query.gen'
import SubscriptionCard from '../components/SubscriptionCard'
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from '@/components/ui/empty'
import { Button } from '@/components/ui/button'
import { Link } from 'react-router-dom'
import { ListChecksIcon, PlusIcon } from 'lucide-react'

export default function SubscriptionsPage() {
  const listQuery = useQuery(listSubscriptionsSchedulingSubscriptionsGetOptions({ client, query: { limit: 100, offset: 0 } }))
  return (
    <div className="p-4 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            Subscriptions
          </h1>
          <p className="text-muted-foreground">
            Manage subscriptions for content extraction
          </p>
        </div>
        <div className="flex gap-2">
          <Button asChild>
            <Link to="/subscriptions/new">
              <PlusIcon className="w-4 h-4" />
              Create subscription
            </Link>
          </Button>
        </div>
      </div>

      {listQuery.isLoading && <div className="text-sm text-muted-foreground">Loading...</div>}
      {listQuery.isError && <div className="text-sm text-red-500">Failed to load</div>}

      {listQuery.data && listQuery.data.length === 0 ? (
        <Empty>
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <ListChecksIcon className="w-4 h-4" />
            </EmptyMedia>
            <EmptyTitle>No subscriptions yet</EmptyTitle>
            <EmptyDescription>
              Create your first subscription to start scheduling. Use a cron like <code>0 9 * * 1</code>.
            </EmptyDescription>
          </EmptyHeader>
            <Button asChild>
              <Link to="/subscriptions/new">
                <PlusIcon className="w-4 h-4" />
                Create subscription
              </Link>
            </Button>

        </Empty>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {listQuery.data?.map((s: any) => (
            <SubscriptionCard key={s.id} sub={s} />
          ))}
        </div>
      )}
    </div>
  )
}


