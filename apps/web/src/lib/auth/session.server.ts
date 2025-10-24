import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { SESSION_COOKIE_NAME, SESSION_MAX_AGE_SECONDS } from "@/lib/auth/constants";

export interface SessionPayload {
  userId: string;
  email: string;
  issuedAt: number;
}

export interface SessionData {
  token: string;
  user: {
    id: string;
    email: string;
  };
}

export function createSessionToken(payload: SessionPayload): string {
  const normalized: SessionPayload = {
    userId: payload.userId,
    email: payload.email.toLowerCase(),
    issuedAt: payload.issuedAt,
  };
  const json = JSON.stringify(normalized);
  return Buffer.from(json, "utf8").toString("base64url");
}

export function parseSessionToken(token: string): SessionPayload | null {
  try {
    const json = Buffer.from(token, "base64url").toString("utf8");
    const data = JSON.parse(json) as Partial<SessionPayload>;
    if (typeof data.userId !== "string" || typeof data.email !== "string" || typeof data.issuedAt !== "number") {
      return null;
    }
    return {
      userId: data.userId,
      email: data.email.toLowerCase(),
      issuedAt: data.issuedAt,
    };
  } catch {
    return null;
  }
}

function parseSessionCookie(value: string | undefined): SessionData | null {
  if (!value) {
    return null;
  }
  const payload = parseSessionToken(value);
  if (!payload) {
    return null;
  }
  return {
    token: value,
    user: {
      id: payload.userId,
      email: payload.email,
    },
  };
}

export async function getSessionFromRequest(): Promise<SessionData | null> {
  const store = await cookies();
  const cookie = store.get(SESSION_COOKIE_NAME)?.value;
  return parseSessionCookie(cookie);
}

export async function requireSession(redirectTo = "/login"): Promise<SessionData> {
  const session = await getSessionFromRequest();
  if (!session) {
    redirect(redirectTo);
  }
  return session;
}

export async function redirectIfAuthenticated(path: string) {
  const session = await getSessionFromRequest();
  if (session) {
    redirect(path);
  }
}

export function getTokenFromSession(session: SessionData | null): string | null {
  return session ? session.token : null;
}

export function getSessionCookieOptions() {
  return {
    name: SESSION_COOKIE_NAME,
    maxAge: SESSION_MAX_AGE_SECONDS,
    path: "/",
    sameSite: "lax" as const,
    secure: process.env.NODE_ENV === "production",
    httpOnly: false,
  };
}
