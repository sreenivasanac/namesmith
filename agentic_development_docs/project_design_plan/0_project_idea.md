NameSmith - Multi-Agent System for Domain Name Generation

Project Requirements Document

High-Level Summary
A multi-step multi-agent bot system to streamline high quality brandable domain name purchase - from market research analysis, domain name generation, domain name scoring, domain name purchase, domain name resale if in the case of speculative investing, by automating the end-to-end process of market research, domain name generation, domain name evaluation, domain purchase and resale of high-quality brandable domain names.

Value Proposition
    * Makes finding available domain names easier for businesses looking for high quality domain names
    * Streamline the workflow for domain investors and resellers
    * Make use of the available arbitrage in the domain names market

Problem Statement
    * Finding high-quality brandable domain names for SaaS businesses is very hard
    * Examples of good names: Corten.com, Amplitude.ai, Latitude.com
    * Requires lots of research and hundreds of trial and error attempts - to check if they are available or not.

Target Audience
1. Online Businesses seeking premium domain names
    * Could be hosted as a service like Domains-GPT or Namy.ai
2. Domain Name Investors & Domain Name Resellers
    * Those who purchase domain names speculatively for future sale at higher prices
    * Need to keep updated with trends


Business Objectives
    1. Improve Domain Quality: Identify high-value, brandable domain names with greater potential for resale
    2. Increase Efficiency: Automate the tedious process of domain name research and availability checking
    3. Maximize ROI: Increase profitability by acquiring and reselling premium domain names

Key Performance Indicators (KPIs)
* Quality of brandable domain names generated
* Bot scoring quality based on different attributes
* Manual Quality review through Domain Discovery Console
* Lesser manual intervention/touchpoints
* Total user time spent in research
* Average resale value of acquired domain names
* Return on investment (ROI) on domain name acquisitions

Key Features
Entry A (Investors): Market Trends Understanding
    * Bot-1 gathers topics and trends from curated sources to inform naming (no LLM here)
    * Stores structured trends in DB; used as context for generation
Entry B (Businesses): Prompt-driven Context + Similar Names
    * Business owner describes their idea, constraints (tone/length/keywords/TLDs)
    * System retrieves similar company names and examples from a `company_names` dataset to ground prompts
2. Domain Name Generation
    * Bot-2 generates creative and brandable domain names
    * Uses detailed prompts, categories/keywords, trends and examples
    * Users can select which LLM model powers each generation run
3. Dedupe and Filtering
    * Remove near-duplicates, enforce constraints (length, style, restricted patterns)
4. Scoring of Generated Domain Names
    * Bot-3 scores domain names based on:
        * Memorability
        * Pronounceability
        * Length
        * Brandability
    * Hybrid approach: heuristics + LLM judge with clear rubric
    * Scoring model choice is user-configurable per job
5. Domain Name Availability Verification
    * For now: verify via registrar API (WhoAPI) directly
    * Future: add DNS heuristics and negative cache to minimize paid checks
    * Small batches may run synchronously; larger batches run as background jobs
6. Domain Discovery Console
    * User-friendly dashboard to:
        * Review generated domain names
        * View scores
        * Check availability status
        * View crawled domain/company information
7. Domain Name Purchase
    * Available domains visible with scores and rankings
    * Human-in-the-loop for evaluation and purchase decisions
8. Domain Name Resale
    * Create webpage for sale
    * Post in domain resale marketplaces
9. Trademark Conflict Flagging
    * Verify if names are trademarked
10. Background Jobs & Progress
    * Long-running tasks (generation, availability batches) run via Celery workers
    * API returns job/batch ids and progress can be polled from the Console

Target TLDs
    * Primary: .com and .ai domain names
    * Additional TLDs may be considered for specific categories/keywords

Multi-Agent Workflow
1. Start → Initialize
2. Entry selection
    * If business prompt present → gather similar names/examples
    * Else (investor flow) → gather trends/topics
    * If both present → merge contexts (dedupe)
3. Domain name generation → produce candidate list
4. Dedupe and filter → enforce constraints and remove near-duplicates
5. Scoring → heuristics + LLM judge; compute overall score
6. Availability checks → registrar API now; add DNS heuristics later
7. Persist results and checkpoints → DB rows for domains, evaluations, availability
8. Review in Console → filters, sorting, details
9. Purchase decision (human-in-the-loop)
10. Optional resale listing and landing page
11. End

Technology Stack
* Multi-Agent Framework: LangGraph (Python)
* Observability: Langfuse; Sentry (frontend + backend)
* Dashboard: Next.js (TypeScript, App Router) + Tailwind/shadcn
* Database: Supabase (Postgres)
* API: FastAPI (Python)
* Background processing: Celery + Redis; job ids for polling
* Auth: Supabase JWT (Console issues, API verifies)
* API Integrations: Registrar APIs (WhoAPI primary; optionally WhoisJSONAPI, Domain‑checker7)

Competitor Analysis
Current services offering domain name suggestions:
* Domains-GPT
* nomenate.com
* namemaxi.com
* namefinder.ai
* namy.ai
* yournextdomain.com

Main Issue with the current domain name generation providers: Current services generate simple concatenations (e.g., ecoclothing.com, eazybooking.com) rather than brandable names like Laminar.AI or Inconvo.com

Data Requirements
Sources for Training:
1. Company Directories:
    * Crunchbase (potentially $99/month for 5000 rows)
    * YCombinator list of startups
    * Extract: domain name, company name, description, industry, TLD, tags
    * Ad-hoc scrapers live under `services/api/scripts/scrapers/` and populate a `company_names` dataset
2. Domain Marketplaces:
    * Historical sales data
    * High-priced domain examples with metadata
3. Additional Sources:
    * Reddit subreddit names for niches/trends
    * Target: 2000-10,000 examples with different categories

Domain Name Attributes to Track
* Domain name and business name
* Domain length
* TLD type
* Categories (SaaS, HealthTech, FinTech, EdTech)
* Keywords
* Memorability Score (1-10)
* Pronounceability Score (1-10)
* Brandability Score (1-10)
* SEO/Keyword Relevance Score (1-10)
* Industry Relevance Score (1-10)
* Availability Status
* Estimated Value
* Language/Localization
* Suggested Use Cases
* Competitor Match
* Related Domains
* Historical Sales Data Match
* Trademark Status

API Integrations
Domain Availability Checking:
* WhoAPI: $99 for 1M requests/month
* WhoisJSONAPI: $50 for 2M requests/month
* Domain‑checker7: $10–125/month depending on volume
* Strategy (current → future): call registrar API (WhoAPI) now for availability; add DNS heuristics and negative cache later to reduce paid calls

Domain Purchase/Registration:
* ionos.com
* porkbun.com
* Both have good reviews and API documentation


Success Criteria
* System generates high-quality, brandable domain names
* Users report significant time savings
* Successful domain acquisitions and profitable resales
* System adaptability to market trends
* Positive feedback from demo judges

Future Enhancements
* Prompt comparison and optimization
* Fine-tuning domain generation model
* Market research & trends analysis
* Twitter/Reddit crawling
* Custom prompts and examples for users
* Email notifications
* Automated domain parking
* DNS pre-checking for cost savings
* Premium/auction domain trading
* Trademark conflict checking



This comprehensive requirements document provides the foundation for developing a multi-agent system that automates the domain name investment process from research to resale.

