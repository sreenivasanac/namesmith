import { fetchDomains } from "@/lib/api/domains";
import { DomainExplorer } from "@/features/domains/domain-explorer";
import { getTokenFromSession, requireSession } from "@/lib/auth/session.server";

export const dynamic = "force-dynamic";

export default async function DomainsPage() {
  const session = await requireSession();
  const accessToken = getTokenFromSession(session) ?? "";
  const initialData = await fetchDomains(accessToken, { limit: 50 });

  return <DomainExplorer initialData={initialData} />;
}
