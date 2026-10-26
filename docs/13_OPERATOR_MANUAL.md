# 13. PRODE Operator & Local Execution Manual

**System Version:** `1.0.0`  
**Sovereign Authority:** Zak (`EXEC-01`)  
**Authorized Spend Default:** **`$0.00 USD` (Hard Lock)**  
**Execution Runtime Twin:** [ZaxterLab](https://github.com/zakshub/zaxterlab)

---

## 1. Local Pull & Setup Instructions

PRODE is engineered with **zero external package dependencies** (runs on standard Python 3 + SQLite3 + vanilla HTML/CSS/JS).

```bash
# 1. Clone or pull the repository locally
git clone https://github.com/zakshub/prode.git
cd prode

# If already cloned, pull the latest main branch:
git pull --ff-only origin main
```

---

## 2. Running Verification & Hermetic Tests

```bash
# 1. Validate all blueprint docs, schemas, templates, and runtime files
python3 scripts/validate_workspace.py

# 2. Run the full hermetic unit & integration test suite
python3 -m unittest discover -s tests -v
```

---

## 3. Command-Line Interface (`python3 -m prode`)

```bash
# View company status, active version, revenue engines, and role/task metrics
python3 -m prode status

# List all 9 departments and all 69 specialist roles
python3 -m prode roles --department all

# Filter roles by a specific department (DEPT-01 through DEPT-09) or active-only
python3 -m prode roles --department DEPT-04
python3 -m prode roles --active-only

# Inspect the 5-Phase Roadmap, 15 Projects, 30 Milestones, and 90 Tasks
python3 -m prode roadmap --version all
python3 -m prode roadmap --version v1.0

# Simulate a project's topological task DAG through the Triple QC gates
python3 -m prode simulate --project PROJ-V1-01
python3 -m prode simulate --project all --clear-deposit

# Approve or reject a Sovereign Approval item as Zak (EXEC-01)
python3 -m prode approve --id APR-001 --decision APPROVED
```

---

## 4. Starting the Interactive Web Control Center

```bash
# Option A: Direct Foreground Server (Default http://127.0.0.1:8080)
python3 -m prode serve --host 127.0.0.1 --port 8080

# Option B: Managed Background Daemon Script
./scripts/run_prode.sh start
./scripts/run_prode.sh status
./scripts/run_prode.sh stop
```

Open **`http://127.0.0.1:8080`** in your browser to access:
1. **Executive Command & Revenue Engines:** Live KPIs, 3 Revenue Engines, 5-Point Opportunity Validator, and 4-Gate SaaS Spinout Validator.
2. **9 Functions & 69 Specialist Roles Inspector:** Filter by department, inspect governing brains and deliverables, and activate or suspend roles.
3. **5-Phase Roadmap (`v1.0` $\rightarrow$ `v5.0`):** Inspect all 15 Projects, 30 Milestones, and 90 Tasks, and execute any project DAG with one click.
4. **Knowledge Vault & Studio:** Author new PRDs, Proposals, ADRs, and Case Studies with full provenance tracking.
5. **Sovereign Approvals & Immutable Audit Log:** Approve/reject pending items as `EXEC-01 (Zak)` and inspect the SQLite audit trail.
6. **Light & Dark Companion Appearances:** Switch between *Architectural Drafting Paper* (Light) and *Precision Obsidian Lab* (Dark) modes, engineered in compliance with `zakshub/designer` and W3C WCAG 2.2 (`2.5.3 Label in Name` & `3.3.2 Labels or Instructions`).
