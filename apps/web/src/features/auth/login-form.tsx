"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createSupabaseBrowserClient } from "@/lib/auth/supabase-browser";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

const schema = z.object({
  email: z.string().email("Enter a valid email"),
});

type LoginValues = z.infer<typeof schema>;

interface LoginFormProps {
  className?: string;
}

export function LoginForm({ className }: LoginFormProps) {
  const [supabase] = useState(() => createSupabaseBrowserClient());
  const router = useRouter();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: "" },
  });
  const [loading, setLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  const onSubmit = handleSubmit(async (values) => {
    try {
      setLoading(true);
      const { error } = await supabase.auth.signInWithOtp({
        email: values.email,
        options: {
          emailRedirectTo: `${window.location.origin}/api/auth/callback`,
        },
      });
      if (error) {
        throw error;
      }
      setEmailSent(true);
      toast.success("Check your email for the login link!");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unable to send login link";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  });

  if (emailSent) {
    return (
      <div className={cn("w-full max-w-sm space-y-6 text-center", className)}>
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold">Check your email</h1>
          <p className="text-sm text-muted-foreground">
            We&apos;ve sent you a magic link to sign in. Click the link in your email to continue.
          </p>
        </div>
        <Button
          type="button"
          variant="outline"
          className="w-full"
          onClick={() => {
            setEmailSent(false);
            router.refresh();
          }}
        >
          Send another link
        </Button>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} className={cn("w-full max-w-sm space-y-6", className)}>
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-semibold">Sign in to Namesmith</h1>
        <p className="text-sm text-muted-foreground">Enter your email to receive a magic link</p>
      </div>
      <div className="space-y-4">
        <div className="space-y-2 text-left">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" autoComplete="email" placeholder="you@example.com" {...register("email")} />
          {errors.email ? <p className="text-sm text-destructive">{errors.email.message}</p> : null}
        </div>
      </div>
      <Button type="submit" className="w-full" disabled={loading}>
        {loading ? "Sending link..." : "Send magic link"}
      </Button>
    </form>
  );
}
