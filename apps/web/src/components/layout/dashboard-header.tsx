"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { SidebarNav } from "@/components/layout/sidebar-nav";
import { SignOutButton } from "@/features/auth/sign-out-button";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Sheet, SheetClose, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { ChevronDown, Menu, PlusCircle, User } from "lucide-react";

interface DashboardHeaderProps {
  userEmail: string;
  brandName: string;
}

export function DashboardHeader({ userEmail, brandName }: DashboardHeaderProps) {
  const [profileOpen, setProfileOpen] = useState(false);
  const closeTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const openProfile = () => {
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current);
      closeTimeoutRef.current = null;
    }
    setProfileOpen(true);
  };

  const closeProfileWithDelay = () => {
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current);
    }
    closeTimeoutRef.current = setTimeout(() => setProfileOpen(false), 100);
  };

  useEffect(() => {
    return () => {
      if (closeTimeoutRef.current) {
        clearTimeout(closeTimeoutRef.current);
      }
    };
  }, []);

  return (
    <header className="flex h-16 items-center justify-between border-b px-4">
      <div className="flex items-center gap-3">
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" className="lg:hidden">
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent className="left-0 right-auto w-64 border-r p-0">
            <div className="flex h-16 items-center border-b px-4 text-lg font-semibold">
              <SheetClose asChild>
                <Link href="/dashboard" className="flex items-center gap-2">
                  <span className="rounded-md bg-primary px-2 py-1 text-sm font-bold text-primary-foreground">NS</span>
                  <span>{brandName}</span>
                </Link>
              </SheetClose>
            </div>
            <SidebarNav useSheetClose />
          </SheetContent>
        </Sheet>
        <Link href="/dashboard" className="flex items-center gap-2 text-lg font-semibold">
          <span className="rounded-md bg-primary px-2 py-1 text-sm font-bold text-primary-foreground">NS</span>
          <span className="flex items-center gap-1">
            {brandName}
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          </span>
        </Link>
      </div>
      <div className="flex items-center gap-3">
        <Button asChild size="sm" className="gap-2">
          <Link href="/dashboard/jobs/new">
            <PlusCircle className="h-4 w-4" />
            Create a job
          </Link>
        </Button>
        <Popover open={profileOpen} onOpenChange={setProfileOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="rounded-full border"
              onMouseEnter={openProfile}
              onFocus={openProfile}
              onMouseLeave={closeProfileWithDelay}
              onBlur={closeProfileWithDelay}
            >
              <User className="h-4 w-4" />
            </Button>
          </PopoverTrigger>
          <PopoverContent
            align="end"
            className="w-60 space-y-4"
            onMouseEnter={openProfile}
            onMouseLeave={closeProfileWithDelay}
          >
            <div className="space-y-1 text-sm">
              <p className="text-xs uppercase text-muted-foreground">Signed in as</p>
              <p className="break-all font-medium">{userEmail}</p>
            </div>
            <SignOutButton />
          </PopoverContent>
        </Popover>
      </div>
    </header>
  );
}
