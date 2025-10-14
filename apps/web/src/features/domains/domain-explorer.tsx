"use client";

import { useEffect, useMemo, useState } from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import type { Domain, DomainFiltersMetadata, DomainListResponse } from "@namesmith/shared-ts";
import { queryKeys } from "@/lib/query-keys";
import { fetchDomains, type DomainQueryParams } from "@/lib/api/domains";
import { useAccessToken } from "@/hooks/useAccessToken";
import { useFilterStore } from "@/store/filter-store";
import { DomainFilters } from "@/features/domains/domain-filters";
import { DomainTable } from "@/features/domains/domain-table";
import { DomainDetailSheet } from "@/features/domains/domain-detail-sheet";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

const PAGE_SIZE = 50;

function buildQueryParams(state: ReturnType<typeof useFilterStore.getState>): DomainQueryParams {
  const params: DomainQueryParams = { limit: PAGE_SIZE };
  if (state.search) params.search = state.search;
  if (state.status.length) params.status = state.status;
  if (state.tld.length) params.tld = state.tld;
  if (state.agentModel.length) params.agent_model = state.agentModel;
  if (state.industry.length) params.category = state.industry;
  if (state.memorability.min !== 1 || state.memorability.max !== 10) {
    params.memorability_min = state.memorability.min;
    params.memorability_max = state.memorability.max;
  }
  if (state.pronounceability.min !== 1 || state.pronounceability.max !== 10) {
    params.pronounceability_min = state.pronounceability.min;
    params.pronounceability_max = state.pronounceability.max;
  }
  if (state.brandability.min !== 1 || state.brandability.max !== 10) {
    params.brandability_min = state.brandability.min;
    params.brandability_max = state.brandability.max;
  }
  if (state.overall.min !== 1 || state.overall.max !== 10) {
    params.overall_min = state.overall.min;
    params.overall_max = state.overall.max;
  }
  if (state.seoKeywordRelevance.min !== 1 || state.seoKeywordRelevance.max !== 10) {
    params.seo_keyword_relevance_min = state.seoKeywordRelevance.min;
    params.seo_keyword_relevance_max = state.seoKeywordRelevance.max;
  }
  return params;
}

interface DomainExplorerProps {
  initialData: DomainListResponse;
}

export function DomainExplorer({ initialData }: DomainExplorerProps) {
  const token = useAccessToken();
  const [selectedDomain, setSelectedDomain] = useState<Domain | null>(null);
  const filterState = useFilterStore();

  const queryParams = useMemo(() => buildQueryParams(filterState), [filterState]);

  const [metadata, setMetadata] = useState<DomainFiltersMetadata | undefined>(initialData.filters ?? undefined);

  const query = useInfiniteQuery({
    queryKey: queryKeys.domains(queryParams),
    queryFn: async ({ pageParam }) => {
      if (!token) {
        throw new Error("Missing token");
      }
      return fetchDomains(token, { ...queryParams, cursor: pageParam ?? undefined });
    },
    getNextPageParam: (lastPage) => lastPage.next_cursor ?? null,
    enabled: Boolean(token),
    initialPageParam: null as string | null,
    initialData: initialData
      ? { pageParams: [null], pages: [initialData] }
      : undefined,
    staleTime: 30_000,
  });

  useEffect(() => {
    const lastPage = query.data?.pages[query.data.pages.length - 1];
    if (lastPage?.filters) {
      setMetadata(lastPage.filters);
    }
  }, [query.data]);

  const domains = useMemo(() => query.data?.pages.flatMap((page) => page.items) ?? [], [query.data]);

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <DomainFilters metadata={metadata} />
      <div className="flex-1 space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Domain explorer</h1>
            <p className="text-sm text-muted-foreground">Search, filter, and review generated domains.</p>
          </div>
          {query.isFetching ? <Skeleton className="h-3 w-24" /> : null}
        </div>

        <DomainTable domains={domains} onSelect={setSelectedDomain} />

        <div className="flex justify-end">
          <Button
            onClick={() => query.fetchNextPage()}
            disabled={!query.hasNextPage || query.isFetchingNextPage}
            variant="outline"
          >
            {query.isFetchingNextPage ? "Loading..." : query.hasNextPage ? "Load more" : "No more results"}
          </Button>
        </div>
      </div>
      <DomainDetailSheet domain={selectedDomain} onClose={() => setSelectedDomain(null)} />
    </div>
  );
}
