import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/auth/supabase-server";
import { fetchDomains } from "@/lib/api/domains";
import { DomainExplorer } from "@/features/domains/domain-explorer";

export const dynamic = "force-dynamic";

export default async function DomainsPage() {
  const supabase = await createSupabaseServerClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session) {
    redirect("/login");
  }

  const initialData = await fetchDomains(session.access_token, { limit: 50 });

  return <DomainExplorer initialData={initialData} />;
}
