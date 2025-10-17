import React, { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { getAccessToken } from '@/api/axios-base'

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
            className={connectionStatus === 'connected' ? 'bg-green-600' : ''}
          >
            {connectionStatus === 'connected' ? '● Live' : '● Disconnected'}
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
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-4 font-semibold">ID</th>
                  <th className="text-left py-2 px-4 font-semibold">Event Type</th>
                  <th className="text-left py-2 px-4 font-semibold">Status</th>
                  <th className="text-left py-2 px-4 font-semibold">Created At</th>
                  <th className="text-left py-2 px-4 font-semibold">Attempts</th>
                </tr>
              </thead>
              <tbody>
                {data.outbox.length > 0 ? (
                  data.outbox.map((entry) => (
                    <tr key={entry.id} className="border-b hover:bg-muted/50">
                      <td className="py-2 px-4">{entry.id}</td>
                      <td className="py-2 px-4 font-mono text-xs">{entry.event_type}</td>
                      <td className="py-2 px-4">
                        <Badge variant="outline" className={getStatusColor(entry.status)}>
                          {entry.status}
                        </Badge>
                      </td>
                      <td className="py-2 px-4 text-xs">
                        {new Date(entry.created_at).toLocaleString()}
                      </td>
                      <td className="py-2 px-4">{entry.attempts}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="py-4 px-4 text-center text-muted-foreground">
                      No outbox entries
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
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
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-4 font-semibold">ID</th>
                  <th className="text-left py-2 px-4 font-semibold">Run Kind</th>
                  <th className="text-left py-2 px-4 font-semibold">Status</th>
                  <th className="text-left py-2 px-4 font-semibold">Subscription ID</th>
                  <th className="text-left py-2 px-4 font-semibold">Started At</th>
                  <th className="text-left py-2 px-4 font-semibold">Ended At</th>
                </tr>
              </thead>
              <tbody>
                {data.runs.length > 0 ? (
                  data.runs.map((entry) => (
                    <tr key={entry.id} className="border-b hover:bg-muted/50">
                      <td className="py-2 px-4">{entry.id}</td>
                      <td className="py-2 px-4 font-mono text-xs">{entry.run_kind}</td>
                      <td className="py-2 px-4">
                        <Badge variant="outline" className={getStatusColor(entry.status)}>
                          {entry.status}
                        </Badge>
                      </td>
                      <td className="py-2 px-4">
                        {entry.subscription_id ? (
                          <span className="font-mono text-xs">{entry.subscription_id}</span>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </td>
                      <td className="py-2 px-4 text-xs">
                        {new Date(entry.started_at).toLocaleString()}
                      </td>
                      <td className="py-2 px-4 text-xs">
                        {entry.ended_at ? new Date(entry.ended_at).toLocaleString() : '-'}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="py-4 px-4 text-center text-muted-foreground">
                      No runs
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
