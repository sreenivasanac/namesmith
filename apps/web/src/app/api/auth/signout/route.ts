import { NextResponse } from "next/server";

import { SESSION_COOKIE_NAME } from "@/lib/auth/constants";
import { getSessionCookieOptions } from "@/lib/auth/session.server";

export async function POST() {
  const response = NextResponse.json({ success: true });
  const options = getSessionCookieOptions();
  response.cookies.set({
    ...options,
    name: SESSION_COOKIE_NAME,
    value: "",
    maxAge: 0,
  });
  return response;
}
