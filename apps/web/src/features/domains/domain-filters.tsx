"use client";

import { useMemo } from "react";
import type { DomainFiltersMetadata } from "@namesmith/shared-ts";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { useFilterStore } from "@/store/filter-store";
import type { RangeFilter } from "@/types/filters";
import { cn } from "@/lib/utils";

function TitleCase(text: string): string {
  if (!text) return text;
  return text
    .replace(/[\-_]+/g, " ")
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

  const statusOptions = useMemo(() => metadata?.statuses ?? ["available", "registered", "unknown"], [metadata?.statuses]);
  const tldOptions = useMemo(() => metadata?.tlds ?? ["com", "ai"], [metadata?.tlds]);
  const agentModelOptions = useMemo(() => metadata?.agent_models ?? [], [metadata?.agent_models]);
  const industryOptions = useMemo(() => metadata?.industries ?? [], [metadata?.industries]);

  const handleToggle = (values: string[], setValues: (values: string[]) => void, value: string) => {
    const next = values.includes(value) ? values.filter((item) => item !== value) : [...values, value];
    setValues(next);
  };

  const renderRange = (label: string, range: RangeFilter, key: Parameters<typeof setRange>[0]) => (
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
        onValueChange={([min, max]) => setRange(key, { min, max })}
      />
    </div>
  );

  return (
    <div className="flex w-72 flex-col gap-6 border-r bg-sidebar p-4 text-sm text-sidebar-foreground">
      <div className="space-y-2">
        <Label htmlFor="search">Search domains</Label>
        <Input id="search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search by name" />
      </div>

      <section className="space-y-2">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Availability</p>
        <div className="space-y-2">
          {statusOptions.map((value) => (
            <label key={value} className="flex items-center gap-2">
              <Checkbox checked={status.includes(value)} onCheckedChange={() => handleToggle(status, setStatus, value)} />
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
              <Checkbox checked={tld.includes(value)} onCheckedChange={() => handleToggle(tld, setTld, value)} />
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
              <Checkbox checked={agentModel.includes(value)} onCheckedChange={() => handleToggle(agentModel, setAgentModel, value)} />
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
            const active = industry.includes(value);
            return (
              <button
                key={value}
                type="button"
                onClick={() => handleToggle(industry, setIndustry, value)}
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
        {renderRange("Memorability", memorability, "memorability")}
        {renderRange("Pronounceability", pronounceability, "pronounceability")}
        {renderRange("Brandability", brandability, "brandability")}
        {renderRange("Overall", overall, "overall")}
        {renderRange("SEO keyword relevance", seoKeywordRelevance, "seoKeywordRelevance")}
      </section>

      <Button variant="ghost" onClick={reset} className="mt-auto">
        Reset filters
      </Button>
    </div>
  );
}
