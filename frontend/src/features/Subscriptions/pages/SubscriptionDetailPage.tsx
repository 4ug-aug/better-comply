import { useParams, Link, useNavigate } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { client } from '@/queries/client.gen'
import {
  enableSubscriptionSchedulingSubscriptionsSubIdEnablePostMutation,
  disableSubscriptionSchedulingSubscriptionsSubIdDisablePostMutation,
  runSubscriptionNowSchedulingSubscriptionsSubIdRunPostMutation,
  readSubscriptionSchedulingSubscriptionsSubIdGetOptions,
  deleteSubscriptionSchedulingSubscriptionsSubIdDeleteMutation,
  updateSubscriptionSchedulingSubscriptionsSubIdPutMutation,
} from '@/queries/@tanstack/react-query.gen'
import { SubscriptionOverviewCard } from '../components/SubscriptionOverviewCard'
import { SubscriptionTargetCard } from '../components/SubscriptionTargetCard'
import { SubscriptionSelectorsCard } from '../components/SubscriptionSelectorsCard'
import SubscriptionForm from '../components/CreateSubscriptionForm'
import { Button } from '@/components/ui/button'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { toast } from 'sonner'
import { useState } from 'react'
import { BanIcon, CheckIcon, PencilIcon, PlayIcon, TrashIcon, XIcon } from 'lucide-react'
export default function SubscriptionDetailPage() {
  const params = useParams()
  const navigate = useNavigate()
  const id = Number(params.id)
  const [isEditing, setIsEditing] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

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

  const deleteSubscription = useMutation(
    deleteSubscriptionSchedulingSubscriptionsSubIdDeleteMutation({ client })
  )

  const updateSubscription = useMutation(
    updateSubscriptionSchedulingSubscriptionsSubIdPutMutation({ client })
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

  const handleUpdateSubscription = (payload: any) => {
    updateSubscription.mutate({ path: { sub_id: id }, body: payload, client }, {
      onSuccess: () => {
        toast.success('Subscription updated')
        setIsEditing(false)
        refetch()
      },
      onError: () => {
        toast.error('Failed to update subscription')
      },
    })
  }

  const handleDeleteSubscription = () => {
    deleteSubscription.mutate({ path: { sub_id: id }, client }, {
      onSuccess: () => {
        toast.success('Subscription deleted')
        navigate('/subscriptions')
      },
      onError: () => {
        toast.error('Failed to delete subscription')
        setShowDeleteDialog(false)
      },
    })
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
        <div>
          <div className="space-x-2">
            {!isEditing && (
              <>
                <Button variant="outline" onClick={() => setIsEditing(true)}> <PencilIcon className="w-4 h-4" /> Edit</Button>
                {data?.status === 'ACTIVE' ? (
                  <Button variant="outline" onClick={handleDisable}> <BanIcon className="w-4 h-4" /> Disable</Button>
                ) : (
                  <Button variant="outline" onClick={handleEnable}> <CheckIcon className="w-4 h-4" /> Enable</Button>
                )}
                <Button variant="default" onClick={handleRunNow}> <PlayIcon className="w-4 h-4" /> Run Now</Button>
                <Button 
                  variant="destructive" 
                  size="icon"
                  onClick={() => setShowDeleteDialog(true)}
                >
                  <TrashIcon className="w-4 h-4" />
                </Button>
              </>
            )}
            {isEditing && (
              <Button variant="outline" onClick={() => setIsEditing(false)}> <XIcon className="w-4 h-4" /> Cancel</Button>
            )}
           </div>
        </div>
      </div>

      {isLoading && (
        <div className="text-sm text-muted-foreground">Loading...</div>
      )}
      {isError && <div className="text-sm text-red-500">Failed to load</div>}

      {data && (
        isEditing ? (
          <div className="border rounded-lg p-4">
            <h2 className="text-sm font-semibold mb-4">Edit Subscription</h2>
            <SubscriptionForm
              defaultValues={{
                source_id: data.source_id,
                jurisdiction: data.jurisdiction,
                schedule: data.schedule,
                status: data.status as 'ACTIVE' | 'DISABLED',
                selectors: typeof data.selectors === 'string' ? data.selectors : JSON.stringify(data.selectors),
              }}
              onSubmit={handleUpdateSubscription}
              submitting={updateSubscription.isPending}
              buttonText="Update Subscription"
              isEditing={true}
            />
          </div>
        ) : (
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
        )
      )}

      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Subscription</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this subscription? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction 
              onClick={handleDeleteSubscription}
              disabled={deleteSubscription.isPending}
              className="bg-destructive text-white hover:bg-destructive/90"
            >
              {deleteSubscription.isPending ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}


