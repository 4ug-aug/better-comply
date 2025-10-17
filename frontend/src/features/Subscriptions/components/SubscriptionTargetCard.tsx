interface SubscriptionTargetCardProps {
  sourceId: number
  jurisdiction: string
}

export function SubscriptionTargetCard({
  sourceId,
  jurisdiction,
}: SubscriptionTargetCardProps) {
  return (
    <div className="border rounded-lg p-4">
      <div className="text-sm font-medium mb-2">Target</div>
      <div className="text-sm">Source ID: {sourceId}</div>
      <div className="text-sm">Jurisdiction: {jurisdiction}</div>
    </div>
  )
}
