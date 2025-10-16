import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/auth/supabase-server";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CreateJobForm } from "@/features/jobs/job-form";

export const dynamic = "force-dynamic";

export default async function NewJobPage() {
  const supabase = await createSupabaseServerClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session) {
    redirect("/login");
  }

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
