# Final GitHub Repo Structure & Codex Prompt Template

## 🗂 Final GitHub Repo Structure

```text
tax-lien-strategist/
├── README.md
├── docker-compose.yml
├── .gitignore
├── .env.example
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
│
├── docs/
│   ├── tax_lien_strategist_readme.md
│   ├── agi_agentic_system_whitepaper.md
│   ├── system_architecture_diagram.md
│   ├── formal_dfd_spec.md
│   ├── diagram_suite_agi_agentic_system.md
│   ├── level_3_deep_dive_deal_engine.md
│   ├── data_model_tax_lien_strategist.md
│   ├── analytical_extensions_tax_lien_strategist.md
│   ├── agi_layer_extensions_tax_lien_strategist.md
│   ├── implementation_artifacts_tax_lien_strategist.md
│   ├── reasoning_explorer_technical_implementation_plan.md
│   ├── reasoning_explorer_ui_design.md
│   ├── reasoning_explorer_user_stories.md
│   ├── azure_stack_and_deployment_plan_tax_lien_strategist.md
│   ├── gcp_stack_and_deployment_plan_tax_lien_strategist.md
│   ├── backend_api_specification.md
│   ├── business_rules_and_validation_spec.md
│   ├── background_jobs_and_scheduling.md
│   ├── agent_protocol_and_tools.md
│   ├── environment_variables_and_config_reference.md
│   ├── ci_cd_pipeline_specification.md
│   ├── local_development_guide.md
│   ├── database_schema_ddl.md
│   ├── seed_data_and_test_fixtures.md
│   ├── logging_monitoring_and_slos.md
│   ├── incident_response_runbooks.md
│   └── codex_build_instructions.md
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml/requirements.txt
│   └── app/
│       ├── main.py
│       ├── core/
│       ├── db/
│       │   └── migrations/
│       ├── models/
│       │   └── ai/
│       ├── schemas/
│       ├── repositories/
│       ├── services/
│       ├── ai/
│       ├── jobs/
│       └── api/
│           └── v1/
│               └── admin/reasoning_explorer_routes.py
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── router/
│       ├── config/
│       ├── components/
│       └── features/
│           ├── auth/
│           ├── investors/
│           ├── properties/
│           ├── liens/
│           ├── analysis/
│           ├── portfolios/
│           ├── documents/
│           ├── notifications/
│           └── reasoning-explorer/
│               ├── index.tsx
│               ├── EpisodesListPage.tsx
│               ├── EpisodeDetailPage.tsx
│               ├── LLMCallsPage.tsx
│               ├── DecisionsPage.tsx
│               ├── EntitiesPage.tsx
│               └── SettingsPage.tsx
│
├── infra/
│   ├── azure/
│   ├── gcp/
│   └── k8s/
│
├── scripts/
│   ├── seed_dev_data.py
│   ├── create_superuser.py
│   └── maintenance/
│       ├── rebuild_indexes.sql
│       └── adhoc_migrations.py
│
└── tests/
    ├── backend/
    └── frontend/
```

---

## 💬 Short Codex Prompt Template (Copy/Paste into Codespaces)

```text
You are GPT-5.1 Codex inside a GitHub Codespace for the “Tax Lien Strategist – AGI/Reasoning Explorer” project.

Goal: Implement the full application (backend, frontend, infra glue) using ONLY the specs in the /docs directory and the repository structure.

1. Read and internalize:
   - /docs/codex_build_instructions.md
   - /docs/backend_api_specification.md
   - /docs/business_rules_and_validation_spec.md
   - /docs/agent_protocol_and_tools.md
   - /docs/background_jobs_and_scheduling.md
   - /docs/data_model_tax_lien_strategist.md
   - /docs/database_schema_ddl.md
   - /docs/reasoning_explorer_technical_implementation_plan.md
   - /docs/reasoning_explorer_ui_design.md
   - /docs/reasoning_explorer_user_stories.md
   - /docs/environment_variables_and_config_reference.md
   - /docs/ci_cd_pipeline_specification.md
   - /docs/local_development_guide.md

2. Use the “Codex Build Instructions” as the master plan to:
   - Scaffold the backend FastAPI app in /backend/app with models, schemas, services, routes, AI/agent layer, and jobs.
   - Scaffold the React/TypeScript frontend in /frontend (including the Reasoning Explorer feature).
   - Add Alembic migrations and a seed script consistent with the DDL and seed fixtures.
   - Wire docker-compose.yml for backend, worker, frontend, Postgres, and Redis.
   - Add basic tests for core business rules and one end-to-end analysis + reasoning episode.

3. Do NOT invent business rules or API shapes that conflict with the docs. Where something is underspecified, choose a safe default and leave a clear TODO comment.

Start by confirming you’ve read the docs and then proceed step-by-step, narrating major milestones (repo scaffolding, backend skeleton, frontend skeleton, migrations, seed data, Reasoning Explorer wiring).
```

---

## ✔️ File successfully generated
