"use client";

import { useMemo, useState } from "react";
import { formatDistanceToNow } from "date-fns";
import type { Domain } from "@namesmith/shared-ts";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ChevronDown, ChevronUp, ChevronsUpDown } from "lucide-react";

function AvailabilityBadge({ status }: { status?: string | null }) {
  if (!status) {
    return <Badge variant="outline">Unknown</Badge>;
  }
  const normalized = status.toLowerCase();
  if (normalized === "available") {
    return <Badge variant="default">Available</Badge>;
  }
  if (normalized === "registered") {
    return <Badge variant="secondary">Registered</Badge>;
  }
  if (normalized === "error") {
    return <Badge variant="destructive">Error</Badge>;
  }
  return <Badge variant="outline">{status}</Badge>;
}

type SortKey = "overall_score" | "label" | "length" | "availability" | "created_at";

interface DomainTableProps {
  domains: Domain[];
  onSelect(domain: Domain): void;
  isLoading?: boolean;
}

export function DomainTable({ domains, onSelect, isLoading = false }: DomainTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("overall_score");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const getSortValue = (domain: Domain, key: SortKey): number | string | null => {
    if (key === "overall_score") {
      return domain.evaluation?.overall_score ?? 0;
    }

    if (key === "label") {
      return (domain.display_name ?? domain.full_domain ?? "").toLowerCase();
    }

    if (key === "availability") {
      const status = domain.availability?.status?.toLowerCase();
      if (status === "available") return 0;
      if (status === "registered") return 1;
      if (status === "error") return 2;
      return 3;
    }

    if (key === "created_at") {
      const timestamp = new Date(domain.created_at).getTime();
      return Number.isNaN(timestamp) ? null : timestamp;
    }

    if (key === "length") {
      return domain.length;
    }

    return null;
  };

  const getSortIcon = (key: SortKey) => {
    if (sortKey !== key) {
      return <ChevronsUpDown className="h-4 w-4 text-muted-foreground" />;
    }
    return sortDir === "asc" ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />;
  };

  const sorted = useMemo(() => {
    const copy = [...domains];
    copy.sort((a, b) => {
      const aValue = getSortValue(a, sortKey);
      const bValue = getSortValue(b, sortKey);
      if (aValue === bValue) return 0;
      if (aValue == null) return sortDir === "asc" ? -1 : 1;
      if (bValue == null) return sortDir === "asc" ? 1 : -1;
      if (typeof aValue === "number" && typeof bValue === "number") {
        return sortDir === "asc" ? aValue - bValue : bValue - aValue;
      }
      const aStr = String(aValue).toLowerCase();
      const bStr = String(bValue).toLowerCase();
      return sortDir === "asc" ? aStr.localeCompare(bStr) : bStr.localeCompare(aStr);
    });
    return copy;
  }, [domains, sortDir, sortKey]);

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      if (key === "availability") {
        setSortDir("asc");
      } else if (key === "created_at") {
        setSortDir("desc");
      } else if (key === "label") {
        setSortDir("asc");
      } else {
        setSortDir("desc");
      }
    }
  };

  const loadingRows = Array.from({ length: 5 });

  return (
    <div className="space-y-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>
              <button type="button" className="flex items-center gap-2" onClick={() => toggleSort("label")}>
                Domain
                {getSortIcon("label")}
              </button>
            </TableHead>
            <TableHead>TLD</TableHead>
            <TableHead>
              <button type="button" className="flex items-center gap-2" onClick={() => toggleSort("length")}>
                Length
                {getSortIcon("length")}
              </button>
            </TableHead>
            <TableHead>Model</TableHead>
            <TableHead>
              <button type="button" className="flex items-center gap-2" onClick={() => toggleSort("availability")}>
                Availability
                {getSortIcon("availability")}
              </button>
            </TableHead>
            <TableHead>
              <button type="button" className="flex items-center gap-2" onClick={() => toggleSort("overall_score")}>
                Overall score
                {getSortIcon("overall_score")}
              </button>
            </TableHead>
            <TableHead>
              <button type="button" className="flex items-center gap-2" onClick={() => toggleSort("created_at")}>
                Created
                {getSortIcon("created_at")}
              </button>
            </TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading
            ? loadingRows.map((_, index) => (
                <TableRow key={`loading-${index}`}>
                  <TableCell className="font-medium"><Skeleton className="h-4 w-32" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-12" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-8 w-24" /></TableCell>
                </TableRow>
              ))
            : sorted.map((domain) => (
            <TableRow key={domain.id} className="cursor-pointer" onClick={() => onSelect(domain)}>
              <TableCell className="font-medium">{domain.display_name ?? domain.full_domain}</TableCell>
              <TableCell>.{domain.tld}</TableCell>
              <TableCell>{domain.length}</TableCell>
              <TableCell>{domain.agent_model ?? "—"}</TableCell>
              <TableCell><AvailabilityBadge status={domain.availability?.status} /></TableCell>
              <TableCell>{domain.evaluation?.overall_score ?? "—"}</TableCell>
              <TableCell className="text-sm text-muted-foreground">
                {formatDistanceToNow(new Date(domain.created_at), { addSuffix: true })}
              </TableCell>
              <TableCell className="text-right">
                <Button variant="outline" size="sm" onClick={(event) => { event.stopPropagation(); onSelect(domain); }}>
                  View details
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {!isLoading && sorted.length === 0 ? (
        <p className="text-sm text-muted-foreground">No domains match the current filters.</p>
      ) : null}
    </div>
  );
}
