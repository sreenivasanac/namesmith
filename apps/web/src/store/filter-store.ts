"use client";

import { create } from "zustand";
import type { DomainFiltersState, RangeFilter } from "@/types/filters";

// Create fresh range objects to avoid shared references across fields
const makeDefaultRange = (): RangeFilter => ({ min: 1, max: 10 });

type RangeKeys = "memorability" | "pronounceability" | "brandability" | "overall" | "seoKeywordRelevance";

interface FilterStore extends DomainFiltersState {
  setSearch(value: string): void;
  setStatus(values: string[]): void;
  setTld(values: string[]): void;
  setAgentModel(values: string[]): void;
  setIndustry(values: string[]): void;
  setRange(key: RangeKeys, value: RangeFilter): void;
  reset(): void;
}

export const useFilterStore = create<FilterStore>((set) => ({
  search: "",
  status: [],
  tld: [],
  agentModel: [],
  industry: [],
  memorability: makeDefaultRange(),
  pronounceability: makeDefaultRange(),
  brandability: makeDefaultRange(),
  overall: makeDefaultRange(),
  seoKeywordRelevance: makeDefaultRange(),
  setSearch: (value) => set({ search: value }),
  setStatus: (values) => set({ status: values }),
  setTld: (values) => set({ tld: values }),
  setAgentModel: (values) => set({ agentModel: values }),
  setIndustry: (values) => set({ industry: values }),
  setRange: (key, value) => set({ [key]: value } as Partial<DomainFiltersState>),
  reset: () =>
    set({
      search: "",
      status: [],
      tld: [],
      agentModel: [],
      industry: [],
      memorability: makeDefaultRange(),
      pronounceability: makeDefaultRange(),
      brandability: makeDefaultRange(),
      overall: makeDefaultRange(),
      seoKeywordRelevance: makeDefaultRange(),
    }),
}));
