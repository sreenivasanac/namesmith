export type AvailabilityStatus = "available" | "registered" | "unknown" | "error";

export type JobStatus = "queued" | "running" | "succeeded" | "failed" | "partial";

export type JobType = "generate" | "score" | "availability" | "research";

export type EntryPath = "investor" | "business";

export type Timestamp = string; // ISO string
