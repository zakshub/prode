"""
PRODE Command-Line Interface (`python3 -m prode <command>`).
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from prode.catalog import (
    COMPANY_PROFILE,
    DEPARTMENTS,
    PROJECTS,
    REVENUE_ENGINES,
    ROLES,
    VERSIONS,
)
from prode.db import DEFAULT_DB_PATH, ProdeDB
from prode.engine import ProdeEngine
from prode.server import run_server


def cmd_status(engine: ProdeEngine) -> int:
    summary = engine.get_dashboard_summary()
    comp = summary["company"]
    m = summary["metrics"]
    print("=" * 78)
    print(f" {comp['name']}")
    print("=" * 78)
    print(f" Founder / Sovereign : {comp['founder']}")
    print(f" Active Version      : {comp['current_active_version']}")
    print(f" Authorized Spend    : ${comp['authorized_spend_usd']:.2f} USD (Hard Lock)")
    print(f" Cash-Flow Policy    : {comp['cash_flow_rule']}")
    print("-" * 78)
    print(f" Functions / Depts   : {m['total_departments']}")
    print(f" Specialist Roles    : {m['total_roles']} total ({m['active_roles']} Active, {m['dormant_roles']} Dormant)")
    print(f" Versions / Phases   : {m['total_versions']} (v1.0 -> v5.0)")
    print(f" Projects            : {m['total_projects']}")
    print(f" Milestones          : {m['completed_milestones']} / {m['total_milestones']} Completed")
    print(f" Tasks               : {m['completed_tasks']} / {m['total_tasks']} Completed")
    print(f" Knowledge Vault     : {m['vault_artifacts']} Artifacts")
    print(f" Pending Approvals   : {m['pending_approvals']}")
    print("=" * 78)
    return 0


def cmd_roles(engine: ProdeEngine, department: str, active_only: bool) -> int:
    depts = {d["id"]: d["name"] for d in engine.db.get_departments()}
    roles = engine.db.get_roles(department_id=department, active_only=active_only)
    print(f"Showing {len(roles)} Specialist Roles (Department filter: {department}):")
    print("-" * 95)
    for r in roles:
        status = "ACTIVE " if r["is_active"] else "DORMANT"
        dept_name = depts.get(r["department_id"], r["department_id"])
        print(
            f"[{r['id']}] ({status}) {r['title']:<42} | {r['department_id']} ({dept_name}) | "
            f"Brain: {r['governing_brain']:<10} | {r['activation_version']}"
        )
    print("-" * 95)
    return 0


def cmd_roadmap(engine: ProdeEngine, version: str) -> int:
    versions = engine.db.get_versions()
    projects = engine.db.get_projects(version=version)
    for v in versions:
        if version.lower() != "all" and v["version"].lower() != version.lower():
            continue
        print("=" * 88)
        print(f" {v['version'].upper()} — {v['name']} [{v['status']}]")
        print(f" Goal: {v['goal']}")
        print(f" Exit Gate: {v['exit_criteria']}")
        print("=" * 88)
        v_projs = [p for p in projects if p["version"] == v["version"]]
        for p in v_projs:
            print(
                f"\n  Project [{p['id']}] ({p['revenue_engine']}) {p['title']} — Status: {p['status']}"
            )
            print(f"  Goal: {p['goal']}")
            for ms in p["milestones"]:
                print(f"    Milestone [{ms['id']}] {ms['title']} ({ms['status']})")
                for t in ms["tasks"]:
                    deps = ",".join(t["depends_on"]) if t["depends_on"] else "None"
                    print(
                        f"      - [{t['id']}] ({t['status']}) {t['title']} "
                        f"[{t['assigned_role_id']} -> {t['reviewer_role_id']} | {t['qc_gate']} | Deps: {deps}]"
                    )
        print()
    return 0


def cmd_simulate(engine: ProdeEngine, project_id: str, auto_clear_deposit: bool) -> int:
    if project_id.lower() == "all":
        projects = engine.db.get_projects()
        for p in projects:
            res = engine.simulate_project(p["id"], auto_clear_deposit=True)
            print(
                f"[SIMULATED] {res['project_id']} ({res['version']}): "
                f"{res['tasks_executed']} tasks completed -> Certificate {res['qc_certificate_id']}"
            )
        return 0

    res = engine.simulate_project(project_id.upper(), auto_clear_deposit=auto_clear_deposit)
    print(json.dumps(res, indent=2))
    return 0


def cmd_export_schemas() -> int:
    root = Path(__file__).resolve().parent.parent
    out_path = root / "schemas" / "role_taxonomy.json"
    dept_list = []
    for d in DEPARTMENTS:
        d_roles = [r for r in ROLES if r["department_id"] == d["id"]]
        dept_list.append(
            {
                "id": d["id"],
                "name": d["name"],
                "role_count": d["role_count"],
                "head_of_department": d["lead_role_id"],
                "governing_brains": d["governing_brains"],
                "mission": d["mission"],
                "roles": d_roles,
            }
        )
    payload = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "PRODE_RoleTaxonomy",
        "version": "1.0.0",
        "total_departments": len(DEPARTMENTS),
        "total_roles": len(ROLES),
        "departments": dept_list,
    }
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    seed_path = root / "schemas" / "company_os_seed.json"
    seed_payload = {
        "company_profile": COMPANY_PROFILE,
        "revenue_engines": REVENUE_ENGINES,
        "departments": DEPARTMENTS,
        "roles": ROLES,
        "versions": VERSIONS,
        "projects": PROJECTS,
    }
    seed_path.write_text(json.dumps(seed_payload, indent=2) + "\n", encoding="utf-8")
    print(f"Exported {len(DEPARTMENTS)} departments and {len(ROLES)} roles to {out_path} and {seed_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prode",
        description="PRODE — AI-Native Product Engineering & Interactive Technology Company OS",
    )
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help="Path to SQLite database")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Show company status, active roles, and roadmap metrics")

    p_roles = sub.add_parser("roles", help="List all 9 departments and 69 specialist roles")
    p_roles.add_argument("--department", default="all", help="Department ID (e.g. DEPT-01 or all)")
    p_roles.add_argument("--active-only", action="store_true", help="Show only active roles")

    p_road = sub.add_parser("roadmap", help="Inspect versions (v1.0-v5.0), projects, milestones, and tasks")
    p_road.add_argument("--version", default="all", help="Version filter (v1.0, v2.0, v3.0, v4.0, v5.0, or all)")

    p_sim = sub.add_parser("simulate", help="Execute a project's task DAG through Triple QC gates")
    p_sim.add_argument("--project", default="PROJ-V1-01", help="Project ID (e.g. PROJ-V1-01 or all)")
    p_sim.add_argument("--clear-deposit", action="store_true", help="Auto-clear 50% deposit before simulation")

    p_app = sub.add_parser("approve", help="Approve or reject a pending Sovereign Approval item")
    p_app.add_argument("--id", required=True, help="Approval ID (e.g. APR-001)")
    p_app.add_argument("--decision", default="APPROVED", choices=["APPROVED", "REJECTED"])

    p_srv = sub.add_parser("serve", help="Start the local PRODE Web Control Center & API server")
    p_srv.add_argument("--host", default="127.0.0.1", help="Bind host (default 127.0.0.1)")
    p_srv.add_argument("--port", type=int, default=8080, help="Bind port (default 8080)")

    sub.add_parser("export-schemas", help="Export full 69-role catalog to schemas/role_taxonomy.json")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    cmd = args.command or "status"

    if cmd == "export-schemas":
        return cmd_export_schemas()

    if cmd == "serve":
        run_server(host=args.host, port=args.port, db_path=args.db)
        return 0

    db = ProdeDB(db_path=args.db)
    engine = ProdeEngine(db=db)
    try:
        if cmd == "status":
            return cmd_status(engine)
        if cmd == "roles":
            return cmd_roles(engine, args.department, args.active_only)
        if cmd == "roadmap":
            return cmd_roadmap(engine, args.version)
        if cmd == "simulate":
            return cmd_simulate(engine, args.project, args.clear_deposit)
        if cmd == "approve":
            res = engine.decide_approval(args.id, args.decision)
            print(json.dumps(res, indent=2))
            return 0
        return cmd_status(engine)
    finally:
        db.close()
