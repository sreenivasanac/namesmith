### Rules for the AI Agentic Codex


- **Development implementation**
  - For this run, develop the major features only. Not the ones like debug logs using sentry, observability using langfuse. We will implement them later.
  - As far as possible, keep the development code simple and straight-forward.
  - You are an expert software engineer with 30 years of programming experience. Follow best programming practices.
  - If there are TODOs, add as comment in the same code file while you are implementing them.
  - Go through the design plan in project_design_plan folder.
[0_project_idea.md](agentic_development_docs/project_design_plan/0_project_idea.md) [0_implementation_plan.md](agentic_development_docs/project_design_plan/0_implementation_plan.md) [1_prd_architecture_overview.md](agentic_development_docs/project_design_plan/1_prd_architecture_overview.md) [2_db_model.md](agentic_development_docs/project_design_plan/2_db_model.md) [2_db_model_extended.md](agentic_development_docs/project_design_plan/2_db_model_extended.md) [3_prd_api_design_req.md](agentic_development_docs/project_design_plan/3_prd_api_design_req.md) [4_prd_agent_design.md](agentic_development_docs/project_design_plan/4_prd_agent_design.md) [5_security_testing_deployment.md](agentic_development_docs/project_design_plan/5_security_testing_deployment.md) 
- If you have made implementation changes, update them back to the relavant project design plan files above.
- If you think there are more useful rules you can add to this rules1.md file while you are implementing, then feel free to add those rules to this file.


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
    - `agentic_development_docs/tools_documentation/langgraph_full_documentation.md`
    - `agentic_development_docs/tools_documentation/langgraph_brief_documentation.md`
  - For LiteLLM documentation, the documentation is available here:  `https://docs.litellm.ai/docs/`

- **Development communication**
  - If you have any question about the implementation, which is an important one, then you can stop and ask me before continuing the implementation.
  - For any communication or logging during development, write documents to `agentic_development_docs/agent_communication/`.
    - Examples include: assumptions made during implementation, design notes, and future work ideas.
    - Future work remaining like TODOs, you can update in agentic_development_docs/agent_communication/future_work.md
  - Feel free to create new markdown files when you want to log your progress, implementation or if you think it will be useful for continuing the implementation of the project.
  - If there are TODOs, add as comment in the same code file while you are implementing them.

- **Defaults and constraints**
  - Default to modern, stable, well-supported stacks and patterns.
  - Keep configuration and branding centralized and easily changeable via constants.
  - Any considerable deviation from these rules requires explicit approval.

- **Final Important rules on completion**
  - When you're done, self-critique your work until you're sure it's correct.
