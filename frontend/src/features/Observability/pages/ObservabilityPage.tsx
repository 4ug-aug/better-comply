import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { getAccessToken } from '@/api/axios-base'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

interface OutboxEntry {
  id: number
  status: string
  event_type: string
  created_at: string
  attempts: number
  published_at?: string
}

interface RunEntry {
  id: number
  status: string
  run_kind: string
  subscription_id?: number
  started_at: string
  ended_at?: string
}

interface ObservabilityData {
  outbox: OutboxEntry[]
  runs: RunEntry[]
  error?: string
}

const statusColorMap: Record<string, string> = {
  PENDING: 'bg-yellow-100 text-yellow-800',
  RUNNING: 'bg-blue-100 text-blue-800',
  PUBLISHED: 'bg-green-100 text-green-800',
  COMPLETED: 'bg-green-100 text-green-800',
  FAILED: 'bg-red-100 text-red-800',
  CANCELLED: 'bg-gray-100 text-gray-800',
}

const getStatusColor = (status: string): string => {
  return statusColorMap[status] || 'bg-gray-100 text-gray-800'
}

export default function ObservabilityPage() {
  const [data, setData] = useState<ObservabilityData>({
    outbox: [],
    runs: [],
  })
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting')

  useEffect(() => {
    const token = getAccessToken()
    if (!token) {
      setConnectionStatus('disconnected')
      console.error('No access token available')
      return
    }

    const apiUrl = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/observability/stream?token=${encodeURIComponent(token)}`

    const eventSource = new EventSource(apiUrl)

    eventSource.onopen = () => {
      setConnectionStatus('connected')
    }

    eventSource.onmessage = (event) => {
      try {
        const newData: ObservabilityData = JSON.parse(event.data)
        setData(newData)
      } catch (error) {
        console.error('Failed to parse SSE data:', error)
      }
    }

    eventSource.onerror = (error) => {
      console.error('EventSource error:', error)
      setConnectionStatus('disconnected')
      eventSource.close()
    }

    return () => {
      eventSource.close()
    }
  }, [])

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Observability</h1>
          <p className="text-muted-foreground mt-1">Live dashboard for outbox and runs</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Status:</span>
          <Badge
            variant={connectionStatus === 'connected' ? 'default' : 'destructive'}
          >
            {connectionStatus === 'connected' ? 'Live' : 'Disconnected'}
          </Badge>
        </div>
      </div>

      {/* Outbox Section */}
      <Card>
        <CardHeader>
          <CardTitle>Outbox</CardTitle>
          <CardDescription>Recent outbox entries</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Event Type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Created At</TableHead>
                  <TableHead>Attempts</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.outbox.length > 0 ? (
                  data.outbox.map((entry) => (
                    <TableRow key={entry.id}>
                      <TableCell>{entry.id}</TableCell>
                      <TableCell>{entry.event_type}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className={getStatusColor(entry.status)}>
                          {entry.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{new Date(entry.created_at).toLocaleString()}</TableCell>
                      <TableCell>{entry.attempts}</TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell className="text-center text-muted-foreground">
                      No outbox entries
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Runs Section */}
      <Card>
        <CardHeader>
          <CardTitle>Runs</CardTitle>
          <CardDescription>Recent execution runs</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Run Kind</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Subscription ID</TableHead>
                  <TableHead>Started At</TableHead>
                  <TableHead>Ended At</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.runs.length > 0 ? (
                  data.runs.map((entry) => (
                    <TableRow key={entry.id}>
                      <TableCell>{entry.id}</TableCell>
                      <TableCell>{entry.run_kind}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className={getStatusColor(entry.status)}>
                          {entry.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{entry.subscription_id}</TableCell>
                      <TableCell>{new Date(entry.started_at).toLocaleString()}</TableCell>
                      <TableCell>{entry.ended_at ? new Date(entry.ended_at).toLocaleString() : '-'}</TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell className="text-center text-muted-foreground">
                      No runs
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

    </div>
  )
}
