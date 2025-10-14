"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useAccessToken } from "@/hooks/useAccessToken";
import { createJob } from "@/lib/api/jobs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

const schema = z.object({
  entry_path: z.enum(["business", "investor"]),
  prompt: z.string().min(10, "Describe your idea in at least 10 characters"),
  categories: z.string().optional(),
  tlds: z.string().optional(),
  count: z.number().min(5).max(200),
  generation_model: z.string().optional(),
  scoring_model: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

export function CreateJobForm() {
  const token = useAccessToken();
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      entry_path: "business",
      count: 20,
    },
  });

  const onSubmit = handleSubmit(async (values) => {
    if (!token) {
      toast.error("Authenticating...");
      return;
    }
    try {
      setLoading(true);
      const payload = {
        entry_path: values.entry_path,
        prompt: values.prompt,
        categories:
          values.categories?.split(",")
            .map((value: string) => value.trim())
            .filter(Boolean) ?? [],
        tlds:
          values.tlds?.split(",")
            .map((value: string) => value.trim())
            .filter(Boolean) ?? [],
        count: values.count,
        generation_model: values.generation_model?.trim() || undefined,
        scoring_model: values.scoring_model?.trim() || undefined,
      };
      const job = await createJob(token, payload);
      toast.success("Job created. Redirecting...");
      router.push(`/dashboard/jobs/${job.id}`);
      router.refresh();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to create job");
    } finally {
      setLoading(false);
    }
  });

  return (
    <form className="space-y-6" onSubmit={onSubmit}>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="entry_path">Entry path</Label>
          <select id="entry_path" className="rounded-md border border-input bg-background px-3 py-2 text-sm" {...register("entry_path")}>
            <option value="business">Business</option>
            <option value="investor">Investor</option>
          </select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="count">Number of candidates</Label>
          <Input id="count" type="number" min={5} max={200} {...register("count", { valueAsNumber: true })} />
          {errors.count ? <p className="text-sm text-destructive">{errors.count.message}</p> : null}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="prompt">Business prompt</Label>
        <Textarea id="prompt" rows={5} placeholder="Describe the product, tone, keywords..." {...register("prompt")} />
        {errors.prompt ? <p className="text-sm text-destructive">{errors.prompt.message}</p> : null}
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="categories">Categories (comma separated)</Label>
          <Input id="categories" placeholder="SaaS, AI" {...register("categories")} />
        </div>
        <div className="space-y-2">
          <Label htmlFor="tlds">TLDs (comma separated)</Label>
          <Input id="tlds" placeholder="com, ai" {...register("tlds")} />
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="generation_model">Generation model</Label>
          <Input id="generation_model" placeholder="e.g. gpt-4o-mini" {...register("generation_model")} />
        </div>
        <div className="space-y-2">
          <Label htmlFor="scoring_model">Scoring model</Label>
          <Input id="scoring_model" placeholder="e.g. gpt-4o-mini" {...register("scoring_model")} />
        </div>
      </div>

      <div className="flex justify-end gap-2">
        <Button type="submit" disabled={loading || !token}>
          {loading ? "Submitting..." : "Create job"}
        </Button>
      </div>
    </form>
  );
}
