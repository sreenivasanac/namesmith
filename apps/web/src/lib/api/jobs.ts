import type { Job, JobCreateRequest, JobListResponse } from "@namesmith/shared-ts";
import { apiFetch } from "@/lib/api-client";

export async function fetchJobs(accessToken: string | null, params: URLSearchParams): Promise<JobListResponse> {
  const query = params.toString();
  const path = query ? `/v1/jobs?${query}` : "/v1/jobs";
  return apiFetch<JobListResponse>(path, { accessToken });
}

export async function fetchJob(accessToken: string | null, id: string): Promise<Job> {
  return apiFetch<Job>(`/v1/jobs/${id}`, { accessToken });
}

export async function createJob(accessToken: string | null, payload: JobCreateRequest): Promise<Job> {
  return apiFetch<Job>("/v1/jobs/generate", {
    method: "POST",
    body: JSON.stringify(payload),
    accessToken,
  });
}
