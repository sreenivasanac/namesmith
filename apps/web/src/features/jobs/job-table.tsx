"use client";

import Link from "next/link";
import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { formatDistanceToNow } from "date-fns";
import type { JobListResponse } from "@namesmith/shared-ts";
import { queryKeys } from "@/lib/query-keys";
import { fetchJobs } from "@/lib/api/jobs";
import { useAccessToken } from "@/hooks/useAccessToken";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { JobStatusBadge } from "@/features/jobs/status-badge";
import { Button } from "@/components/ui/button";

interface JobTableProps {
  initialData: JobListResponse;
  limit?: number;
  showViewAllLink?: boolean;
}

export function JobTable({ initialData, limit, showViewAllLink = true }: JobTableProps) {
  const token = useAccessToken();

  const params = useMemo(() => new URLSearchParams(limit ? { limit: String(limit) } : {}), [limit]);

  const { data } = useQuery({
    queryKey: queryKeys.jobs(Object.fromEntries(params)),
    queryFn: () => fetchJobs(token!, params),
    enabled: Boolean(token),
    initialData,
  });

  const jobs = data?.items ?? [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Recent jobs</h2>
        {showViewAllLink ? (
          <Button variant="link" asChild>
            <Link href="/dashboard/jobs">View all</Link>
          </Button>
        ) : null}
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Job ID</TableHead>
            <TableHead>Entry path</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Created</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {jobs.length === 0 ? (
            <TableRow>
              <TableCell colSpan={5} className="text-center text-sm text-muted-foreground">
                No jobs yet. Create your first generation job.
              </TableCell>
            </TableRow>
          ) : (
            jobs.map((job) => (
              <TableRow key={job.id}>
                <TableCell className="font-mono text-xs">{job.id.slice(0, 8)}…</TableCell>
                <TableCell className="capitalize">{job.entry_path}</TableCell>
                <TableCell><JobStatusBadge status={job.status} /></TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}
                </TableCell>
                <TableCell className="text-right">
                  <Button variant="outline" size="sm" asChild>
                    <Link href={`/dashboard/jobs/${job.id}`}>View</Link>
                  </Button>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
