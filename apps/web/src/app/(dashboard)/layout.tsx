import { ReactNode } from "react";
import { BRAND_NAME } from "@/lib/utils";
import Link from "next/link";
import { DashboardHeader } from "@/components/layout/dashboard-header";
import { SidebarNav } from "@/components/layout/sidebar-nav";
import { AppProviders } from "@/providers/app-providers";
import { requireSession } from "@/lib/auth/session.server";

export default async function DashboardLayout({ children }: { children: ReactNode }) {
  const session = await requireSession();
  const userEmail = session.user.email ?? "user";

  return (
    <AppProviders>
      <div className="flex min-h-screen bg-background text-foreground">
        <aside className="hidden w-64 flex-col border-r bg-sidebar text-sidebar-foreground lg:flex">
          <div className="flex h-16 items-center border-b px-4 text-lg font-semibold">
            <Link href="/dashboard" className="flex items-center gap-2">
              <span className="rounded-md bg-primary px-2 py-1 text-sm font-bold text-primary-foreground">NS</span>
              <span>{BRAND_NAME}</span>
            </Link>
          </div>
          <SidebarNav />
        </aside>
        <div className="flex flex-1 flex-col">
          <DashboardHeader userEmail={userEmail} brandName={BRAND_NAME} />
          <main className="flex-1 overflow-y-auto bg-background px-4 py-6 lg:px-8">{children}</main>
        </div>
      </div>
    </AppProviders>
  );
}
