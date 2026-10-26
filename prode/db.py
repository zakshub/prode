"""
PRODE SQLite Persistence & Transactional Ledger.
Seeds all 9 Departments, 69 Specialist Roles, 5 Versions, 15 Projects, 30 Milestones, and 90 Tasks.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from prode.catalog import (
    COMPANY_PROFILE,
    DEPARTMENTS,
    PROJECTS,
    REVENUE_ENGINES,
    ROLES,
    VERSIONS,
)

DEFAULT_DB_PATH = str(Path(__file__).resolve().parent.parent / "prode.db")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class ProdeDB:
    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self.init_schema()
        self.seed_if_empty()

    def close(self) -> None:
        self._conn.close()

    def init_schema(self) -> None:
        cur = self._conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS company_state (
                company_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                founder TEXT NOT NULL,
                current_active_version TEXT NOT NULL,
                authorized_spend_usd REAL NOT NULL DEFAULT 0.0,
                cash_flow_rule TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS departments (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role_count INTEGER NOT NULL,
                lead_role_id TEXT NOT NULL,
                governing_brains_json TEXT NOT NULL,
                mission TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS roles (
                id TEXT PRIMARY KEY,
                department_id TEXT NOT NULL,
                title TEXT NOT NULL,
                agent_archetype TEXT NOT NULL,
                execution_mode TEXT NOT NULL,
                governing_brain TEXT NOT NULL,
                activation_version TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 0,
                permission_tier TEXT NOT NULL,
                responsibilities TEXT NOT NULL,
                deliverables_json TEXT NOT NULL,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            );

            CREATE TABLE IF NOT EXISTS versions (
                version TEXT PRIMARY KEY,
                phase_number INTEGER NOT NULL,
                name TEXT NOT NULL,
                focus_model TEXT NOT NULL,
                revenue_focus_json TEXT NOT NULL,
                goal TEXT NOT NULL,
                exit_criteria TEXT NOT NULL,
                status TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                version TEXT NOT NULL,
                title TEXT NOT NULL,
                revenue_engine TEXT NOT NULL,
                category TEXT NOT NULL,
                goal TEXT NOT NULL,
                contract_value_usd REAL NOT NULL DEFAULT 0.0,
                deposit_50_cleared INTEGER NOT NULL DEFAULT 0,
                staging_25_cleared INTEGER NOT NULL DEFAULT 0,
                final_25_cleared INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL,
                FOREIGN KEY (version) REFERENCES versions(version)
            );

            CREATE TABLE IF NOT EXISTS milestones (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                version TEXT NOT NULL,
                title TEXT NOT NULL,
                goal TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                milestone_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                version TEXT NOT NULL,
                title TEXT NOT NULL,
                assigned_role_id TEXT NOT NULL,
                reviewer_role_id TEXT NOT NULL,
                governing_brain TEXT NOT NULL,
                qc_gate TEXT NOT NULL,
                depends_on_json TEXT NOT NULL,
                acceptance_criteria TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'QUEUED',
                design_fit_qc TEXT NOT NULL DEFAULT 'PENDING',
                image_qc TEXT NOT NULL DEFAULT 'PENDING',
                ast_compile_qc TEXT NOT NULL DEFAULT 'PENDING',
                completed_at TEXT,
                FOREIGN KEY (milestone_id) REFERENCES milestones(id),
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );

            CREATE TABLE IF NOT EXISTS approvals (
                id TEXT PRIMARY KEY,
                approval_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                requested_by_role TEXT NOT NULL,
                summary TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                decided_by TEXT,
                decided_at TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS knowledge_vault (
                id TEXT PRIMARY KEY,
                artifact_type TEXT NOT NULL,
                project_id TEXT NOT NULL,
                title TEXT NOT NULL,
                ip_classification TEXT NOT NULL,
                governing_brain TEXT NOT NULL,
                content TEXT NOT NULL,
                created_by_role TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                target_id TEXT NOT NULL,
                details TEXT NOT NULL
            );
            """
        )
        self._conn.commit()

    def seed_if_empty(self) -> None:
        cur = self._conn.cursor()
        row = cur.execute("SELECT COUNT(*) AS cnt FROM departments").fetchone()
        if row and row["cnt"] > 0:
            return

        now = utc_now()
        cur.execute(
            """
            INSERT INTO company_state (
                company_id, name, founder, current_active_version,
                authorized_spend_usd, cash_flow_rule, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                COMPANY_PROFILE["company_id"],
                COMPANY_PROFILE["name"],
                COMPANY_PROFILE["founder"],
                COMPANY_PROFILE["current_active_version"],
                COMPANY_PROFILE["authorized_spend_usd"],
                COMPANY_PROFILE["cash_flow_rule"],
                now,
            ),
        )

        for dept in DEPARTMENTS:
            cur.execute(
                """
                INSERT INTO departments (id, name, role_count, lead_role_id, governing_brains_json, mission)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    dept["id"],
                    dept["name"],
                    dept["role_count"],
                    dept["lead_role_id"],
                    json.dumps(dept["governing_brains"]),
                    dept["mission"],
                ),
            )

        for role in ROLES:
            cur.execute(
                """
                INSERT INTO roles (
                    id, department_id, title, agent_archetype, execution_mode,
                    governing_brain, activation_version, is_active, permission_tier,
                    responsibilities, deliverables_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    role["id"],
                    role["department_id"],
                    role["title"],
                    role["agent_archetype"],
                    role["execution_mode"],
                    role["governing_brain"],
                    role["activation_version"],
                    1 if role["default_active"] else 0,
                    role["permission_tier"],
                    role["responsibilities"],
                    json.dumps(role["deliverables"]),
                ),
            )

        for ver in VERSIONS:
            cur.execute(
                """
                INSERT INTO versions (
                    version, phase_number, name, focus_model,
                    revenue_focus_json, goal, exit_criteria, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ver["version"],
                    ver["phase_number"],
                    ver["name"],
                    ver["focus_model"],
                    json.dumps(ver["revenue_focus"]),
                    ver["goal"],
                    ver["exit_criteria"],
                    ver["status"],
                ),
            )

        for proj in PROJECTS:
            cur.execute(
                """
                INSERT INTO projects (
                    id, version, title, revenue_engine, category, goal,
                    contract_value_usd, deposit_50_cleared, staging_25_cleared,
                    final_25_cleared, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    proj["id"],
                    proj["version"],
                    proj["title"],
                    proj["revenue_engine"],
                    proj["category"],
                    proj["goal"],
                    proj["contract_value_usd"],
                    1 if proj["deposit_50_cleared"] else 0,
                    1 if proj["staging_25_cleared"] else 0,
                    1 if proj["final_25_cleared"] else 0,
                    proj["status"],
                ),
            )
            for ms in proj["milestones"]:
                cur.execute(
                    """
                    INSERT INTO milestones (id, project_id, version, title, goal, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        ms["id"],
                        proj["id"],
                        proj["version"],
                        ms["title"],
                        ms["goal"],
                        "IN_PROGRESS" if proj["status"] == "ACTIVE" else "PENDING",
                    ),
                )
                for task in ms["tasks"]:
                    cur.execute(
                        """
                        INSERT INTO tasks (
                            id, milestone_id, project_id, version, title,
                            assigned_role_id, reviewer_role_id, governing_brain,
                            qc_gate, depends_on_json, acceptance_criteria, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            task["id"],
                            ms["id"],
                            proj["id"],
                            proj["version"],
                            task["title"],
                            task["assigned_role_id"],
                            task["reviewer_role_id"],
                            task["governing_brain"],
                            task["qc_gate"],
                            json.dumps(task["depends_on"]),
                            task["acceptance_criteria"],
                            "QUEUED",
                        ),
                    )

        # Seed initial Knowledge Vault artifacts
        cur.execute(
            """
            INSERT INTO knowledge_vault (
                id, artifact_type, project_id, title, ip_classification,
                governing_brain, content, created_by_role, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "KV-ADR-001",
                "ADR",
                "PROJ-V1-01",
                "ADR-001: Hybrid Product Engineering & Interactive Tech over Pure SaaS",
                "PRODE_CORE_IP",
                "zis",
                "Accepted: Start with Product Design & Engineering Studio (REV-01) and Productized Services (REV-02) using AI-Native operations (ZaxterLab), expanding into Interactive 3D (v3.0), Cyber-Physical Electronics (v4.0), and validated SaaS spinouts (v5.0).",
                "EXEC-01",
                now,
            ),
        )

        # Seed an initial sovereign approval item for demonstration
        cur.execute(
            """
            INSERT INTO approvals (
                id, approval_type, target_id, requested_by_role, summary, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "APR-001",
                "RELEASE_HANDOVER",
                "PROJ-V1-02",
                "QSR-08",
                "Approve final 25% invoice clearance and handover for Sprint Zero & CodeLift Engine (PROJ-V1-02).",
                "PENDING",
                now,
            ),
        )

        self.log_event(
            actor="EXEC-01 (Zak)",
            action="COMPANY_OS_SEEDED",
            target_id="PRODE-CORE",
            details="Seeded 9 departments, 69 specialist roles, 5 versions, 15 projects, 30 milestones, and 90 tasks.",
            commit=False,
        )
        self._conn.commit()

    def log_event(
        self, actor: str, action: str, target_id: str, details: str, commit: bool = True
    ) -> None:
        self._conn.execute(
            """
            INSERT INTO audit_log (timestamp, actor, action, target_id, details)
            VALUES (?, ?, ?, ?, ?)
            """,
            (utc_now(), actor, action, target_id, details),
        )
        if commit:
            self._conn.commit()

    def get_company_state(self) -> Dict[str, Any]:
        row = self._conn.execute("SELECT * FROM company_state LIMIT 1").fetchone()
        return dict(row) if row else dict(COMPANY_PROFILE)

    def get_departments(self) -> List[Dict[str, Any]]:
        rows = self._conn.execute("SELECT * FROM departments ORDER BY id").fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["governing_brains"] = json.loads(d.pop("governing_brains_json"))
            active_cnt = self._conn.execute(
                "SELECT COUNT(*) AS c FROM roles WHERE department_id = ? AND is_active = 1",
                (d["id"],),
            ).fetchone()["c"]
            d["active_role_count"] = active_cnt
            result.append(d)
        return result

    def get_roles(
        self, department_id: Optional[str] = None, active_only: bool = False
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM roles WHERE 1=1"
        params: List[Any] = []
        if department_id and department_id.lower() != "all":
            query += " AND department_id = ?"
            params.append(department_id.upper())
        if active_only:
            query += " AND is_active = 1"
        query += " ORDER BY id"
        rows = self._conn.execute(query, params).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["deliverables"] = json.loads(d.pop("deliverables_json"))
            d["is_active"] = bool(d["is_active"])
            result.append(d)
        return result

    def get_versions(self) -> List[Dict[str, Any]]:
        rows = self._conn.execute("SELECT * FROM versions ORDER BY phase_number").fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["revenue_focus"] = json.loads(d.pop("revenue_focus_json"))
            result.append(d)
        return result

    def get_projects(self, version: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM projects WHERE 1=1"
        params: List[Any] = []
        if version and version.lower() != "all":
            query += " AND version = ?"
            params.append(version.lower())
        query += " ORDER BY id"
        rows = self._conn.execute(query, params).fetchall()
        result = []
        for r in rows:
            p = dict(r)
            p["deposit_50_cleared"] = bool(p["deposit_50_cleared"])
            p["staging_25_cleared"] = bool(p["staging_25_cleared"])
            p["final_25_cleared"] = bool(p["final_25_cleared"])
            ms_rows = self._conn.execute(
                "SELECT * FROM milestones WHERE project_id = ? ORDER BY id", (p["id"],)
            ).fetchall()
            milestones = []
            for m in ms_rows:
                md = dict(m)
                t_rows = self._conn.execute(
                    "SELECT * FROM tasks WHERE milestone_id = ? ORDER BY id", (md["id"],)
                ).fetchall()
                tasks = []
                for t in t_rows:
                    td = dict(t)
                    td["depends_on"] = json.loads(td.pop("depends_on_json"))
                    tasks.append(td)
                md["tasks"] = tasks
                milestones.append(md)
            p["milestones"] = milestones
            result.append(p)
        return result

    def get_approvals(self) -> List[Dict[str, Any]]:
        rows = self._conn.execute("SELECT * FROM approvals ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

    def get_knowledge_vault(self) -> List[Dict[str, Any]]:
        rows = self._conn.execute("SELECT * FROM knowledge_vault ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

    def get_audit_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
