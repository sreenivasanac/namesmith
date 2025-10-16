"use client";

import { useEffect, useState } from "react";
import { createSupabaseBrowserClient } from "@/lib/auth/supabase-browser";

export function useAccessToken(): string | null {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [supabase] = useState(() => createSupabaseBrowserClient());

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setAccessToken(session?.access_token ?? null);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setAccessToken(session?.access_token ?? null);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [supabase]);

  return accessToken;
}
