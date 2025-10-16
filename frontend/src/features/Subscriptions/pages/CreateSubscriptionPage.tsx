import { useMutation } from '@tanstack/react-query'
import { client } from '@/queries/client.gen'
import { createSubscriptionSchedulingSubscriptionsPostMutation } from '@/queries/@tanstack/react-query.gen'
import CreateSubscriptionForm from '../components/CreateSubscriptionForm'
import { Link, useNavigate } from 'react-router-dom'

export default function CreateSubscriptionPage() {
  const navigate = useNavigate()
  const createSub = useMutation(createSubscriptionSchedulingSubscriptionsPostMutation({ client }))

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs text-muted-foreground"><Link to="/subscriptions" className="underline">Subscriptions</Link> / New</div>
          <h1 className="text-lg font-semibold">Create Subscription</h1>
        </div>
      </div>

      <div className="border rounded-lg p-4">
        <CreateSubscriptionForm
          onCreate={(payload) =>
            createSub.mutate(
              { body: payload, client },
              { onSuccess: (r) => navigate(`/subscriptions/${(r as any).id ?? ''}`) }
            )
          }
        />
      </div>
    </div>
  )
}


