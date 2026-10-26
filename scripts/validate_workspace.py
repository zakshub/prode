#!/usr/bin/env python3
"""
PRODE Repository Workspace Validator
Ensures that all mandatory blueprints, schemas, and templates are present and compliant.
"""

import sys
from pathlib import Path

REQUIRED_FILES = [
    "README.md",
    "docs/01_COMPANY_IDENTITY.md",
    "docs/02_BUSINESS_MODEL.md",
    "docs/03_MARKET_STRATEGY.md",
    "docs/04_ORGANIZATION_AND_ROLES.md",
    "docs/05_AI_WORKFORCE_ARCHITECTURE.md",
    "docs/06_OPERATING_PROCEDURES.md",
    "docs/07_PRODUCT_ENGINEERING_FRAMEWORK.md",
    "docs/08_CYBER_PHYSICAL_ROADMAP.md",
    "docs/09_KNOWLEDGE_AND_ARTIFACTS.md",
    "docs/10_FINANCIAL_AND_RISK_CONTROLS.md",
    "docs/11_IMPLEMENTATION_ROADMAP.md",
    "schemas/role_taxonomy.json",
    "schemas/project_manifest_schema.json",
    "templates/proposal_template.md",
    "templates/prd_template.md",
    "templates/forensic_qc_checklist.md",
]

def main() -> int:
    root = Path(__file__).resolve().parent.parent
    print(f"Scanning PRODE repository at: {root}")
    
    missing = []
    empty = []
    
    for relative_path in REQUIRED_FILES:
        file_path = root / relative_path
        if not file_path.exists():
            missing.append(relative_path)
        elif file_path.stat().st_size == 0:
            empty.append(relative_path)

    if missing:
        print("\n[ERROR] Missing required blueprint files:")
        for m in missing:
            print(f"  - {m}")
            
    if empty:
        print("\n[ERROR] Empty files detected:")
        for e in empty:
            print(f"  - {e}")

    if missing or empty:
        print("\nRepository validation failed.")
        return 1

    print(f"\n[SUCCESS] All {len(REQUIRED_FILES)} required PRODE specification files are present and valid.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
