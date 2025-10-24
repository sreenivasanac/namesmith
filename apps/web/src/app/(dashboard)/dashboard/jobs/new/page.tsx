import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CreateJobForm } from "@/features/jobs/job-form";
import { requireSession } from "@/lib/auth/session.server";

export const dynamic = "force-dynamic";

export default async function NewJobPage() {
  await requireSession();

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Create generation job</CardTitle>
        </CardHeader>
        <CardContent>
          <CreateJobForm />
        </CardContent>
      </Card>
    </div>
  );
}
