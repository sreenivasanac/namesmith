"use client";

import { useEffect, useState } from "react";

import { SESSION_COOKIE_NAME } from "@/lib/auth/constants";

function readSessionToken(): string | null {
  if (typeof document === "undefined") {
    return null;
  }
  const prefix = `${SESSION_COOKIE_NAME}=`;
  const entry = document.cookie
    .split("; ")
    .find((cookie) => cookie.startsWith(prefix));
  if (!entry) {
    return null;
  }
  const token = entry.slice(prefix.length);
  return token || null;
}

export function useAccessToken(): string | null {
  const [token, setToken] = useState<string | null>(() => readSessionToken());

  useEffect(() => {
    const updateToken = () => {
      setToken(readSessionToken());
    };

    updateToken();

    window.addEventListener("focus", updateToken);
    document.addEventListener("visibilitychange", updateToken);

    return () => {
      window.removeEventListener("focus", updateToken);
      document.removeEventListener("visibilitychange", updateToken);
    };
  }, []);

  return token;
}
