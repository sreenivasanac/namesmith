"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { createSupabaseBrowserClient } from "@/lib/auth/supabase-browser";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export function SignOutButton() {
  const [supabase] = useState(() => createSupabaseBrowserClient());
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleSignOut = async () => {
    try {
      setLoading(true);
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
      toast.success("Signed out");
      router.push("/login");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Unable to sign out");
    } finally {
      setLoading(false);
      router.refresh();
    }
  };

  return (
    <Button variant="outline" size="sm" onClick={handleSignOut} disabled={loading}>
      {loading ? "Signing out..." : "Sign out"}
    </Button>
  );
}
