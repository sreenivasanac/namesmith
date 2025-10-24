import Link from "next/link";
import { Button } from "@/components/ui/button";
import { fetchJobs } from "@/lib/api/jobs";
import { JobTable } from "@/features/jobs/job-table";
import { getTokenFromSession, requireSession } from "@/lib/auth/session.server";

export const dynamic = "force-dynamic";

export default async function JobsPage() {
  const session = await requireSession();
  const token = getTokenFromSession(session);
  const initialJobs = token ? await fetchJobs(token, new URLSearchParams()) : { items: [], next_cursor: null };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Jobs</h1>
          <p className="text-sm text-muted-foreground">Manage generation jobs and monitor their progress.</p>
        </div>
        <Button asChild>
          <Link href="/dashboard/jobs/new">Create job</Link>
        </Button>
      </div>
      <JobTable initialData={initialJobs} showViewAllLink={false} />
    </div>
  );
}
