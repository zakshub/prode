# PRODE (Product Design & Engineering)
### Canonical Company OS Blueprint & Control Plane for an AI-Native Product Engineering & Interactive Technology Company

```
   ██████╗ ██████╗  ██████╗ ██████╗ ███████╗
   ██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔════╝
   ██████╔╝██████╔╝██║   ██║██║  ██║█████╗  
   ██╔═══╝ ██╔══██╗██║   ██║██║  ██║██╔══╝  
   ██║     ██║  ██║╚██████╔╝██████╔╝███████╗
   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝
   AI-NATIVE PRODUCT ENGINEERING & INTERACTIVE TECH
```

---

## 1. Executive Summary

**PRODE** is the canonical strategic blueprint, 69-role organizational registry, SOP governance engine, and local control plane for an **AI-Native Product Engineering & Interactive Technology Company**.

Rather than building six disconnected businesses—or trapping yourself in a speculative pure-play SaaS startup, a Figma-only design boutique, or a capital-burning game studio—PRODE unifies **Product Design (`zakshub/designer`), Visual Physics (`zakshub/studio`), AI-Native Software (`zakshub/codelift`), Real-Time 3D/Spatial Tech (`zakshub/bob`), and Cyber-Physical Electronic Engineering** under one coherent operating system.

While **[ZaxterLab](https://github.com/zakshub/zaxterlab)** serves as the adaptive multi-agent execution runtime, **PRODE** governs company strategy, commercial revenue engines, the 9 functional departments & 69 specialist roles, the 50/25/25 cash-flow lock, the `$0.00` spend guard, and the 5-Phase progression from `v1.0` to `v5.0`.

---

## 2. Quick Start (Pull & Run Locally)

PRODE runs 100% offline using standard Python 3 + SQLite3 with **zero external package dependencies** and a hard-locked **`$0.00 USD`** spend boundary.

```bash
# 1. Clone or pull the repository
git clone https://github.com/zakshub/prode.git
cd prode

# 2. Validate workspace & run the 10-part hermetic test suite
python3 scripts/validate_workspace.py
python3 -m unittest discover -s tests -v

# 3. Inspect Company OS status, 9 Functions & 69 Roles, and Roadmap (v1.0 -> v5.0)
python3 -m prode status
python3 -m prode roles --department all
python3 -m prode roadmap --version all

# 4. Simulate any project's Task DAG through Triple QC gates
python3 -m prode simulate --project PROJ-V1-01

# 5. Launch the interactive Web Control Center (http://127.0.0.1:8080)
python3 -m prode serve --host 127.0.0.1 --port 8080
# Or run in background via daemon script:
./scripts/run_prode.sh start
```

---

## 3. Repository Documentation & Runtime Map

| File / Module | Purpose & Scope |
| :--- | :--- |
| **[`docs/01_COMPANY_IDENTITY.md`](./docs/01_COMPANY_IDENTITY.md)** | Mission, vision, core values, positioning quadrant, and the "Synthesist" thesis. |
| **[`docs/02_BUSINESS_MODEL.md`](./docs/02_BUSINESS_MODEL.md)** | The 3 complementary revenue paths (`REV-01` Client Services, `REV-02` Productized Packages, `REV-03` Owned SaaS/IP). |
| **[`docs/03_MARKET_STRATEGY.md`](./docs/03_MARKET_STRATEGY.md)** | Target customer archetypes, 5-Point Validation Filter, and competitive moats. |
| **[`docs/04_ORGANIZATION_AND_ROLES.md`](./docs/04_ORGANIZATION_AND_ROLES.md)** | All **9 Departments** and **69 Specialist Roles** (`7+8+7+9+9+8+8+7+6`), RACI, and authority boundaries. |
| **[`docs/05_AI_WORKFORCE_ARCHITECTURE.md`](./docs/05_AI_WORKFORCE_ARCHITECTURE.md)** | Multi-agent cognitive mesh, specialist sandboxes, and ZaxterLab execution bridge. |
| **[`docs/06_OPERATING_PROCEDURES.md`](./docs/06_OPERATING_PROCEDURES.md)** | SOPs for Lead-to-Contract, Sprint Zero, Core Engineering, Triple QC, and Release. |
| **[`docs/07_PRODUCT_ENGINEERING_FRAMEWORK.md`](./docs/07_PRODUCT_ENGINEERING_FRAMEWORK.md)** | 6-phase engineering lifecycle from Discovery to CodeLift AST build and deployment. |
| **[`docs/08_CYBER_PHYSICAL_ROADMAP.md`](./docs/08_CYBER_PHYSICAL_ROADMAP.md)** | Electronic engineering progression: Digital twins $\rightarrow$ ESP32/STM32 $\rightarrow$ TinyML $\rightarrow$ Robotics. |
| **[`docs/09_KNOWLEDGE_AND_ARTIFACTS.md`](./docs/09_KNOWLEDGE_AND_ARTIFACTS.md)** | Institutional Knowledge Vault, ADR protocols, and evidence-backed records. |
| **[`docs/10_FINANCIAL_AND_RISK_CONTROLS.md`](./docs/10_FINANCIAL_AND_RISK_CONTROLS.md)** | Hard `$0.00` spend guardrails, IP ring-fencing, and 50/25/25 cash-flow locks. |
| **[`docs/11_IMPLEMENTATION_ROADMAP.md`](./docs/11_IMPLEMENTATION_ROADMAP.md)** | Strategic progression across Phases 1 to 5. |
| **[`docs/12_MASTER_EXECUTION_PLAN.md`](./docs/12_MASTER_EXECUTION_PLAN.md)** | Complete breakdown of **5 Versions (`v1.0`–`v5.0`)**, **15 Projects**, **30 Milestones**, and **90 Tasks**. |
| **[`docs/13_OPERATOR_MANUAL.md`](./docs/13_OPERATOR_MANUAL.md)** | Step-by-step CLI, Web Control Center, API, and local operation manual. |
| **[`prode/`](./prode/)** | Executable Python/SQLite Company OS engine, CLI (`prode/cli.py`), API (`prode/server.py`), and Light/Dark Companion Web UI (`prode/ui/index.html`). |
| **[`schemas/role_taxonomy.json`](./schemas/role_taxonomy.json)** | Machine-readable JSON catalog of all 9 departments and 69 specialist roles. |
| **[`tests/test_prode.py`](./tests/test_prode.py)** | Hermetic unit & integration test suite verifying all 69 roles, 90 tasks, spend locks, and QC gates. |
