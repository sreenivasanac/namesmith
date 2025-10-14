import type { EntryPath, JobStatus, JobType } from "./base";

export interface Job {
  id: string;
  type: JobType;
  entry_path: EntryPath;
  status: JobStatus;
  created_at: string;
  finished_at?: string | null;
  error?: string | null;
  progress?: Record<string, unknown> | null;
  generation_model?: string | null;
  scoring_model?: string | null;
}

export interface JobListResponse {
  items: Job[];
  next_cursor?: string | null;
}

export interface JobCreateRequest {
  entry_path: EntryPath;
  topic?: string | null;
  prompt?: string | null;
  categories?: string[];
  tlds?: string[];
  count?: number;
  generation_model?: string | null;
  scoring_model?: string | null;
}
