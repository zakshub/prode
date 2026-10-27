# System Architecture Specification
## Sentinel Cardiac IoT Gateway (apex_health_sentinel_cardiac_iot_gateway)

### 1. Technology Stack
- **Frontend Framework:** Next.js 14+ (App Router, Server & Client Components)
- **Styling & UI Tokens:** Tailwind CSS with Sentinel Companion palettes
- **3D Spatial Graphics:** Three.js / WebGL with procedural fallback
- **Backend & Persistence:** SQLite (Dev) / PostgreSQL (Prod) via Prisma ORM
- **Cyber-Physical Gateway:** MQTT / WebSockets for IoT & ESP32 telemetry

### 2. Directory Layout
```text
apex_health_sentinel_cardiac_iot_gateway/
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
