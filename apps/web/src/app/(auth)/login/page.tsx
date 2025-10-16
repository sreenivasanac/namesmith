import { redirect } from "next/navigation";
import { LoginForm } from "@/features/auth/login-form";
import { createSupabaseServerClient } from "@/lib/auth/supabase-server";
import { BRAND_NAME } from "@/lib/utils";

export const metadata = {
  title: `${BRAND_NAME} – Sign in`,
};

export default async function LoginPage() {
  const supabase = await createSupabaseServerClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (session) {
    redirect("/dashboard");
  }

  return (
    <div className="w-full max-w-md rounded-xl border bg-card p-8 shadow">
      <LoginForm />
    </div>
  );
}
