# Dual-Gate Forensic Quality Control (QC) Checklist

**Release Candidate:** [Version Tag or Git Commit SHA]  
**Date:** [YYYY-MM-DD]  
**Auditor (Code & Systems):** `zakshub/codelift` Protocol  
**Auditor (Visual & Physical):** `zakshub/studio` Protocol  
**Human Approver:** Zak (`zakshub`)

---

## Gate 1: Code Reliability & Compiler Verification (`codelift`)

| Inspection Item | Validation Command / Tool | Status | Auditor Notes |
| :--- | :--- | :---: | :--- |
| **Static Type Safety** | `npm run typecheck` (`tsc --noEmit`) | [PASS / FAIL] | Zero type errors allowed. |
| **AST Build Compilation** | `npm run build` | [PASS / FAIL] | Production bundle compiles cleanly. |
| **Unit & Integration Tests** | `npm run test` | [PASS / FAIL] | 100% test suite pass rate. |
| **Linting & Code Formatting**| `npm run lint` | [PASS / FAIL] | Adheres strictly to project styleguide. |
| **Secret & Vault Leak Scan** | Git diff audit / TruffleHog | [PASS / FAIL] | Zero API keys, secrets, or tokens committed. |
| **Accessibility Compliance** | axe-core / Lighthouse audit | [PASS / FAIL] | W3C WCAG AA compliant. |

---

## Gate 2: Forensic Visual & Physical Causality Verification (`studio`)

| Visual Element | Physical Causality Verification Criteria | Status | Notes |
| :--- | :--- | :---: | :--- |
| **Directional Lighting** | Visible shadows correspond accurately to defined light sources. | [PASS / FAIL] | No contradictory illumination. |
| **Contact Physics & Gravity**| Garments, surfaces, and objects show realistic compression and contact. | [PASS / FAIL] | No floating or geometry clipping. |
| **Material Optics** | Specular highlights, subsurface scattering, and roughness behave realistically. | [PASS / FAIL] | Plastic/metal roughness adheres to physics. |
| **Anti-AI Artifact Audit** | Hands, eyes, text, micro-textures show zero AI distortion or smearing. | [PASS / FAIL] | Uncompromising photographic realism. |
| **3D Rendering Frame Rate** | Interactive WebGL scene maintains solid 60 FPS under test load. | [PASS / FAIL] | Mobile and desktop verified. |

---

## Gate 3: Sovereign Owner Sign-Off

* [ ] Milestone demonstrated and verified on staging.
* [ ] All financial invoices and deposits cleared.
* [ ] Human owner (Zak) explicit sign-off recorded.

**Final Release Status:** [APPROVED FOR PRODUCTION / BLOCKED - REWORK REQUIRED]  
**Signature (Zak):** _______________________________________
