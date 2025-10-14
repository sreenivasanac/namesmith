export const queryKeys = {
  jobs: (params?: Record<string, unknown>) => ["jobs", params ?? {}] as const,
  job: (id: string) => ["job", id] as const,
  domains: (params?: object) => ["domains", params ?? {}] as const,
  domain: (id: string) => ["domain", id] as const,
  jobDomains: (jobId: string, params?: object) => ["job-domains", jobId, params ?? {}] as const,
  filters: () => ["domain-filters"] as const,
};
