import { redirect } from "next/navigation";
import { getSessionFromRequest } from "@/lib/auth/session.server";

export default async function Home() {
  const session = await getSessionFromRequest();
  redirect(session ? "/dashboard" : "/login");
}
