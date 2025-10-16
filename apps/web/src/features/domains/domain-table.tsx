"use client";

import { useMemo, useState } from "react";
import { formatDistanceToNow } from "date-fns";
import type { Domain } from "@namesmith/shared-ts";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

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

interface DomainTableProps {
  domains: Domain[];
  onSelect(domain: Domain): void;
}

export function DomainTable({ domains, onSelect }: DomainTableProps) {
  const [sortKey, setSortKey] = useState<keyof Domain | "overall_score">("overall_score");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const sorted = useMemo(() => {
    const copy = [...domains];
    copy.sort((a, b) => {
      let aValue: number | string | null = null;
      let bValue: number | string | null = null;
      if (sortKey === "overall_score") {
        aValue = a.evaluation?.overall_score ?? 0;
        bValue = b.evaluation?.overall_score ?? 0;
      } else {
        const aAny = a[sortKey];
        const bAny = b[sortKey];
        aValue = typeof aAny === "number" || typeof aAny === "string" ? aAny : null;
        bValue = typeof bAny === "number" || typeof bAny === "string" ? bAny : null;
      }
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

  const toggleSort = (key: typeof sortKey) => {
    if (sortKey === key) {
      setSortDir((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  };

  return (
    <div className="space-y-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>
              <button type="button" className="flex items-center gap-2" onClick={() => toggleSort("label")}>Domain</button>
            </TableHead>
            <TableHead>TLD</TableHead>
            <TableHead>
              <button type="button" className="flex items-center gap-2" onClick={() => toggleSort("length")}>Length</button>
            </TableHead>
            <TableHead>Model</TableHead>
            <TableHead>Availability</TableHead>
            <TableHead>
              <button type="button" className="flex items-center gap-2" onClick={() => toggleSort("overall_score")}>Overall score</button>
            </TableHead>
            <TableHead>Created</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.map((domain) => (
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
      {sorted.length === 0 ? <p className="text-sm text-muted-foreground">No domains match the current filters.</p> : null}
    </div>
  );
}
