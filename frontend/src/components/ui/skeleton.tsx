import { cn } from "@/lib/utils"

// =============================================================================
// Skeleton Component
// Loading placeholder for content that is being fetched
// =============================================================================

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-muted", className)}
      {...props}
    />
  )
}

export { Skeleton }
