### Rules for the AI Agentic Codex

- **Development implementation**
  - For this run, develop the major features only. Not the ones like debug logs using sentry, observability using langfuse. We will implement them later.
  - As far as possible, keep the development code simple and straight-forward.
  - You are an expert software engineer with 30 years of programming experience. Follow best programming practices.
  - If there are TODOs, add as comment in the same code file while you are implementing them.

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
    - Install pnpm packages only for this project folder, not globally.
  - Python: use `uv` for environment and dependency management.
    - Please create an environment with uv, and install within that environment, not globally.

- **Frontend standards**
  - Follow the frontend rules defined in `agentic_development_docs/project_design_plan/5_frontend_design.md`.

- **Tools and frameworks documentation sources**
  - Prefer the Context7 MCP server for the latest documentation for any of the tools, frameworks and packages that you want to use. 
  - For example, use context7 MCP server for LangChain documentation.
  - If unavailable, use:
    - `agentic_development_docs/tools_documentation/langchain_full_doc.md`
    - `agentic_development_docs/tools_documentation/langchain_llms_brief.md`

- **Development communication**
  - If you have any question about the implementation, which is an important one, then you can stop and ask me before continuing the implementation.
  - For any communication or logging during development, write documents to `agentic_development_docs/agent_communication/`.
    - Examples include: assumptions made during implementation, design notes, and future work ideas.
  - Feel free to create new markdown files when you want to log your progress, implementation or if you think it will be useful for continuing the implementation of the project.
  - If there are TODOs, add as comment in the same code file while you are implementing them.

- **Defaults and constraints**
  - Default to modern, stable, well-supported stacks and patterns.
  - Keep configuration and branding centralized and easily changeable via constants.
  - Any deviation from these rules requires explicit approval.

