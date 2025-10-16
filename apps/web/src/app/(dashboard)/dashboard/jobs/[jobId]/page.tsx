import { notFound, redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/auth/supabase-server";
import { fetchJob } from "@/lib/api/jobs";
import { fetchDomains } from "@/lib/api/domains";
import { JobDetail } from "@/features/jobs/job-detail";

interface JobDetailPageProps {
  params: Promise<{ jobId: string }>;
}

export const dynamic = "force-dynamic";

export default async function JobDetailPage({ params }: JobDetailPageProps) {
  const { jobId } = await params;
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
  const accessToken = session?.access_token;

  try {
    const [job, domains] = await Promise.all([
      fetchJob(accessToken ?? "", jobId),
      fetchDomains(accessToken ?? "", { job_id: jobId, limit: 50 }),
    ]);
    return <JobDetail job={job} initialDomains={domains} />;
  } catch (error) {
    console.error("Failed to load job", error);
    notFound();
  }
}
