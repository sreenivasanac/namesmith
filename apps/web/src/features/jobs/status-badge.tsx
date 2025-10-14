import { Badge } from "@/components/ui/badge";
import type { JobStatus } from "@namesmith/shared-ts";

const statusConfig: Record<JobStatus, { label: string; variant: "default" | "secondary" | "outline" | "destructive" }> = {
  queued: { label: "Queued", variant: "secondary" },
  running: { label: "Running", variant: "default" },
  succeeded: { label: "Succeeded", variant: "default" },
  failed: { label: "Failed", variant: "destructive" },
  partial: { label: "Partial", variant: "outline" },
};

export function JobStatusBadge({ status }: { status: JobStatus }) {
  const { label, variant } = statusConfig[status];
  return <Badge variant={variant}>{label}</Badge>;
}
