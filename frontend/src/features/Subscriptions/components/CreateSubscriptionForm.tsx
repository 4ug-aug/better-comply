import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { useQuery } from '@tanstack/react-query'
import { client } from '@/queries/client.gen'
import { listSourcesSourcesGetOptions } from '@/queries/@tanstack/react-query.gen'

const schema = z.object({
  source_id: z.coerce.number().int().min(1, 'Please select a source'),
  jurisdiction: z.string().min(1, 'Jurisdiction is required'),
  schedule: z.string().min(1, 'Schedule is required'),
  status: z.enum(['ACTIVE', 'DISABLED']).default('ACTIVE'),
  selectors: z.string().optional(),
})

export type CreateSubscriptionValues = z.infer<typeof schema>

export function CreateSubscriptionForm({ onCreate }: { onCreate: (body: any) => void }) {
  const { data: sources, isLoading: sourcesLoading } = useQuery(listSourcesSourcesGetOptions({ client, query: { limit: 100, offset: 0 } }))
  
  const form = useForm<CreateSubscriptionValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      source_id: 0,
      jurisdiction: '',
      schedule: '',
      status: 'ACTIVE',
      selectors: '',
    },
  })

  const onSubmit = (values: CreateSubscriptionValues) => {
    let parsedSelectors: Record<string, unknown> = {}
    if (values.selectors?.trim()) {
      try {
        parsedSelectors = JSON.parse(values.selectors)
      } catch {
        // fallback to empty object
      }
    }
    onCreate({
      source_id: values.source_id,
      jurisdiction: values.jurisdiction,
      schedule: values.schedule,
      status: values.status,
      selectors: parsedSelectors,
    })
    form.reset()
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField
          control={form.control}
          name="source_id"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Source</FormLabel>
              <Select onValueChange={(value) => field.onChange(Number(value))} value={field.value?.toString()} defaultValue={field.value?.toString()}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder={sourcesLoading ? "Loading sources..." : "Select a source"} />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {sources?.map((source: any) => (
                    <SelectItem key={source.id} value={source.id.toString()}>
                      {source.name} ({source.kind})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="jurisdiction"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Jurisdiction</FormLabel>
              <FormControl>
                <Input placeholder="e.g., EU, US, UK" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="schedule"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Schedule (Cron)</FormLabel>
              <FormControl>
                <Input placeholder="0 9 * * 1" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="status"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Status</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select status" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="ACTIVE">Active</SelectItem>
                  <SelectItem value="DISABLED">Disabled</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="selectors"
          render={({ field }) => (
            <FormItem className="md:col-span-2">
              <FormLabel>Selectors (JSON)</FormLabel>
              <FormControl>
                <Input placeholder='{"key": "value"}' {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="md:col-span-2 flex justify-end gap-2">
          <Button type="submit">Create Subscription</Button>
        </div>
      </form>
    </Form>
  )
}

export default CreateSubscriptionForm


