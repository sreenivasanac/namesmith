import { redirect } from "next/navigation";
import type { JobListResponse } from "@namesmith/shared-ts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { createSupabaseServerClient } from "@/lib/auth/supabase-server";
import { fetchJobs } from "@/lib/api/jobs";
import { JobTable } from "@/features/jobs/job-table";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login");
  }

  const {
    data: { session },
  } = await supabase.auth.getSession();
  const token = session?.access_token ?? null;
  const params = new URLSearchParams({ limit: "5" });
  
  let initialJobs: JobListResponse = { items: [], next_cursor: null };
  let apiError = false;
  
  try {
    if (token) {
      initialJobs = await fetchJobs(token, params);
    }
  } catch (error) {
    console.error("Failed to fetch jobs:", error);
    apiError = true;
  }

  const totalJobs = initialJobs.items.length;
  const completedJobs = initialJobs.items.filter((job) => job.status === "succeeded").length;
  const activeJobs = initialJobs.items.filter((job) => job.status === "running" || job.status === "queued" || job.status === "partial").length;

  return (
    <div className="space-y-8">
      {apiError && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-sm text-destructive">
              Unable to connect to the backend API. Please make sure the API server is running at{" "}
              <code className="rounded bg-muted px-1 py-0.5">http://localhost:8000</code>
            </p>
          </CardContent>
        </Card>
      )}
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Total jobs</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold">{totalJobs}</p>
            <p className="text-sm text-muted-foreground">Last {initialJobs.items.length} records</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Completed jobs</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold">{completedJobs}</p>
            <p className="text-sm text-muted-foreground">Succeeded within recent jobs</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Active jobs</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold">{activeJobs}</p>
            <p className="text-sm text-muted-foreground">Queued or running</p>
          </CardContent>
        </Card>
      </section>
      <JobTable initialData={initialJobs} limit={5} />
    </div>
  );
}
