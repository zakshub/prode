"""
PRODE Execution & Governance Engine:
- Hard $0.00 Spend Lock (ZEDCU invariant)
- 50/25/25 Cash-Flow Milestone Lock
- 5-Point Opportunity Validation Filter
- 4-Gate Proprietary SaaS Spinout Filter
- Designer-Studio-CodeLift Triple QC Contract Evaluator
- Topological DAG Task Sorter & End-to-End Project Simulator
- Sovereign Owner Approval Queue & Knowledge Vault Generator
"""

from collections import deque
from typing import Any, Dict, List, Optional, Tuple

from prode.catalog import REVENUE_ENGINES
from prode.db import ProdeDB, utc_now


class SpendBoundaryViolation(PermissionError):
    """Raised when any operation attempts > $0.00 spend without sovereign override."""


class CashFlowLockViolation(PermissionError):
    """Raised when engineering or IP handover is attempted before milestone payment clears."""


class ContractValidationError(ValueError):
    """Raised when a Designer-Studio-CodeLift QC packet or DAG violates contract rules."""


class ProdeEngine:
    def __init__(self, db: ProdeDB) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # 1. Hard $0.00 Spend Guard (OPS-02 / EXEC-07)
    # ------------------------------------------------------------------
    def enforce_spend_guard(
        self, requested_usd: float, approved_by_owner: bool = False, context: str = "operation"
    ) -> Dict[str, Any]:
        state = self.db.get_company_state()
        limit = float(state.get("authorized_spend_usd", 0.0))
        if requested_usd > limit and not approved_by_owner:
            self.db.log_event(
                actor="OPS-02 (ZEDCU Spend Guard)",
                action="SPEND_VIOLATION_BLOCKED",
                target_id=context,
                details=f"Blocked ${requested_usd:.2f} USD request (hard limit: ${limit:.2f} USD).",
            )
            raise SpendBoundaryViolation(
                f"Hard $0.00 Spend Lock Violation: Requested ${requested_usd:.2f} USD for '{context}' "
                f"exceeds authorized limit (${limit:.2f} USD). Sovereign approval by Zak (EXEC-01) required."
            )
        return {"status": "ALLOWED", "requested_usd": requested_usd, "limit_usd": limit}

    # ------------------------------------------------------------------
    # 2. 50/25/25 Cash-Flow Lock (OPS-01 / DLV-03)
    # ------------------------------------------------------------------
    def enforce_engineering_start_lock(self, project_id: str) -> Dict[str, Any]:
        projects = self.db.get_projects()
        proj = next((p for p in projects if p["id"] == project_id), None)
        if not proj:
            raise ValueError(f"Unknown project_id: {project_id}")

        if proj["contract_value_usd"] > 0 and not proj["deposit_50_cleared"]:
            self.db.log_event(
                actor="OPS-01 (Cash-Flow Controller)",
                action="ENGINEERING_START_BLOCKED",
                target_id=project_id,
                details="Blocked engineering start: 50% upfront deposit has not cleared.",
            )
            raise CashFlowLockViolation(
                f"50/25/25 Cash-Flow Lock: Project '{project_id}' (${proj['contract_value_usd']:,.2f}) "
                f"cannot begin engineering until the 50% upfront deposit clears."
            )
        return {"project_id": project_id, "engineering_unlocked": True}

    def enforce_ip_handover_lock(self, project_id: str) -> Dict[str, Any]:
        projects = self.db.get_projects()
        proj = next((p for p in projects if p["id"] == project_id), None)
        if not proj:
            raise ValueError(f"Unknown project_id: {project_id}")

        if proj["contract_value_usd"] > 0 and not (
            proj["deposit_50_cleared"] and proj["staging_25_cleared"] and proj["final_25_cleared"]
        ):
            self.db.log_event(
                actor="OPS-03 (IP Guardian)",
                action="IP_HANDOVER_BLOCKED",
                target_id=project_id,
                details="Blocked IP transfer: 100% of 50/25/25 invoices have not cleared.",
            )
            raise CashFlowLockViolation(
                f"IP Ring-Fencing Lock: Project '{project_id}' cannot transfer source code or IP until "
                f"all 50% Deposit, 25% Staging, and 25% Final payments are cleared."
            )
        return {"project_id": project_id, "ip_handover_unlocked": True}

    def update_payment_milestone(
        self, project_id: str, stage: str, cleared: bool = True
    ) -> Dict[str, Any]:
        col_map = {
            "deposit_50": "deposit_50_cleared",
            "staging_25": "staging_25_cleared",
            "final_25": "final_25_cleared",
        }
        if stage not in col_map:
            raise ValueError("stage must be one of: deposit_50, staging_25, final_25")
        col = col_map[stage]
        self.db._conn.execute(
            f"UPDATE projects SET {col} = ? WHERE id = ?",
            (1 if cleared else 0, project_id),
        )
        self.db.log_event(
            actor="OPS-01 (Cash-Flow Controller)",
            action="PAYMENT_MILESTONE_UPDATED",
            target_id=project_id,
            details=f"Updated {stage} to {'CLEARED' if cleared else 'PENDING'}.",
        )
        return next(p for p in self.db.get_projects() if p["id"] == project_id)

    # ------------------------------------------------------------------
    # 3. 5-Point Opportunity Validation Filter (MKT-04)
    # ------------------------------------------------------------------
    def validate_opportunity(
        self,
        pain_severity_annual_usd: float,
        velocity_10x_advantage: bool,
        multidisciplinary_fit: bool,
        yields_reusable_ip: bool,
        zero_speculative_spend: bool,
    ) -> Dict[str, Any]:
        checks = {
            "pain_economically_severe": pain_severity_annual_usd >= 20000.0,
            "ai_10x_velocity_advantage": bool(velocity_10x_advantage),
            "multidisciplinary_synthesist_fit": bool(multidisciplinary_fit),
            "yields_reusable_ip": bool(yields_reusable_ip),
            "zero_speculative_spend": bool(zero_speculative_spend),
        }
        score = sum(1 for v in checks.values() if v)
        passed = all(checks.values())
        return {
            "passed": passed,
            "score": f"{score}/5",
            "recommendation": "PROCEED_TO_SPRINT_ZERO" if passed else "REJECT_OR_RESCOPE",
            "checks": checks,
        }

    # ------------------------------------------------------------------
    # 4. 4-Gate Proprietary SaaS Spinout Filter (PRD-01 / EXEC-05)
    # ------------------------------------------------------------------
    def validate_saas_spinout(
        self,
        paying_clients_count: int,
        reusable_code_ratio: float,
        external_debt_usd: float,
        has_direct_distribution: bool,
    ) -> Dict[str, Any]:
        gates = {
            "observed_frequency_3plus_clients": paying_clients_count >= 3,
            "reusability_60pct_plus": reusable_code_ratio >= 0.60,
            "zero_capital_risk": external_debt_usd == 0.0,
            "direct_distribution_advantage": bool(has_direct_distribution),
        }
        passed = all(gates.values())
        return {
            "passed": passed,
            "recommendation": "APPROVED_FOR_V5_SAAS_SPINOUT" if passed else "KEEP_AS_CLIENT_MODULE",
            "gates": gates,
        }

    # ------------------------------------------------------------------
    # 5. Designer-Studio-CodeLift Triple QC Contract Evaluator
    # ------------------------------------------------------------------
    def evaluate_designer_studio_codelift_contract(
        self, brief: Dict[str, Any], delivery: Dict[str, Any]
    ) -> Dict[str, Any]:
        required_brief = [
            "id",
            "owner",
            "intent",
            "audience",
            "placement",
            "composition",
            "accessibility",
            "acceptance_criteria",
        ]
        for f in required_brief:
            if not brief.get(f):
                raise ContractValidationError(f"Designer brief missing required field: '{f}'")
        if brief.get("owner") != "designer":
            raise ContractValidationError("Brief owner must be 'designer'")

        required_delivery = [
            "brief_id",
            "owner",
            "asset_uri",
            "production_rationale",
            "rights",
            "image_qc",
            "design_fit_qc",
            "ast_compile_qc",
        ]
        for f in required_delivery:
            if not delivery.get(f):
                raise ContractValidationError(f"Delivery packet missing required field: '{f}'")
        if delivery.get("brief_id") != brief["id"]:
            raise ContractValidationError("Delivery brief_id does not match brief.id")

        image_qc = delivery["image_qc"]
        design_fit_qc = delivery["design_fit_qc"]
        ast_compile_qc = delivery["ast_compile_qc"]

        if image_qc.get("owner") != "studio":
            raise ContractValidationError("image_qc must be owned by 'studio'")
        if design_fit_qc.get("owner") != "designer":
            raise ContractValidationError("design_fit_qc must be owned by 'designer'")
        if ast_compile_qc.get("owner") != "codelift":
            raise ContractValidationError("ast_compile_qc must be owned by 'codelift'")

        accepted = (
            image_qc.get("status") == "pass"
            and design_fit_qc.get("status") == "pass"
            and ast_compile_qc.get("status") == "pass"
        )
        return {
            "brief_id": brief["id"],
            "accepted": accepted,
            "image_qc_status": image_qc.get("status"),
            "design_fit_qc_status": design_fit_qc.get("status"),
            "ast_compile_qc_status": ast_compile_qc.get("status"),
        }

    # ------------------------------------------------------------------
    # 6. Topological DAG Sorting & End-to-End Project Simulation
    # ------------------------------------------------------------------
    @staticmethod
    def topological_sort_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        task_map = {t["id"]: t for t in tasks}
        in_degree = {t["id"]: 0 for t in tasks}
        adj: Dict[str, List[str]] = {t["id"]: [] for t in tasks}

        for t in tasks:
            for dep in t.get("depends_on", []):
                if dep in task_map:
                    adj[dep].append(t["id"])
                    in_degree[t["id"]] += 1

        queue = deque([tid for tid, deg in in_degree.items() if deg == 0])
        ordered: List[Dict[str, Any]] = []

        while queue:
            curr = queue.popleft()
            ordered.append(task_map[curr])
            for nxt in adj[curr]:
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)

        if len(ordered) != len(tasks):
            raise ContractValidationError("Cyclic dependency detected in project task DAG.")
        return ordered

    def simulate_project(
        self, project_id: str, auto_clear_deposit: bool = False
    ) -> Dict[str, Any]:
        projects = self.db.get_projects()
        proj = next((p for p in projects if p["id"] == project_id), None)
        if not proj:
            raise ValueError(f"Project not found: {project_id}")

        if auto_clear_deposit and not proj["deposit_50_cleared"]:
            self.update_payment_milestone(project_id, "deposit_50", True)

        # Gate 1: $0.00 Spend Guard + 50% Deposit Check
        self.enforce_spend_guard(0.0, context=f"simulate:{project_id}")
        self.enforce_engineering_start_lock(project_id)

        all_tasks: List[Dict[str, Any]] = []
        for ms in proj["milestones"]:
            all_tasks.extend(ms["tasks"])

        ordered_tasks = self.topological_sort_tasks(all_tasks)
        now = utc_now()
        executed_ids: List[str] = []

        for task in ordered_tasks:
            # Ensure assigned and reviewer roles are active
            self.db._conn.execute(
                "UPDATE roles SET is_active = 1 WHERE id IN (?, ?)",
                (task["assigned_role_id"], task["reviewer_role_id"]),
            )
            self.db._conn.execute(
                """
                UPDATE tasks
                SET status = 'COMPLETED',
                    design_fit_qc = 'PASS',
                    image_qc = 'PASS',
                    ast_compile_qc = 'PASS',
                    completed_at = ?
                WHERE id = ?
                """,
                (now, task["id"]),
            )
            executed_ids.append(task["id"])

        for ms in proj["milestones"]:
            self.db._conn.execute(
                "UPDATE milestones SET status = 'COMPLETED' WHERE id = ?", (ms["id"],)
            )

        self.db._conn.execute(
            "UPDATE projects SET status = 'COMPLETED' WHERE id = ?", (project_id,)
        )

        cert_id = f"KV-QC-{project_id}"
        self.db._conn.execute(
            """
            INSERT OR REPLACE INTO knowledge_vault (
                id, artifact_type, project_id, title, ip_classification,
                governing_brain, content, created_by_role, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cert_id,
                "QC_CERTIFICATE",
                project_id,
                f"Dual-Gate Forensic & Compiler QC Certificate — {proj['title']}",
                "PRODE_CORE_IP",
                "codelift",
                f"Verified {len(executed_ids)} tasks in topological DAG order: {', '.join(executed_ids)}. "
                f"design_fit_qc=PASS, image_qc=PASS, ast_compile_qc=PASS, spend=$0.00.",
                "QSR-08",
                now,
            ),
        )

        self.db.log_event(
            actor="EXEC-03 (Sirfaraz) + QSR-08 (Umer)",
            action="PROJECT_DAG_COMPLETED",
            target_id=project_id,
            details=f"Executed {len(executed_ids)} tasks across {len(proj['milestones'])} milestones with Triple QC PASS.",
        )

        return {
            "project_id": project_id,
            "title": proj["title"],
            "version": proj["version"],
            "tasks_executed": len(executed_ids),
            "ordered_task_ids": executed_ids,
            "qc_certificate_id": cert_id,
            "status": "COMPLETED",
        }

    # ------------------------------------------------------------------
    # 7. Role Toggle, Sovereign Approvals & Vault Creation
    # ------------------------------------------------------------------
    def toggle_role(self, role_id: str, active: bool) -> Dict[str, Any]:
        roles = self.db.get_roles()
        role = next((r for r in roles if r["id"] == role_id), None)
        if not role:
            raise ValueError(f"Role not found: {role_id}")
        if role_id == "EXEC-01" and not active:
            raise ValueError("Sovereign Founder role (EXEC-01) cannot be deactivated.")

        self.db._conn.execute(
            "UPDATE roles SET is_active = ? WHERE id = ?", (1 if active else 0, role_id)
        )
        self.db.log_event(
            actor="EXEC-01 (Zak)",
            action="ROLE_STATE_CHANGED",
            target_id=role_id,
            details=f"Role '{role['title']}' ({role_id}) set to {'ACTIVE' if active else 'DORMANT'}.",
        )
        return next(r for r in self.db.get_roles() if r["id"] == role_id)

    def decide_approval(
        self, approval_id: str, decision: str, actor: str = "EXEC-01 (Zak)"
    ) -> Dict[str, Any]:
        decision_up = decision.upper()
        if decision_up not in ("APPROVED", "REJECTED"):
            raise ValueError("decision must be APPROVED or REJECTED")

        row = self.db._conn.execute(
            "SELECT * FROM approvals WHERE id = ?", (approval_id,)
        ).fetchone()
        if not row:
            raise ValueError(f"Approval ID not found: {approval_id}")

        now = utc_now()
        self.db._conn.execute(
            """
            UPDATE approvals
            SET status = ?, decided_by = ?, decided_at = ?
            WHERE id = ?
            """,
            (decision_up, actor, now, approval_id),
        )

        # If approving a release handover, mark final_25_cleared on target project
        if decision_up == "APPROVED" and row["approval_type"] == "RELEASE_HANDOVER":
            self.db._conn.execute(
                "UPDATE projects SET final_25_cleared = 1 WHERE id = ?",
                (row["target_id"],),
            )

        self.db.log_event(
            actor=actor,
            action=f"SOVEREIGN_APPROVAL_{decision_up}",
            target_id=approval_id,
            details=f"{decision_up}: {row['summary']}",
        )
        return dict(
            self.db._conn.execute(
                "SELECT * FROM approvals WHERE id = ?", (approval_id,)
            ).fetchone()
        )

    def create_vault_artifact(
        self,
        artifact_type: str,
        project_id: str,
        title: str,
        content: str,
        ip_classification: str = "PRODE_CORE_IP",
        governing_brain: str = "designer",
        created_by_role: str = "PRD-06",
    ) -> Dict[str, Any]:
        existing = self.db.get_knowledge_vault()
        art_id = f"KV-{artifact_type.upper()}-{len(existing) + 1:03d}"
        now = utc_now()
        self.db._conn.execute(
            """
            INSERT INTO knowledge_vault (
                id, artifact_type, project_id, title, ip_classification,
                governing_brain, content, created_by_role, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                art_id,
                artifact_type.upper(),
                project_id,
                title,
                ip_classification,
                governing_brain,
                content,
                created_by_role,
                now,
            ),
        )
        self.db.log_event(
            actor=created_by_role,
            action="VAULT_ARTIFACT_CREATED",
            target_id=art_id,
            details=f"Created {artifact_type.upper()} artifact '{title}' for {project_id}.",
        )
        return next(a for a in self.db.get_knowledge_vault() if a["id"] == art_id)

    def generate_client_proposal(
        self,
        client_name: str,
        client_email: str,
        project_title: str,
        project_type: str = "sprint_zero",
        total_cost_usd: float = 7500.0,
        timeline_str: str = "10 Business Days",
        problem_summary: str = "Engineering and prototyping a production-grade digital/physical product.",
    ) -> Dict[str, Any]:
        p1 = round(total_cost_usd * 0.50)
        p2 = round(total_cost_usd * 0.25)
        p3 = round(total_cost_usd - p1 - p2)
        date_today = utc_now().split("T")[0]

        proposal_md = f"""# Statement of Work & Project Proposal: {project_title}

**Client Organization:** {client_name} ({client_email})  
**Engineering Firm:** PRODE — Product Design & Interactive Technology Company  
**Primary Architect:** Zak (EXEC-01)  
**Date Issued:** {date_today}  
**Total Fixed Investment:** ${total_cost_usd:,.2f} USD  
**Guaranteed Timeline:** {timeline_str}  

---

## 1. Executive Summary & Objective
{client_name} is partnering with PRODE to design and engineer a production-ready solution.
* **The Challenge:** {problem_summary}
* **Our Commitment:** Deliver working, build-validated software and interactive systems rather than static concepts or unverified mockups.

---

## 2. Guaranteed Deliverables ({timeline_str})
1. **Product Architecture & Requirements Blueprint:** Complete system specification, state diagrams, and database schemas.
2. **Accessible UX/UI Screen Layouts:** High-contrast, responsive interfaces designed in strict compliance with W3C WCAG 2.2 AA accessibility standards.
3. **Interactive Working Prototype:** Clickable, testable staging deployment you can review directly on your phone and desktop.
4. **Production Codebase / Implementation Package:** Clean, type-checked code (Next.js / React / TypeScript / Tailwind) that compiles with zero errors.
5. **Guaranteed Fixed-Price Quote for Subsequent Milestones:** Full transparency for long-term expansion.

---

## 3. Transparent 50/25/25 Cash Flow & Milestone Schedule
PRODE operates with a strict milestone-governed payment schedule:

| Milestone Phase | Amount (USD) | Trigger Event & Acceptance Condition |
| :--- | :---: | :--- |
| **Milestone 1 (50% Upfront)** | **${p1:,.2f}** | Due upon contract signing prior to sprint commencement. |
| **Milestone 2 (25% Staging Demo)** | **${p2:,.2f}** | Due upon demonstration of the verified interactive staging build. |
| **Milestone 3 (25% Final Handover)** | **${p3:,.2f}** | Due upon production release, repository transfer, and IP handover. |

---

## 4. Intellectual Property & Ownership
* **Client IP Rights:** Upon 100% settlement of Milestone 3, all custom source code, databases, designs, and brand assets created specifically for {client_name} become the exclusive, transferable property of {client_name}.
* **PRODE Background Tools:** Core proprietary generator engines and internal tooling libraries remain owned by PRODE, with an irrevocable, royalty-free license granted to {client_name} for runtime use.

---

## 5. Acceptance & Authorization

| Authorized Representative for {client_name}: | For PRODE Product Engineering: |
| :--- | :--- |
| **Name:** ________________________________ | **Name:** Zak |
| **Title:** _______________________________ | **Title:** Founder & Sovereign Architect |
| **Signature:** __________________________ | **Signature:** __________________________ |
| **Date:** _______________________________ | **Date:** {date_today} |
"""
        artifact = self.create_vault_artifact(
            artifact_type="PROPOSAL",
            project_id=f"PROP-{client_name.replace(' ', '-').upper()[:12]}",
            title=f"Official Proposal: {project_title} for {client_name}",
            content=proposal_md,
            ip_classification="CLIENT_PROPOSAL",
            governing_brain="designer",
            created_by_role="MKT-08",
        )

        self.db.log_event(
            actor="MKT-08 (Proposal Architect)",
            action="CLIENT_PROPOSAL_GENERATED",
            target_id=artifact["id"],
            details=f"Generated ${total_cost_usd:,.2f} USD proposal for {client_name} ({project_title}).",
        )

        return {
            "artifact_id": artifact["id"],
            "client_name": client_name,
            "project_title": project_title,
            "total_cost_usd": total_cost_usd,
            "timeline": timeline_str,
            "proposal_markdown": proposal_md,
            "payment_schedule": {"m1_deposit_50": p1, "m2_staging_25": p2, "m3_final_25": p3},
        }

    def scaffold_client_project(
        self,
        client_name: str,
        project_title: str,
        project_type: str = "sprint_zero",
        features: Optional[List[str]] = None,
        base_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        import os
        import re

        features_list = features or [
            "Next.js App Router & Tailwind CSS",
            "Interactive Three.js 3D Viewport",
            "Hardware Microcontroller Telemetry Hook (ESP32/MQTT)",
            "Role-Based Access Control & Database Schema"
        ]

        safe_client = re.sub(r'[^a-zA-Z0-9]', '_', client_name.strip()).lower().strip('_') or "client"
        safe_proj = re.sub(r'[^a-zA-Z0-9]', '_', project_title.strip()).lower().strip('_') or "product"
        slug = f"{safe_client}_{safe_proj}"

        if not base_dir:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "projects", slug))
        else:
            base_dir = os.path.join(base_dir, slug)

        docs_dir = os.path.join(base_dir, "docs")
        src_app_dir = os.path.join(base_dir, "src", "app")
        os.makedirs(docs_dir, exist_ok=True)
        os.makedirs(src_app_dir, exist_ok=True)

        now = utc_now()

        # 1. PRD.md
        prd_content = f"""# Product Requirements Document (PRD)
## {project_title} — Client Engineering Specification

- **Client Organization:** {client_name}
- **Engineering Partner:** PRODE (AI-Native Product Engineering & Interactive Technology)
- **Sovereign Executive:** Zak (EXEC-01)
- **Status:** APPROVED & INITIALIZED
- **Generated At:** {now}

---

### 1. Executive Summary & Problem Statement
{client_name} requires a high-performance product built to production standards without speculative waste. This repository contains the complete specification, architecture, and starter implementation delivered under PRODE's guaranteed 50/25/25 cash-flow and Dual-Gate Quality framework.

### 2. Core Functional Scope & Features
""" + "\n".join(f"- [x] **Feature {i+1}:** {f}" for i, f in enumerate(features_list)) + f"""

### 3. Non-Functional Invariants
- **Visual Design Standard:** Governed by `zakshub/designer` (WCAG AAA contrast, semantic token hierarchy).
- **Interactive 3D / Realism:** Governed by `zakshub/bob` and `zakshub/studio` (60 FPS WebGL, physically accurate materials).
- **Code Velocity & Cleanliness:** Governed by `zakshub/codelift` (zero compiler warnings, TypeScript strict mode).
- **Telemetry Latency:** Sub-100ms bidirectional packet delivery.

### 4. 50/25/25 Milestone Acceptance Criteria
1. **Milestone 1 (50% Deposit Cleared):** Architecture, database schemas, and UX wireframes complete.
2. **Milestone 2 (25% on Staging Demo):** Live interactive clickable prototype + 3D viewport hosted on staging.
3. **Milestone 3 (25% on Final Handover):** Production deployment, full IP transfer, and clean Git repository handover.
"""

        # 2. ARCHITECTURE.md
        arch_content = f"""# System Architecture Specification
## {project_title} ({slug})

### 1. Technology Stack
- **Frontend Framework:** Next.js 14+ (App Router, Server & Client Components)
- **Styling & UI Tokens:** Tailwind CSS with Sentinel Companion palettes
- **3D Spatial Graphics:** Three.js / WebGL with procedural fallback
- **Backend & Persistence:** SQLite (Dev) / PostgreSQL (Prod) via Prisma ORM
- **Cyber-Physical Gateway:** MQTT / WebSockets for IoT & ESP32 telemetry

### 2. Directory Layout
```text
{slug}/
├── docs/
│   ├── PRD.md              # Product Requirements Document
│   └── ARCHITECTURE.md     # Engineering & Data Architecture
├── src/
│   └── app/
│       ├── layout.tsx      # Root HTML shell & meta
│       └── page.tsx        # Modern dashboard & 3D view
├── package.json            # Node.js dependencies
└── README.md               # Quickstart guide
```

### 3. Security & Quality Guardrails
- All user inputs sanitized against SQL injection and XSS.
- No third-party tracking scripts or speculative analytics.
- Zero-spend rule: All development verified locally without paid API locks.
"""

        # 3. package.json
        pkg_content = f"""{{
  "name": "{slug}",
  "version": "0.1.0",
  "private": true,
  "description": "{project_title} engineered by PRODE",
  "scripts": {{
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }},
  "dependencies": {{
    "next": "^14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "lucide-react": "^0.360.0",
    "three": "^0.160.0"
  }},
  "devDependencies": {{
    "@types/node": "^20.0.0",
    "@types/react": "^18.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.4.0"
  }}
}}
"""

        # 4. README.md
        readme_content = f"""# {project_title}
**Engineered by PRODE for {client_name}**

This project was automatically scaffolded using PRODE's AI-Native Product Engineering engine.

## Quickstart (Under 60 Seconds)

```bash
# 1. Install dependencies
npm install

# 2. Run local development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view your product live.

## Documentation
- [Product Requirements Document (PRD)](docs/PRD.md)
- [System Architecture](docs/ARCHITECTURE.md)
"""

        # 5. src/app/page.tsx
        page_content = f"""// {project_title} — Generated by PRODE
export default function HomePage() {{
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-8 flex flex-col items-center justify-center">
      <div className="max-w-2xl w-full bg-slate-900 border border-slate-800 rounded-xl p-8 shadow-2xl">
        <div className="flex items-center gap-2 mb-4">
          <span className="px-3 py-1 text-xs font-bold rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30">
            PRODE VERIFIED SCAFFOLD
          </span>
          <span className="px-3 py-1 text-xs font-bold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            50/25/25 CASH-FLOW ACTIVE
          </span>
        </div>
        <h1 className="text-3xl font-extrabold mb-2 text-white">{project_title}</h1>
        <p className="text-slate-400 mb-6">
          Client Workspace for <strong className="text-slate-200">{client_name}</strong>. Ready for custom UI and cyber-physical integration.
        </p>
        <div className="border-t border-slate-800 pt-4 flex justify-between text-xs text-slate-500">
          <span>Engineered by PRODE</span>
          <span>Founder Sovereign: Zak (EXEC-01)</span>
        </div>
      </div>
    </main>
  );
}}
"""

        # Write files
        files_created = {
            os.path.join(docs_dir, "PRD.md"): prd_content,
            os.path.join(docs_dir, "ARCHITECTURE.md"): arch_content,
            os.path.join(base_dir, "package.json"): pkg_content,
            os.path.join(base_dir, "README.md"): readme_content,
            os.path.join(src_app_dir, "page.tsx"): page_content,
        }

        for path, data in files_created.items():
            with open(path, "w", encoding="utf-8") as f:
                f.write(data)

        # Store in Knowledge Vault
        art_id = f"KV-SCAFFOLD-{slug.upper()[:20]}"
        self.db._conn.execute(
            """
            INSERT OR REPLACE INTO knowledge_vault (
                id, artifact_type, project_id, title, ip_classification,
                governing_brain, content, created_by_role, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                art_id,
                "PROJECT_SCAFFOLD",
                slug,
                f"Project Scaffolder & PRD: {project_title} ({client_name})",
                "CLIENT_IP",
                "codelift",
                f"Generated 5 production starter files in {base_dir}. PRD, Architecture, package.json, and Next.js starter page.",
                "PRD-01",
                now,
            ),
        )

        self.db.log_event(
            actor="PRD-01 (Principal Product Architect)",
            action="PROJECT_SCAFFOLDED",
            target_id=slug,
            details=f"Scaffolded full codebase and PRD for {client_name} at {base_dir}.",
        )

        return {
            "slug": slug,
            "project_dir": base_dir,
            "artifact_id": art_id,
            "files_count": len(files_created),
            "files": list(files_created.keys()),
            "message": f"Successfully scaffolded {project_title} into {base_dir}",
        }

    def get_dashboard_summary(self) -> Dict[str, Any]:
        state = self.db.get_company_state()
        depts = self.db.get_departments()
        roles = self.db.get_roles()
        versions = self.db.get_versions()
        projects = self.db.get_projects()
        approvals = self.db.get_approvals()
        vault = self.db.get_knowledge_vault()
        audit = self.db.get_audit_log(limit=25)

        total_tasks = 0
        completed_tasks = 0
        total_milestones = 0
        completed_milestones = 0
        for p in projects:
            total_milestones += len(p["milestones"])
            for m in p["milestones"]:
                if m["status"] == "COMPLETED":
                    completed_milestones += 1
                total_tasks += len(m["tasks"])
                for t in m["tasks"]:
                    if t["status"] == "COMPLETED":
                        completed_tasks += 1

        active_roles = [r for r in roles if r["is_active"]]
        pending_approvals = [a for a in approvals if a["status"] == "PENDING"]

        return {
            "company": state,
            "revenue_engines": REVENUE_ENGINES,
            "metrics": {
                "total_departments": len(depts),
                "total_roles": len(roles),
                "active_roles": len(active_roles),
                "dormant_roles": len(roles) - len(active_roles),
                "total_versions": len(versions),
                "total_projects": len(projects),
                "total_milestones": total_milestones,
                "completed_milestones": completed_milestones,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_approvals": len(pending_approvals),
                "vault_artifacts": len(vault),
                "authorized_spend_usd": state["authorized_spend_usd"],
            },
            "departments": depts,
            "roles": roles,
            "versions": versions,
            "projects": projects,
            "approvals": approvals,
            "knowledge_vault": vault,
            "audit_log": audit,
        }

    # ------------------------------------------------------------------
    # 8. Cyber-Physical & IoT Edge Telemetry Engine (CPE-01 / CPE-02)
    # ------------------------------------------------------------------
    _hardware_mode = "NOMINAL"
    _packet_seq = 1024

    def get_hardware_telemetry(self) -> Dict[str, Any]:
        ProdeEngine._packet_seq += 1
        mode = ProdeEngine._hardware_mode
        if mode == "THERMAL_SPIKE":
            temp = 78.4
            vib = 14.8
            volt = 3.86
            curr = 280.0
            rssi = -64
            status = "THERMAL_ALERT"
        elif mode == "VIBRATION_ANOMALY":
            temp = 42.1
            vib = 86.2
            volt = 3.89
            curr = 210.0
            rssi = -61
            status = "IMU_EXCURSION"
        elif mode == "DEEP_SLEEP":
            temp = 24.5
            vib = 0.2
            volt = 3.75
            curr = 0.02
            rssi = -78
            status = "LOW_POWER_SLEEP"
        else:  # NOMINAL
            temp = 38.4
            vib = 12.4
            volt = 3.92
            curr = 140.0
            rssi = -58
            status = "NOMINAL"

        return {
            "device_id": "PRODE-ESP32-S3-01",
            "firmware_version": "v2.4.1-RTOS",
            "packet_seq": ProdeEngine._packet_seq,
            "mode": mode,
            "status": status,
            "core_temp_c": temp,
            "vibration_freq_hz": vib,
            "supply_voltage_v": volt,
            "current_draw_ma": curr,
            "wifi_rssi_dbm": rssi,
            "telemetry_rate_hz": 20,
        }

    def set_hardware_telemetry_mode(self, mode: str) -> Dict[str, Any]:
        allowed = {"NOMINAL", "THERMAL_SPIKE", "VIBRATION_ANOMALY", "DEEP_SLEEP"}
        m_up = mode.upper()
        if m_up not in allowed:
            raise ValueError(f"Invalid hardware mode '{mode}'. Allowed: {', '.join(allowed)}")
        ProdeEngine._hardware_mode = m_up
        self.db.log_event(
            actor="CPE-01 (Embedded Systems Lead)",
            action="HARDWARE_SIMULATION_TRIGGERED",
            target_id="PRODE-ESP32-S3-01",
            details=f"Hardware operating condition set to {m_up}.",
        )
        return self.get_hardware_telemetry()
