import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Button } from '@/components/ui/button'

const schema = z.object({
  name: z.string().min(1, 'Required'),
  kind: z.enum(['html', 'api', 'pdf']),
  base_url: z.url('Must be a valid URL'),
  auth_ref: z.string().optional().nullable(),
  robots_mode: z.enum(['allow', 'disallow', 'custom']).default('allow'),
  rate_limit: z.coerce.number().int().min(0).default(60),
  enabled: z.boolean().default(true),
})

export type SourceFormValues = z.infer<typeof schema>

export function SourceForm({ defaultValues, onSubmit, submitting }: {
  defaultValues?: Partial<SourceFormValues>
  onSubmit: (values: SourceFormValues) => void
  submitting?: boolean
}) {
  const form = useForm<SourceFormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: '',
      kind: 'html',
      base_url: '',
      auth_ref: '',
      robots_mode: 'allow',
      rate_limit: 60,
      enabled: true,
      ...defaultValues,
    },
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Name</FormLabel>
              <FormControl>
                <Input placeholder="EU Official Journal" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="kind"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Kind</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select kind" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="html">HTML</SelectItem>
                  <SelectItem value="api">API</SelectItem>
                  <SelectItem value="pdf">PDF</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="base_url"
          render={({ field }) => (
            <FormItem className="md:col-span-2">
              <FormLabel>Base URL</FormLabel>
              <FormControl>
                <Input placeholder="https://example.gov" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="auth_ref"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Auth Ref</FormLabel>
              <FormControl>
                <Input placeholder="optional auth ref" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="robots_mode"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Robots</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Robots mode" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="allow">Allow</SelectItem>
                  <SelectItem value="disallow">Disallow</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="rate_limit"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Rate limit (rpm)</FormLabel>
              <FormControl>
                <Input type="number" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="enabled"
          render={({ field }) => (
            <FormItem className="flex items-center justify-between md:col-span-2 border rounded p-3">
              <FormLabel className="m-0">Enabled</FormLabel>
              <FormControl>
                <Switch checked={field.value} onCheckedChange={field.onChange} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="md:col-span-2 flex justify-end gap-2">
          <Button type="submit" disabled={submitting}>Save</Button>
        </div>
      </form>
    </Form>
  )
}

export default SourceForm


