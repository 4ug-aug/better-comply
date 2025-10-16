import { useMutation, useQuery } from '@tanstack/react-query'
import { client } from '@/queries/client.gen'
import { listSourcesSourcesGetOptions, deleteSourceSourcesSourceIdDeleteMutation } from '@/queries/@tanstack/react-query.gen'
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from '@/components/ui/empty'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Link, useNavigate } from 'react-router-dom'
import { PencilIcon, PlusIcon, RefreshCwIcon, TrashIcon } from 'lucide-react'
import { GlobeIcon, MoreHorizontalIcon } from 'lucide-react'
import { Spinner } from '@/components/ui/spinner'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog'
import { useState } from 'react'

export default function SourcesPage() {
  const navigate = useNavigate()
  const [sourceToDelete, setSourceToDelete] = useState<{ id: number; name: string } | null>(null)
  
  const { data, isLoading, isError, refetch } = useQuery({
    ...listSourcesSourcesGetOptions({ client, query: { limit: 100, offset: 0 } }),
    select: (data) => data as any[]
  })

  const deleteSource = useMutation(deleteSourceSourcesSourceIdDeleteMutation({ client }))

  const handleRefresh = () => {
    refetch()
  }

  const handleDelete = (id: number) => {
    deleteSource.mutate({ path: { source_id: id }, client }, { onSuccess: () => refetch() })
    setSourceToDelete(null)
  }

  if (isLoading) {
    return <Spinner />
  }
  if (isError) {
    return <div className="text-sm text-red-500">Failed to load</div>
  }

  return (
    <div className="p-4 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            Sources
          </h1>
          <p className="text-muted-foreground">
            Manage content sources for subscriptions
          </p>
        </div>
        <div className="flex gap-2">
          <Button asChild>
            <Link to="/sources/new">
              <PlusIcon className="w-4 h-4" />
              Create source
            </Link>
          </Button>
          <Button variant="outline" size="icon" onClick={handleRefresh}>
            <RefreshCwIcon className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {data && data.length === 0 ? (
        <Empty>
          <EmptyHeader>
            <EmptyMedia variant="icon"><GlobeIcon className="w-4 h-4" /></EmptyMedia>
            <EmptyTitle>No sources configured</EmptyTitle>
            <EmptyDescription>Add a source to begin creating subscriptions.</EmptyDescription>
          </EmptyHeader>
            <Button asChild>
              <Link to="/sources/new">
                <PlusIcon className="w-4 h-4" />
                Create source
              </Link>
            </Button>
        </Empty>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Kind</TableHead>
              <TableHead>Base URL</TableHead>
              <TableHead>Enabled</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
            <TableBody>
              {data?.map((s: any) => (
                <TableRow key={s.id} onClick={() => navigate(`/sources/${s.id}`)} className="cursor-pointer hover:bg-muted/50">
                  <TableCell>{s.id}</TableCell>
                  <TableCell>{s.name}</TableCell>
                  <TableCell>{s.kind}</TableCell>
                  <TableCell className="truncate max-w-[24rem]">{s.base_url}</TableCell>
                  <TableCell>{s.enabled ? 'Yes' : 'No'}</TableCell>
                  <TableCell className="text-center w-[1rem]">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreHorizontalIcon className="w-4 h-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent>
                        <DropdownMenuItem asChild>
                          <Link to={`/sources/${s.id}`}>
                            <PencilIcon className="w-4 h-4 mr-2" />
                            Edit
                          </Link>
                        </DropdownMenuItem>
                        <DropdownMenuItem 
                          onClick={(e) => {
                            e.stopPropagation()
                            setSourceToDelete({ id: s.id, name: s.name })
                          }}
                          className="text-red-600"
                        >
                          <TrashIcon className="w-4 h-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
      )}

      <AlertDialog open={!!sourceToDelete} onOpenChange={() => setSourceToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Source</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{sourceToDelete?.name}"? This action cannot be undone.
              Any subscriptions using this source will also be affected.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => sourceToDelete && handleDelete(sourceToDelete.id)}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}


