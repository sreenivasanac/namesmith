import { NextResponse } from "next/server";
import { z } from "zod";

import { SESSION_COOKIE_NAME } from "@/lib/auth/constants";
import { createSessionToken, getSessionCookieOptions } from "@/lib/auth/session.server";
import { buildApiUrl } from "@/lib/utils";

const loginSchema = z.object({
  email: z.string().email(),
});

export async function POST(request: Request) {
  const payload = await request.json().catch(() => null);
  const result = loginSchema.safeParse(payload ?? {});

  if (!result.success) {
    return NextResponse.json({ error: "Invalid email address" }, { status: 400 });
  }

  const email = result.data.email.toLowerCase();

  try {
    const apiResponse = await fetch(buildApiUrl("/v1/auth/login"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email }),
    });

    if (!apiResponse.ok) {
      const message = await apiResponse.text();
      return NextResponse.json({ error: message || "Login failed" }, { status: apiResponse.status });
    }

    const data = await apiResponse.json();
    const user = data?.user ?? data;
    const userId: string | undefined = user?.id;
    const userEmail: string = (user?.email ?? email).toLowerCase();

    if (!userId) {
      return NextResponse.json({ error: "Login response missing user id" }, { status: 502 });
    }

    const token = createSessionToken({
      userId,
      email: userEmail,
      issuedAt: Date.now(),
    });

    const response = NextResponse.json({ user: { id: userId, email: userEmail } });
    response.cookies.set({
      ...getSessionCookieOptions(),
      name: SESSION_COOKIE_NAME,
      value: token,
    });
    return response;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Login failed";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
