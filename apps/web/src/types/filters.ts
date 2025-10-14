export interface RangeFilter {
  min: number;
  max: number;
}

export interface DomainFiltersState {
  search: string;
  status: string[];
  tld: string[];
  agentModel: string[];
  industry: string[];
  memorability: RangeFilter;
  pronounceability: RangeFilter;
  brandability: RangeFilter;
  overall: RangeFilter;
  seoKeywordRelevance: RangeFilter;
}

export interface DomainFiltersMetadata {
  statuses: string[];
  tlds: string[];
  agent_models: string[];
  industries: string[];
}
