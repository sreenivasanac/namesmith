"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { FilePlus, Globe2, LayoutDashboard, Workflow } from "lucide-react";
import { cn } from "@/lib/utils";
import { SheetClose } from "@/components/ui/sheet";

interface SidebarNavProps {
  useSheetClose?: boolean;
}

interface SidebarItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

const navItems: SidebarItem[] = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/jobs", label: "Jobs", icon: Workflow },
  { href: "/dashboard/domains", label: "Domains", icon: Globe2 },
];

export function SidebarNav({ useSheetClose = false }: SidebarNavProps = {}) {
  const pathname = usePathname();
  const baseLinkClasses = "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors";
  const activeClasses = "bg-sidebar-primary text-sidebar-primary-foreground";
  const inactiveClasses = "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground";

  return (
    <nav className="flex flex-1 flex-col gap-4 p-4">
      <div className="flex flex-col gap-1">
        {navItems.map((item) => {
          const active = pathname.startsWith(item.href);
          const Icon = item.icon;
          const link = (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                baseLinkClasses,
                active ? activeClasses : inactiveClasses
              )}
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </Link>
          );

          return useSheetClose ? (
            <SheetClose key={item.href} asChild>
              {link}
            </SheetClose>
          ) : (
            link
          );
        })}
      </div>
      <div className="mt-2">
        {useSheetClose ? (
          <SheetClose asChild>
            <Link
              href="/dashboard/jobs/new"
              className={cn(
                baseLinkClasses,
                pathname.startsWith("/dashboard/jobs/new")
                  ? activeClasses
                  : inactiveClasses
              )}
            >
              <FilePlus className="h-4 w-4" />
              <span>Create a job</span>
            </Link>
          </SheetClose>
        ) : (
          <Link
            href="/dashboard/jobs/new"
            className={cn(
              baseLinkClasses,
              pathname.startsWith("/dashboard/jobs/new")
                ? activeClasses
                : inactiveClasses
            )}
          >
            <FilePlus className="h-4 w-4" />
            <span>Create a job</span>
          </Link>
        )}
      </div>
    </nav>
  );
}
