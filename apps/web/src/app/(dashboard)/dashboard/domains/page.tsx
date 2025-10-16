import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/auth/supabase-server";
import { fetchDomains } from "@/lib/api/domains";
import { DomainExplorer } from "@/features/domains/domain-explorer";

export const dynamic = "force-dynamic";

export default async function DomainsPage() {
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
  const accessToken = session?.access_token ?? "";
  const initialData = await fetchDomains(accessToken, { limit: 50 });

  return <DomainExplorer initialData={initialData} />;
}
