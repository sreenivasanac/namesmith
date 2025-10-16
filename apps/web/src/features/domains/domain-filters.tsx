"use client";

import { useEffect, useMemo, useState } from "react";
import type { DomainFiltersMetadata } from "@namesmith/shared-ts";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { PulsatingButton } from "@/components/ui/pulsating-button";
import { useFilterStore } from "@/store/filter-store";
import type { DomainFiltersState, RangeFilter } from "@/types/filters";
import { cn } from "@/lib/utils";

function TitleCase(text: string): string {
  if (!text) return text;
  return text
    .replace(/[-_]+/g, " ")
    .split(" ")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

interface DomainFiltersProps {
  metadata?: DomainFiltersMetadata | null;
}

export function DomainFilters({ metadata }: DomainFiltersProps) {
  const {
    search,
    setSearch,
    status,
    setStatus,
    tld,
    setTld,
    agentModel,
    setAgentModel,
    industry,
    setIndustry,
    memorability,
    pronounceability,
    brandability,
    overall,
    seoKeywordRelevance,
    setRange,
    reset,
  } = useFilterStore();

  type ArrayFilterKey = "status" | "tld" | "agentModel" | "industry";
  type RangeFilterKey = "memorability" | "pronounceability" | "brandability" | "overall" | "seoKeywordRelevance";

  const buildDraftFromStore = (): DomainFiltersState => ({
    search,
    status: [...status],
    tld: [...tld],
    agentModel: [...agentModel],
    industry: [...industry],
    memorability: { ...memorability },
    pronounceability: { ...pronounceability },
    brandability: { ...brandability },
    overall: { ...overall },
    seoKeywordRelevance: { ...seoKeywordRelevance },
  });

  const [draftFilters, setDraftFilters] = useState<DomainFiltersState>(buildDraftFromStore);
  const [hasFilterChanges, setHasFilterChanges] = useState(false);

  const statusOptions = useMemo(() => metadata?.statuses ?? ["available", "registered", "unknown"], [metadata?.statuses]);
  const tldOptions = useMemo(() => metadata?.tlds ?? ["com", "ai"], [metadata?.tlds]);
  const agentModelOptions = useMemo(() => metadata?.agent_models ?? [], [metadata?.agent_models]);
  const industryOptions = useMemo(() => metadata?.industries ?? [], [metadata?.industries]);

  useEffect(() => {
    setDraftFilters(buildDraftFromStore());
    setHasFilterChanges(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    search,
    status,
    tld,
    agentModel,
    industry,
    memorability,
    pronounceability,
    brandability,
    overall,
    seoKeywordRelevance,
  ]);

  const markDirty = () => {
    setHasFilterChanges(true);
  };

  const handleDraftToggle = (key: ArrayFilterKey, value: string) => {
    setDraftFilters((current) => {
      const values = current[key];
      const next = values.includes(value) ? values.filter((item) => item !== value) : [...values, value];
      return { ...current, [key]: next };
    });
    markDirty();
  };

  const handleRangeChange = (key: RangeFilterKey, range: RangeFilter) => {
    setDraftFilters((current) => ({
      ...current,
      [key]: { ...range },
    }));
    markDirty();
  };

  const renderRange = (label: string, key: RangeFilterKey) => {
    const range = draftFilters[key];
    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm font-medium">
          <span>{label}</span>
          <span className="text-muted-foreground">{range.min} – {range.max}</span>
        </div>
        <Slider
          min={1}
          max={10}
          step={1}
          value={[range.min, range.max]}
          onValueChange={([min, max]) => handleRangeChange(key, { min, max })}
        />
      </div>
    );
  };

  const handleSubmit = () => {
    setSearch(draftFilters.search);
    setStatus([...draftFilters.status]);
    setTld([...draftFilters.tld]);
    setAgentModel([...draftFilters.agentModel]);
    setIndustry([...draftFilters.industry]);
    setRange("memorability", { ...draftFilters.memorability });
    setRange("pronounceability", { ...draftFilters.pronounceability });
    setRange("brandability", { ...draftFilters.brandability });
    setRange("overall", { ...draftFilters.overall });
    setRange("seoKeywordRelevance", { ...draftFilters.seoKeywordRelevance });
    setHasFilterChanges(false);
  };

  const handleReset = () => {
    reset();
    setDraftFilters({
      search: "",
      status: [],
      tld: [],
      agentModel: [],
      industry: [],
      memorability: { min: 1, max: 10 },
      pronounceability: { min: 1, max: 10 },
      brandability: { min: 1, max: 10 },
      overall: { min: 1, max: 10 },
      seoKeywordRelevance: { min: 1, max: 10 },
    });
    setHasFilterChanges(false);
  };

  return (
    <div className="flex w-72 flex-col gap-6 border-r bg-sidebar p-4 text-sm text-sidebar-foreground">
      <div className="space-y-2">
        <Label htmlFor="search">Search domains</Label>
        <Input
          id="search"
          value={draftFilters.search}
          onChange={(event) => {
            const value = event.target.value;
            setDraftFilters((current) => ({ ...current, search: value }));
            markDirty();
          }}
          placeholder="Search by name"
        />
      </div>

      <section className="space-y-2">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Availability</p>
        <div className="space-y-2">
          {statusOptions.map((value) => (
            <label key={value} className="flex items-center gap-2">
              <Checkbox checked={draftFilters.status.includes(value)} onCheckedChange={() => handleDraftToggle("status", value)} />
              <span>{TitleCase(value)}</span>
            </label>
          ))}
        </div>
      </section>

      <section className="space-y-2">
        <p className="text-xs font-semibold uppercase text-muted-foreground">TLDs</p>
        <div className="space-y-2">
          {tldOptions.map((value) => (
            <label key={value} className="flex items-center gap-2">
              <Checkbox checked={draftFilters.tld.includes(value)} onCheckedChange={() => handleDraftToggle("tld", value)} />
              <span>.{value}</span>
            </label>
          ))}
        </div>
      </section>

      <section className="space-y-2">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Models</p>
        <div className="space-y-2">
          {agentModelOptions.map((value) => (
            <label key={value} className="flex items-center gap-2">
              <Checkbox checked={draftFilters.agentModel.includes(value)} onCheckedChange={() => handleDraftToggle("agentModel", value)} />
              <span>{value}</span>
            </label>
          ))}
          {agentModelOptions.length === 0 ? <p className="text-xs text-muted-foreground">No agent metadata yet</p> : null}
        </div>
      </section>

      <section className="space-y-2">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Industries</p>
        <div className="flex flex-wrap gap-2">
          {industryOptions.map((value) => {
            const active = draftFilters.industry.includes(value);
            return (
              <button
                key={value}
                type="button"
                onClick={() => handleDraftToggle("industry", value)}
                className={cn(
                  "rounded-full border px-2 py-1 text-xs transition",
                  active ? "bg-primary text-primary-foreground" : "hover:bg-secondary"
                )}
              >
                {TitleCase(value)}
              </button>
            );
          })}
          {industryOptions.length === 0 ? <p className="text-xs text-muted-foreground">No industry metadata</p> : null}
        </div>
      </section>

      <section className="space-y-4">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Scores</p>
        {renderRange("Memorability", "memorability")}
        {renderRange("Pronounceability", "pronounceability")}
        {renderRange("Brandability", "brandability")}
        {renderRange("Overall", "overall")}
        {renderRange("SEO keyword relevance", "seoKeywordRelevance")}
      </section>

      <div className="space-y-2">
        <PulsatingButton
          type="button"
          onClick={handleSubmit}
          disabled={!hasFilterChanges}
          className={cn("w-full justify-center", !hasFilterChanges && "opacity-70")}
        >
          Show results
        </PulsatingButton>
        <p className="text-center text-xs text-muted-foreground">Adjust filters, then click Show results.</p>
        <Button variant="ghost" type="button" onClick={handleReset} className="w-full">
          Reset filters
        </Button>
      </div>
    </div>
  );
}
