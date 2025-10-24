import { notFound } from "next/navigation";
import { fetchJob } from "@/lib/api/jobs";
import { fetchDomains } from "@/lib/api/domains";
import { JobDetail } from "@/features/jobs/job-detail";
import { getTokenFromSession, requireSession } from "@/lib/auth/session.server";

interface JobDetailPageProps {
  params: Promise<{ jobId: string }>;
}

export const dynamic = "force-dynamic";

export default async function JobDetailPage({ params }: JobDetailPageProps) {
  const { jobId } = await params;
  const session = await requireSession();
  const accessToken = getTokenFromSession(session);

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
