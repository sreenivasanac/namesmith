import type { AvailabilityStatus } from "./base";

export interface DomainAvailability {
  status: AvailabilityStatus;
  agent_model?: string | null;
  created_at: string;
}

export interface DomainEvaluation {
  possible_categories: string[];
  possible_keywords: string[];
  memorability_score: number;
  pronounceability_score: number;
  brandability_score: number;
  overall_score: number;
  description: string;
  processed_by_agent?: string | null;
  agent_model?: string | null;
  created_at: string;
}

export interface DomainSeoAnalysis {
  seo_keywords: string[];
  seo_keyword_relevance_score: number;
  industry_relevance_score: number;
  domain_age: number;
  potential_resale_value: number;
  language: string;
  trademark_status?: string | null;
  scored_by_agent?: string | null;
  agent_model?: string | null;
  description: string;
  created_at: string;
}

export interface Domain {
  id: string;
  label: string;
  tld: string;
  full_domain: string;
  display_name?: string | null;
  length: number;
  processed_by_agent?: string | null;
  agent_model?: string | null;
  created_at: string;
  availability?: DomainAvailability | null;
  evaluation?: DomainEvaluation | null;
  seo_analysis?: DomainSeoAnalysis | null;
}

export interface DomainFiltersMetadata {
  statuses: string[];
  tlds: string[];
  agent_models: string[];
  industries: string[];
}

export interface DomainListResponse {
  items: Domain[];
  next_cursor?: string | null;
  filters?: DomainFiltersMetadata;
}
