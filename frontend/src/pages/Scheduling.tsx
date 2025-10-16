import { useSchedulingStore } from '@/store/scheduling'
import { client } from '@/queries/client.gen'
import {
  listSubscriptionsSchedulingSubscriptionsGetOptions,
  listRunsSchedulingRunsGetOptions,
  listOutboxSchedulingOutboxGetOptions,
  tickSchedulingTickPostMutation,
  computeNextSchedulingComputeNextPostMutation,
  dispatchOutboxSchedulingOutboxDispatchPostMutation,
  createSubscriptionSchedulingSubscriptionsPostMutation,
  enableSubscriptionSchedulingSubscriptionsSubIdEnablePostMutation,
  disableSubscriptionSchedulingSubscriptionsSubIdDisablePostMutation,
  runSubscriptionNowSchedulingSubscriptionsSubIdRunPostMutation,
} from '@/queries/@tanstack/react-query.gen'
import { useMutation, useQuery } from '@tanstack/react-query'

export default function Scheduling() {
  const {
    subsStatus, outboxStatus,
    subsLimit, subsOffset, runsLimit, runsOffset, outboxLimit, outboxOffset
  } = useSchedulingStore()

  const subsQuery = useQuery(listSubscriptionsSchedulingSubscriptionsGetOptions({
    client,
    query: { status: subsStatus, limit: subsLimit, offset: subsOffset },
  }))
  const runsQuery = useQuery(listRunsSchedulingRunsGetOptions({ client, query: { limit: runsLimit, offset: runsOffset } }))
  const outboxQuery = useQuery(listOutboxSchedulingOutboxGetOptions({ client, query: { status: outboxStatus, limit: outboxLimit, offset: outboxOffset } }))

  const tick = useMutation(tickSchedulingTickPostMutation({ client }))
  const computeNext = useMutation(computeNextSchedulingComputeNextPostMutation({ client }))
  const dispatchOutbox = useMutation(dispatchOutboxSchedulingOutboxDispatchPostMutation({ client }))
  const createSub = useMutation(createSubscriptionSchedulingSubscriptionsPostMutation({ client }))
  const enableSub = useMutation(enableSubscriptionSchedulingSubscriptionsSubIdEnablePostMutation({ client }))
  const disableSub = useMutation(disableSubscriptionSchedulingSubscriptionsSubIdDisablePostMutation({ client }))
  const runNow = useMutation(runSubscriptionNowSchedulingSubscriptionsSubIdRunPostMutation({ client }))

  const refresh = () => {
    subsQuery.refetch()
    runsQuery.refetch()
    outboxQuery.refetch()
  }

  return (
    <div className="p-4 space-y-6">
      <div className="flex items-center gap-2">
        <button className="px-3 py-1.5 border rounded" onClick={() => tick.mutate({ body: { batch_size: 100 }, client }, { onSuccess: refresh })}>Tick</button>
        <button className="px-3 py-1.5 border rounded" onClick={() => computeNext.mutate({ body: { batch_size: 500 }, client }, { onSuccess: refresh })}>Compute Next</button>
        <button className="px-3 py-1.5 border rounded" onClick={() => dispatchOutbox.mutate({ body: { batch_size: 200 }, client }, { onSuccess: refresh })}>Dispatch Outbox</button>
      </div>

      <div className="grid grid-cols-1 gap-6">
        <section>
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Subscriptions</h2>
            <CreateSubscriptionForm onCreate={(payload) => createSub.mutate({ body: payload, client }, { onSuccess: refresh })} />
          </div>
          <table className="w-full text-sm mt-3">
            <thead>
              <tr className="text-left">
                <th className="py-2">ID</th>
                <th>Schedule</th>
                <th>Status</th>
                <th>Last</th>
                <th>Next</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {subsQuery.data?.map((s: any) => (
                <tr key={s.id} className="border-t">
                  <td className="py-2">{s.id}</td>
                  <td>{s.schedule}</td>
                  <td>{s.status}</td>
                  <td>{s.last_run_at ?? '-'}</td>
                  <td>{s.next_run_at ?? '-'}</td>
                  <td className="space-x-2">
                    <button className="px-2 py-1 border rounded" onClick={() => enableSub.mutate({ path: { sub_id: s.id }, client }, { onSuccess: refresh })}>Enable</button>
                    <button className="px-2 py-1 border rounded" onClick={() => disableSub.mutate({ path: { sub_id: s.id }, client }, { onSuccess: refresh })}>Disable</button>
                    <button className="px-2 py-1 border rounded" onClick={() => runNow.mutate({ path: { sub_id: s.id }, client }, { onSuccess: refresh })}>Run Now</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section>
          <h2 className="text-lg font-semibold">Outbox</h2>
          <table className="w-full text-sm mt-3">
            <thead>
              <tr className="text-left">
                <th className="py-2">ID</th>
                <th>Type</th>
                <th>Status</th>
                <th>Attempts</th>
              </tr>
            </thead>
            <tbody>
              {outboxQuery.data?.map((o: any) => (
                <tr key={o.id} className="border-t">
                  <td className="py-2">{o.id}</td>
                  <td>{o.event_type}</td>
                  <td>{o.status}</td>
                  <td>{o.attempts}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section>
          <h2 className="text-lg font-semibold">Runs</h2>
          <table className="w-full text-sm mt-3">
            <thead>
              <tr className="text-left">
                <th className="py-2">ID</th>
                <th>Sub</th>
                <th>Kind</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {runsQuery.data?.map((r: any) => (
                <tr key={r.id} className="border-t">
                  <td className="py-2">{r.id}</td>
                  <td>{r.subscription_id}</td>
                  <td>{r.run_kind}</td>
                  <td>{r.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </div>
    </div>
  )
}

function CreateSubscriptionForm({ onCreate }: { onCreate: (body: any) => void }) {
  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const data = new FormData(e.currentTarget)
    const payload = {
      source_id: Number(data.get('source_id')),
      jurisdiction: String(data.get('jurisdiction')),
      schedule: String(data.get('schedule')),
      status: String(data.get('status') || 'ACTIVE'),
      selectors: JSON.parse(String(data.get('selectors') || '{}')),
    }
    onCreate(payload)
    e.currentTarget.reset()
  }
  return (
    <form onSubmit={onSubmit} className="flex items-center gap-2 text-sm">
      <input name="source_id" placeholder="source_id" className="border px-2 py-1 rounded w-24" required />
      <input name="jurisdiction" placeholder="jurisdiction" className="border px-2 py-1 rounded w-40" required />
      <input name="schedule" placeholder="cron" className="border px-2 py-1 rounded w-32" required />
      <select name="status" className="border px-2 py-1 rounded">
        <option value="ACTIVE">ACTIVE</option>
        <option value="DISABLED">DISABLED</option>
      </select>
      <input name="selectors" placeholder='{"key":"value"}' className="border px-2 py-1 rounded w-64" />
      <button type="submit" className="px-3 py-1.5 border rounded">Create</button>
    </form>
  )
}


