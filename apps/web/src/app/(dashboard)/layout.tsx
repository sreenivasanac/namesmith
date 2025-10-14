import { redirect } from "next/navigation";
import Link from "next/link";
import { ReactNode } from "react";
import { createSupabaseServerClient } from "@/lib/auth/supabase-server";
import { BRAND_NAME } from "@/lib/utils";
import { SidebarNav } from "@/components/layout/sidebar-nav";
import { SignOutButton } from "@/features/auth/sign-out-button";

export default async function DashboardLayout({ children }: { children: ReactNode }) {
  const supabase = await createSupabaseServerClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session) {
    redirect("/login");
  }

  const userEmail = session.user.email ?? "user";

  return (
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
        <header className="flex h-16 items-center justify-between border-b px-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            Signed in as <span className="font-medium text-foreground">{userEmail}</span>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/dashboard/jobs/new" className="text-sm font-medium text-primary hover:underline">
              New job
            </Link>
            <SignOutButton />
          </div>
        </header>
        <main className="flex-1 overflow-y-auto bg-background px-4 py-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
