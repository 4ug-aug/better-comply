import { useMutation, useQueryClient } from '@tanstack/react-query'
import { client } from '@/queries/client.gen'
import { createSourceSourcesPostMutation } from '@/queries/@tanstack/react-query.gen'
import SourceForm, { type SourceFormValues } from '../components/SourceForm'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from "sonner"

export default function CreateSourcePage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const create = useMutation(createSourceSourcesPostMutation({ client }))

  const onSubmit = (values: SourceFormValues) => {
    create.mutate({ body: values, client }, { 
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['listSourcesSourcesGet'] })
        toast.success('Source created successfully')
        navigate('/sources')
      },
      onError: () => {
        toast.error('Failed to create source')
      }
    })
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs text-muted-foreground"><Link to="/sources" className="underline">Sources</Link> / New</div>
          <h1 className="text-lg font-semibold">Create Source</h1>
        </div>
      </div>
      <div className="border rounded-lg p-4">
        <SourceForm onSubmit={onSubmit} submitting={create.isPending} />
      </div>
    </div>
  )
}


