"""
PRODE HTTP API & Web Control Center Server (Standard Library, Zero External Dependencies).
Default Host: 127.0.0.1, Default Port: 8080.
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import parse_qs, urlparse

from prode.db import DEFAULT_DB_PATH, ProdeDB
from prode.engine import (
    CashFlowLockViolation,
    ContractValidationError,
    ProdeEngine,
    SpendBoundaryViolation,
)

UI_HTML_PATH = Path(__file__).resolve().parent / "ui" / "index.html"


def dispatch_api_request(
    engine: ProdeEngine, method: str, path: str, query: Dict[str, List[str]], body: Dict[str, Any]
) -> Tuple[int, Dict[str, Any]]:
    try:
        if method == "GET":
            if path == "/api/health":
                return 200, {"status": "ok", "authorized_spend_usd": 0.0}
            if path == "/api/dashboard":
                return 200, engine.get_dashboard_summary()
            if path == "/api/departments":
                return 200, {"departments": engine.db.get_departments()}
            if path == "/api/roles":
                dept = query.get("department", ["all"])[0]
                return 200, {"roles": engine.db.get_roles(department_id=dept)}
            if path == "/api/roadmap":
                ver = query.get("version", ["all"])[0]
                return 200, {
                    "versions": engine.db.get_versions(),
                    "projects": engine.db.get_projects(version=ver),
                }
            if path == "/api/vault":
                return 200, {"knowledge_vault": engine.db.get_knowledge_vault()}
            if path == "/api/approvals":
                return 200, {"approvals": engine.db.get_approvals()}

        elif method == "POST":
            if path == "/api/roles/toggle":
                role = engine.toggle_role(body["role_id"], bool(body.get("active", True)))
                return 200, role
            if path == "/api/projects/simulate":
                res = engine.simulate_project(
                    body["project_id"],
                    auto_clear_deposit=bool(body.get("auto_clear_deposit", False)),
                )
                return 200, res
            if path == "/api/projects/payment":
                proj = engine.update_payment_milestone(
                    body["project_id"], body["stage"], bool(body.get("cleared", True))
                )
                return 200, proj
            if path == "/api/approvals/decide":
                ap = engine.decide_approval(body["approval_id"], body["decision"])
                return 200, ap
            if path == "/api/inquiry/submit":
                now = engine.db.get_company_state().get("updated_at")
                inq_id = f"INQ-{len(engine.db.get_approvals()) + 1:03d}"
                client_name = body.get("name", "Prospective Client")
                proj_type = body.get("project_type", "Sprint Zero")
                est_cost = body.get("estimated_cost", "$5,000 - $15,000")
                desc = body.get("description", "New product inquiry")
                summary = f"New Client Inquiry from {client_name} for '{proj_type}' (Est: {est_cost}). Details: {desc}"
                engine.db._conn.execute(
                    """
                    INSERT INTO approvals (id, approval_type, target_id, requested_by_role, summary, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (inq_id, "CLIENT_INQUIRY", inq_id, "MKT-06", summary, "PENDING", now),
                )
                engine.db.log_event(
                    actor="MKT-06 (Sales Copilot)",
                    action="CLIENT_INQUIRY_RECEIVED",
                    target_id=inq_id,
                    details=summary,
                )
                return 201, {"inquiry_id": inq_id, "status": "PENDING_OWNER_REVIEW", "summary": summary}
            if path == "/api/proposal/generate":
                client_name = body.get("client_name", "Acme Corp")
                client_email = body.get("client_email", "contact@acme.com")
                project_title = body.get("project_title", "Sprint Zero Blueprint & Clickable Prototype")
                cost = float(body.get("total_cost_usd", 7500.0))
                timeline = body.get("timeline_str", "10 Business Days")
                problem = body.get("problem_summary", "Transforming product concept into verified software.")
                res = engine.generate_client_proposal(
                    client_name=client_name,
                    client_email=client_email,
                    project_title=project_title,
                    total_cost_usd=cost,
                    timeline_str=timeline,
                    problem_summary=problem,
                )
                return 201, res
            if path == "/api/project/scaffold":
                client_name = body.get("client_name", "Acme Labs")
                project_title = body.get("project_title", "Custom Enterprise Platform")
                project_type = body.get("project_type", "sprint_zero")
                features = body.get("features")
                res = engine.scaffold_client_project(
                    client_name=client_name,
                    project_title=project_title,
                    project_type=project_type,
                    features=features,
                )
                return 201, res
            if path == "/api/vault/create":
                art = engine.create_vault_artifact(
                    artifact_type=body.get("artifact_type", "PRD"),
                    project_id=body.get("project_id", "PROJ-V1-01"),
                    title=body["title"],
                    content=body["content"],
                )
                return 201, art
            if path == "/api/validate/opportunity":
                res = engine.validate_opportunity(
                    pain_severity_annual_usd=float(body.get("pain_severity_annual_usd", 0.0)),
                    velocity_10x_advantage=bool(body.get("velocity_10x_advantage", True)),
                    multidisciplinary_fit=bool(body.get("multidisciplinary_fit", True)),
                    yields_reusable_ip=bool(body.get("yields_reusable_ip", True)),
                    zero_speculative_spend=bool(body.get("zero_speculative_spend", True)),
                )
                return 200, res
            if path == "/api/validate/saas":
                res = engine.validate_saas_spinout(
                    paying_clients_count=int(body.get("paying_clients_count", 0)),
                    reusable_code_ratio=float(body.get("reusable_code_ratio", 0.0)),
                    external_debt_usd=float(body.get("external_debt_usd", 0.0)),
                    has_direct_distribution=bool(body.get("has_direct_distribution", True)),
                )
                return 200, res

        return 404, {"error": f"Route not found: {method} {path}"}

    except (SpendBoundaryViolation, CashFlowLockViolation) as exc:
        return 403, {"error": str(exc)}
    except (ContractValidationError, ValueError, KeyError) as exc:
        return 400, {"error": str(exc)}


def run_server(host: str = "0.0.0.0", port: int = 8080, db_path: str = DEFAULT_DB_PATH) -> None:
    db = ProdeDB(db_path=db_path)
    engine = ProdeEngine(db=db)

    class ProdeRequestHandler(BaseHTTPRequestHandler):
        def _send_json(self, status_code: int, payload: Dict[str, Any]) -> None:
            raw = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path in ("/", "/index.html"):
                html = UI_HTML_PATH.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html)))
                self.end_headers()
                self.wfile.write(html)
                return

            status, payload = dispatch_api_request(
                engine, "GET", parsed.path, parse_qs(parsed.query), {}
            )
            self._send_json(status, payload)

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            body = json.loads(raw_body) if raw_body.strip() else {}
            status, payload = dispatch_api_request(
                engine, "POST", parsed.path, parse_qs(parsed.query), body
            )
            self._send_json(status, payload)

        def log_message(self, format: str, *args: Any) -> None:
            return

    server = HTTPServer((host, port), ProdeRequestHandler)
    print(f"PRODE Control Center listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down PRODE server.")
    finally:
        server.server_close()
        db.close()
