"use client";

import { format } from "date-fns";
import type { Domain } from "@namesmith/shared-ts";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetClose,
} from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface DomainDetailSheetProps {
  domain: Domain | null;
  onClose(): void;
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-2">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">{title}</h3>
      <div className="space-y-1 text-sm text-foreground">{children}</div>
    </section>
  );
}

export function DomainDetailSheet({ domain, onClose }: DomainDetailSheetProps) {
  if (!domain) {
    return null;
  }

  const createdAt = format(new Date(domain.created_at), "PPP p");

  return (
    <Sheet open={Boolean(domain)} onOpenChange={(open) => { if (!open) onClose(); }}>
      <SheetContent className="w-full max-w-xl p-0">
        <SheetHeader className="border-b p-6">
          <SheetTitle className="text-2xl font-semibold">{domain.display_name ?? domain.full_domain}</SheetTitle>
          <SheetDescription>
            <span className="text-sm text-muted-foreground">Generated {createdAt}</span>
          </SheetDescription>
        </SheetHeader>
        <ScrollArea className="h-[calc(100vh-7rem)]">
          <div className="space-y-6 p-6">
            <Section title="Domain">
              <p className="text-lg font-medium">{domain.full_domain}</p>
              <p>TLD: <strong>.{domain.tld}</strong></p>
              <p>Length: {domain.length}</p>
              <p>Processed by: {domain.processed_by_agent ?? "Unknown"}</p>
              <p>Model: {domain.agent_model ?? "Unknown"}</p>
            </Section>

            <Section title="Availability">
              <p>Status: {domain.availability?.status ?? "unknown"}</p>
              {domain.availability?.created_at ? (
                <p>Checked: {format(new Date(domain.availability.created_at), "PPP p")}</p>
              ) : null}
              <div className="flex gap-2 pt-2">
                <Button variant="ghost" size="sm" asChild>
                  <a href={`https://who.is/whois/${domain.full_domain}`} target="_blank" rel="noreferrer">Open WHOIS</a>
                </Button>
              </div>
            </Section>

            {domain.evaluation ? (
              <Section title="Evaluation">
                <div className="grid grid-cols-2 gap-2">
                  <Badge variant="secondary">Memorability {domain.evaluation.memorability_score}/10</Badge>
                  <Badge variant="secondary">Pronounceability {domain.evaluation.pronounceability_score}/10</Badge>
                  <Badge variant="secondary">Brandability {domain.evaluation.brandability_score}/10</Badge>
                  <Badge variant="default">Overall {domain.evaluation.overall_score}/10</Badge>
                </div>
                <p className="pt-2 text-sm text-muted-foreground">{domain.evaluation.description}</p>
                {domain.evaluation.possible_categories.length ? (
                  <p>Categories: {domain.evaluation.possible_categories.join(", ")}</p>
                ) : null}
                {domain.evaluation.possible_keywords.length ? (
                  <p>Keywords: {domain.evaluation.possible_keywords.join(", ")}</p>
                ) : null}
              </Section>
            ) : null}

            {domain.seo_analysis ? (
              <Section title="SEO insights">
                <p>SEO keyword relevance: {domain.seo_analysis.seo_keyword_relevance_score}/10</p>
                <p>Industry relevance: {domain.seo_analysis.industry_relevance_score}/10</p>
                <p>Potential resale value: ${domain.seo_analysis.potential_resale_value}</p>
                <p>Language: {domain.seo_analysis.language}</p>
                {domain.seo_analysis.seo_keywords.length ? (
                  <p>Keywords: {domain.seo_analysis.seo_keywords.join(", ")}</p>
                ) : null}
                {domain.seo_analysis.trademark_status ? (
                  <p>Trademark status: {domain.seo_analysis.trademark_status}</p>
                ) : null}
              </Section>
            ) : null}
          </div>
        </ScrollArea>
        <div className="flex items-center justify-between border-t p-4">
          <div className="space-x-2 text-sm text-muted-foreground">
            <span>ID:</span>
            <span className="font-mono text-xs">{domain.id}</span>
          </div>
          <SheetClose asChild>
            <Button variant="outline" onClick={onClose}>Close</Button>
          </SheetClose>
        </div>
      </SheetContent>
    </Sheet>
  );
}
