"use client";

import { useMemo, useState } from "react";
import { useQuery, useInfiniteQuery } from "@tanstack/react-query";
import type { Domain, DomainListResponse, Job } from "@namesmith/shared-ts";
import { queryKeys } from "@/lib/query-keys";
import { fetchJob } from "@/lib/api/jobs";
import { fetchDomains } from "@/lib/api/domains";
import { useAccessToken } from "@/hooks/useAccessToken";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { JobStatusBadge } from "@/features/jobs/status-badge";
import { DomainTable } from "@/features/domains/domain-table";
import { DomainDetailSheet } from "@/features/domains/domain-detail-sheet";
import { format } from "date-fns";

interface JobDetailProps {
  job: Job;
  initialDomains: DomainListResponse;
}

const PAGE_SIZE = 50;
const ACTIVE_STATUSES = new Set(["queued", "running", "partial"]);

export function JobDetail({ job, initialDomains }: JobDetailProps) {
  const token = useAccessToken();
  const [selectedDomain, setSelectedDomain] = useState<Domain | null>(null);

  const jobQuery = useQuery({
    queryKey: queryKeys.job(job.id),
    queryFn: () => {
      if (!token) {
        throw new Error("Missing token");
      }
      return fetchJob(token, job.id);
    },
    enabled: Boolean(token),
    initialData: job,
    refetchInterval: (query) => {
      const current = query.state.data;
      if (current && ACTIVE_STATUSES.has(current.status)) {
        return 3000;
      }
      return false;
    },
  });

  const domainsQuery = useInfiniteQuery({
    queryKey: queryKeys.jobDomains(job.id, { limit: PAGE_SIZE }),
    queryFn: ({ pageParam }) => {
      if (!token) {
        throw new Error("Missing token");
      }
      return fetchDomains(token, {
        job_id: job.id,
        cursor: pageParam ?? undefined,
        limit: PAGE_SIZE,
      });
    },
    enabled: Boolean(token),
    getNextPageParam: (lastPage) => lastPage.next_cursor ?? null,
    initialPageParam: null as string | null,
    initialData: initialDomains ? { pageParams: [null], pages: [initialDomains] } : undefined,
  });

  const domains = useMemo(() => domainsQuery.data?.pages.flatMap((page) => page.items) ?? [], [domainsQuery.data]);

  const activeJob = jobQuery.data ?? job;
  const createdAt = format(new Date(activeJob.created_at), "PPP p");
  const finishedAt = activeJob.finished_at ? format(new Date(activeJob.finished_at), "PPP p") : null;
  const progress = (activeJob.progress ?? {}) as Record<string, number>;

  return (
    <div className="space-y-8">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Status</CardTitle>
          </CardHeader>
          <CardContent className="flex items-center gap-3">
            <JobStatusBadge status={activeJob.status} />
            <div className="text-sm text-muted-foreground">
              Created {createdAt}
              {finishedAt ? <div>Finished {finishedAt}</div> : null}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Models</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 text-sm">
            <p>Generation: {activeJob.generation_model ?? "default"}</p>
            <p>Scoring: {activeJob.scoring_model ?? "default"}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Progress</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2 text-xs">
            {Object.entries(progress).length ? (
              Object.entries(progress).map(([key, value]) => (
                <Badge key={key} variant="secondary">
                  {key}: {value}
                </Badge>
              ))
            ) : (
              <span className="text-muted-foreground">Progress not reported yet</span>
            )}
          </CardContent>
        </Card>
      </div>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Generated domains</h2>
            <p className="text-sm text-muted-foreground">Domains associated with this job.</p>
          </div>
          {domainsQuery.isFetching ? <Skeleton className="h-3 w-20" /> : null}
        </div>
        <DomainTable domains={domains} onSelect={setSelectedDomain} />
        <div className="flex justify-end">
          <Button
            variant="outline"
            onClick={() => domainsQuery.fetchNextPage()}
            disabled={!domainsQuery.hasNextPage || domainsQuery.isFetchingNextPage}
          >
            {domainsQuery.isFetchingNextPage ? "Loading..." : domainsQuery.hasNextPage ? "Load more" : "No more names"}
          </Button>
        </div>
      </section>

      <DomainDetailSheet domain={selectedDomain} onClose={() => setSelectedDomain(null)} />
    </div>
  );
}
