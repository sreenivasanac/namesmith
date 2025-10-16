import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { createServerClient } from "@supabase/ssr";

export async function POST() {
  const cookieStore = await cookies();
  const response = NextResponse.json({ success: true });

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

  await supabase.auth.signOut();

  return response;
}
