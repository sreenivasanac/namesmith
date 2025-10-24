import { LoginForm } from "@/features/auth/login-form";
import { BRAND_NAME } from "@/lib/utils";
import { redirectIfAuthenticated } from "@/lib/auth/session.server";

export const metadata = {
  title: `${BRAND_NAME} – Sign in`,
};

export default async function LoginPage() {
  await redirectIfAuthenticated("/dashboard");

  return (
    <div className="w-full max-w-md rounded-xl border bg-card p-8 shadow">
      <LoginForm />
    </div>
  );
}
