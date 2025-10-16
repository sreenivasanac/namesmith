import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { createServerClient } from "@supabase/ssr";

export async function GET(request: Request) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get("code");

  if (code) {
    const cookieStore = await cookies();
    const response = NextResponse.redirect(new URL("/dashboard", request.url));
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          async getAll() {
            return cookieStore.getAll().map(({ name, value }) => ({ name, value }));
          },
          async setAll(cookiesToSet) {
            for (const { name, value, options } of cookiesToSet) {
              if (!value) {
                response.cookies.delete(name, options);
              } else {
                response.cookies.set(name, value, options);
              }
            }
          },
        },
      }
    );

    await supabase.auth.exchangeCodeForSession(code);

    return response;
  }

  return NextResponse.redirect(new URL("/login", request.url));
}
