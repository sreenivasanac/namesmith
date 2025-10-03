### Rules for the AI Agentic Codex

- **Project naming and branding**
  - I have not yet fully decided on the name of the Product. For now, it is "Namesmith"
  - Use `namesmith` for variables and identifiers when a project name is required.
  - For any user-facing text, reference a single global branding constant set to "Namesmith" so it can be changed in one place later.

- **Legacy code policy**
  - Treat `old_code/` as reference-only. Do not modify files inside `old_code/`.
  - You may read `old_code/` to understand the prior implementation, but do not adopt outdated versions from it.

- **Tools, versions, and package managers**
  - Use the latest stable versions of software and libraries.
  - Node.js: use `pnpm` for package management.
  - Python: use `uv` for environment and dependency management.

- **Frontend standards**
  - Follow the frontend rules defined in `agentic_development_docs/project_design_plan/5_frontend_design.md`.

- **LangChain documentation sources**
  - Prefer the Context7 MCP server for the latest LangChain documentation.
  - If unavailable, use:
    - `agentic_development_docs/tools_documentation/langchain_full_doc.md`
    - `agentic_development_docs/tools_documentation/langchain_llms_brief.md`

- **Development communication and logging**
  - For any communication or logging during development, write documents to `agentic_development_docs/agent_communication/`.
  - Examples include: assumptions made during implementation, design notes, and future work ideas.

- **Defaults and constraints**
  - Default to modern, stable, well-supported stacks and patterns.
  - Keep configuration and branding centralized and easily changeable via constants.
  - Any deviation from these rules requires explicit approval.
