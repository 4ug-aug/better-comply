import { useParams, Link } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { client } from '@/queries/client.gen'
import { getSourceSourcesSourceIdGetOptions, updateSourceSourcesSourceIdPutMutation } from '@/queries/@tanstack/react-query.gen'
import SourceForm, { type SourceFormValues } from '../components/SourceForm'

export default function SourceDetailPage() {
  const params = useParams()
  const id = Number(params.id)
  const read = useQuery(getSourceSourcesSourceIdGetOptions({ client, path: { source_id: id } }))
  const update = useMutation(updateSourceSourcesSourceIdPutMutation({ client }))

  const onSubmit = (values: SourceFormValues) => {
    update.mutate({ path: { source_id: id }, body: values, client }, { onSuccess: () => read.refetch() })
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs text-muted-foreground"><Link to="/sources" className="underline">Sources</Link> / #{id}</div>
          <h1 className="text-lg font-semibold">Source #{id}</h1>
        </div>
      </div>

      {read.isLoading && <div className="text-sm text-muted-foreground">Loading...</div>}
      {read.isError && <div className="text-sm text-red-500">Failed to load</div>}

      {read.data && (
        <div className="border rounded-lg p-4">
          <SourceForm defaultValues={read.data} onSubmit={onSubmit} submitting={update.isPending} />
        </div>
      )}
    </div>
  )
}


