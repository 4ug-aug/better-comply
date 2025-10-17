interface SubscriptionSelectorsCardProps {
  selectors: Record<string, unknown>
}

export function SubscriptionSelectorsCard({
  selectors,
}: SubscriptionSelectorsCardProps) {
  return (
    <div className="border rounded-lg p-4 overflow-auto">
      <div className="text-sm font-medium mb-2">Selectors</div>
      <pre className="text-xs bg-muted/40 p-2 rounded overflow-auto">
        {JSON.stringify(selectors, null, 2)}
      </pre>
    </div>
  )
}
