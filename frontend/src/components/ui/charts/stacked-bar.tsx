import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent, type ChartConfig } from "@/components/ui/chart"

interface StackedBarData {
  date: string
  open: number
  closed: number
}

interface StackedBarProps {
  title?: string
  data: StackedBarData[]
}

export function StackedBar({ title = "", data }: StackedBarProps) {
  const chartConfig: ChartConfig = {
    closed: { label: "Closed", color: "var(--closed)" },
    open: { label: "Open", color: "var(--open)" },
  }
  
    return (
      <div>
        {title && <h3 className="mb-3 text-base font-semibold tracking-tight">{title}</h3>}
        <ChartContainer config={chartConfig} className="w-full h-[200px]">
          <BarChart accessibilityLayer data={data} barCategoryGap={6}>
            <CartesianGrid vertical={false} />
            <YAxis ticks={[0, 50, 100]} domain={[0, 100]} tickFormatter={(v) => `${v}%`} axisLine={false} tickLine={false} />
            <XAxis dataKey="date" tickLine={false} axisLine={false} tickMargin={8} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <ChartLegend content={<ChartLegendContent />} />
            <Bar dataKey="open" stackId="a" fill="var(--color-open)" radius={[0, 0, 0, 0]} />
            <Bar dataKey="closed" stackId="a" fill="var(--color-closed)" radius={[0, 0, 0, 0]} />
          </BarChart>
        </ChartContainer>
      </div>
    )
  }