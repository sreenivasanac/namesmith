import type { Domain, DomainListResponse } from "@namesmith/shared-ts";
import { apiFetch } from "@/lib/api-client";

export interface DomainQueryParams {
  search?: string;
  status?: string[];
  tld?: string[];
  agent_model?: string[];
  category?: string[];
  memorability_min?: number;
  memorability_max?: number;
  pronounceability_min?: number;
  pronounceability_max?: number;
  brandability_min?: number;
  brandability_max?: number;
  overall_min?: number;
  overall_max?: number;
  seo_keyword_relevance_min?: number;
  seo_keyword_relevance_max?: number;
  job_id?: string;
  cursor?: string;
  limit?: number;
  sort_by?: string;
  sort_dir?: "asc" | "desc";
}

export function buildDomainQuery(params: DomainQueryParams): string {
  const qs = new URLSearchParams();
  if (params.search) qs.set("search", params.search);
  if (params.status?.length) qs.set("status", params.status.join(","));
  if (params.tld?.length) qs.set("tld", params.tld.join(","));
  if (params.agent_model?.length) qs.set("agent_model", params.agent_model.join(","));
  if (params.category?.length) qs.set("category", params.category.join(","));
  if (params.job_id) qs.set("job_id", params.job_id);
  if (params.cursor) qs.set("cursor", params.cursor);
  if (params.limit) qs.set("limit", params.limit.toString());
  if (params.sort_by) qs.set("sort_by", params.sort_by);
  if (params.sort_dir) qs.set("sort_dir", params.sort_dir);

  const numericKeys: Array<[keyof DomainQueryParams, keyof DomainQueryParams]> = [
    ["memorability_min", "memorability_max"],
    ["pronounceability_min", "pronounceability_max"],
    ["brandability_min", "brandability_max"],
    ["overall_min", "overall_max"],
    ["seo_keyword_relevance_min", "seo_keyword_relevance_max"],
  ];

  for (const [minKey, maxKey] of numericKeys) {
    const minValue = params[minKey];
    const maxValue = params[maxKey];
    if (typeof minValue === "number") qs.set(minKey, minValue.toString());
    if (typeof maxValue === "number") qs.set(maxKey, maxValue.toString());
  }

  return qs.toString();
}

export async function fetchDomains(accessToken: string | null, params: DomainQueryParams = {}): Promise<DomainListResponse> {
  const query = buildDomainQuery(params);
  const path = query ? `/v1/domains?${query}` : "/v1/domains";
  return apiFetch<DomainListResponse>(path, { accessToken });
}

export async function fetchDomain(accessToken: string | null, id: string): Promise<Domain> {
  return apiFetch<Domain>(`/v1/domains/${id}`, { accessToken });
}
