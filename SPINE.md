# CineClear AI - System Backbone & Operational Spine (SPINE.md)

This document defines the **core philosophy, legal clearance invariants, statutory rules, and pipeline lifecycles** of CineClear AI.

---

## 1. System Invariants & Cinema Clearance Policy

1. **Zero Uncleared Liabilities in Distribution Cuts:**
   * Commercial feature films, episodic streaming series, and national broadcast spots cannot obtain Errors & Omissions (E&O) insurance coverage without affirmative legal clearance or documented statutory fair use defense for all on-screen and audible elements.
2. **Never Rely on Un-Grounded Assumptions:**
   * Every detected brand, artwork, building, or audio cue MUST be grounded through **Parallel Web Search** against official government registers (USPTO, US Copyright Office, NANPA) or binding case law before assigning risk tiers.
3. **Actionable Remediation over Abstract Warnings:**
   * The system provides concrete, industry-standard cinema remediation deliverables via **Agent 3** (pre-filled Form-4A art releases, trademark placement agreements, timecoded VFX Greeking work orders, NANPA script substitutions, and PRO Music Cue Sheets).
4. **Deterministic Risk Calibration Tiers:**
   * **`CRITICAL`**: Mandatory distribution block. Real working telephone numbers, defamatory brand portrayals in criminal schemes, or living person likeness violations.
   * **`HIGH`**: Action required prior to picture lock. Modern copyrighted visual art in sharp focus, uncleared commercial music, or restricted architectural facades.
   * **`MEDIUM`**: Incidental trademark on hero prop or ambiguous commercial context requiring production counsel review or standard product placement release.
   * **`LOW`**: Confirmed public domain works (pre-1929), de minimis background inclusion, or architectural works visible from public spaces under 17 U.S.C. § 120(a).

---

## 2. The 3-Agent Autonomous Triad & Dynamic Cascade

Live audits stream four UI stages over SSE (`POST /api/audit/stream`). Grounding fans out with `asyncio.as_completed` (Parallel Search + Gemini synthesis per flag). Production requires Judge VIP + TOS acceptance.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           CINECLEAR 3-AGENT ORCHESTRATION                               │
├────────────────────────────┬─────────────────────────────┬──────────────────────────────┤
│ AGENT 1: EXTRACTOR         │ AGENT 2: CRITIC COUNSEL     │ AGENT 3: REMEDIATION         │
├────────────────────────────┼─────────────────────────────┼──────────────────────────────┤
│ • Gemini 3.8 vision/script │ • Multi-turn reflection     │ • Form-4A Art Releases       │
│ • PyMuPDF script parsing   │ • Public domain check       │ • Trademark agreements       │
│ • OpenCV keyframes (async) │ • Reconcile anomalies       │ • VFX Greeking orders        │
│ • 2D Bounding Boxes [0-1k] │ • Risk tier calibration     │ • NANPA 555-01XX fixes       │
│ • ExtractorHarness dedupe  │ • CriticHarness invariants  │ • ASCAP/BMI Music Cue Sheets │
└────────────────────────────┴─────────────────────────────┴──────────────────────────────┘
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
     ┌─────────────────────────┐                     ┌─────────────────────────┐
     │ DYNAMIC MODEL CASCADE   │                     │ STATUTORY ENGINES       │
     ├─────────────────────────┤                     ├─────────────────────────┤
     │ 1. gemini-3.8-flash     │                     │ • 4-Factor Fair Use     │
     │ 2. gemini-3.5-flash     │                     │   (17 U.S.C. § 107)     │
     │ (max 2 live tiers)      │                     │ • Multi-Territory (EU/  │
     │ then 3.5-flash-lite,    │                     │   UK/CA/US)             │
     │ 3.6-flash, flash-latest │                     │ • AWCPA § 120(a) Safe   │
     │ then local regex harness│                     │   Harbor & Restricted TM│
     └─────────────────────────┘                     └─────────────────────────┘
```

---

## 3. The 6 Core Clearance Pipeline Lifecycles

### 🏷️ Pipeline A — Trademark & Product Placement Clearance
* **Trigger:** Visual or script detection of registered brand names, logos, trade dress, or distinctive product packaging (e.g., Nike Swoosh, Apple MacBook, Starbucks siren).
* **Statutory Framework:** Lanham Act (15 U.S.C. § 1114 & § 1125(a)).
* **Reasoning Loop:**
  1. Verifies active USPTO registration status via Parallel Search.
  2. Evaluates scene context: Hero prop vs incidental background.
  3. Computes Fair Use Scorecard (17 U.S.C. § 107) nominative fair use defense rating.
* **Mitigation Protocol:**
  * *Hero placement / Malicious context:* Order VFX Greeking / digital paint-out.
  * *Incidental / Natural usage:* Document nominative fair use defense in E&O Binder.

---

### 🎨 Pipeline B — Set Dressing & Copyrighted Art Clearance
* **Trigger:** Visual detection of framed paintings, sculptures, street graffiti/murals, or book jackets on set.
* **Statutory Framework:** 17 U.S.C. § 106 (Exclusive Display & Reproduction Rights) & 17 U.S.C. § 107.
* **Reasoning Loop:**
  1. Checks creation date against worldwide public domain threshold (pre-1929).
  2. Evaluates visual prominence, depth of field blur, and duration.
  3. Maps territory requirements across US (Form-4A required), UK (CDPA 1988 § 31 incidental safe harbor), and Canada (§ 30.7).
* **Mitigation Protocol:**
  * Execute standard **Form-4A Artwork Release Form** with artist or licensing agency.
  * If release cannot be obtained, replace with cleared stock art or blur in VFX.

---

### 🏛️ Pipeline C — Architectural Rights & Location Clearance
* **Trigger:** Exterior or interior footage of distinctive landmarks, modern buildings, or public monuments.
* **Statutory Framework:** Architectural Works Copyright Protection Act (AWCPA - 17 U.S.C. § 120(a)) & Trademark Law.
* **Reasoning Loop:**
  1. Confirms whether the building is located in or ordinarily visible from a public space (protected under 17 U.S.C. § 120(a) safe harbor).
  2. Isolates registered commercial facades and protected light installations (e.g., nighttime Eiffel Tower illumination, Hollywood Sign, Chrysler Building).
* **Mitigation Protocol:**
  * Standard public buildings: Certify statutory safe harbor in E&O report.
  * Protected commercial facades: Execute location release or reframe shot.

---

### 🎵 Pipeline D — Music Synchronization & Sound Recording Clearance
* **Trigger:** Dialogue cues specifying commercial songs, background radio audio, or soundtrack needle drops.
* **Statutory Framework:** 17 U.S.C. § 106 & § 114 (Dual Master + Synchronization Rights).
* **Reasoning Loop:**
  1. Distinguishes public domain compositions from modern proprietary sound recordings.
  2. Identifies master sound recording rights holder (Record Label) and musical composition publisher (PRO: ASCAP / BMI / SESAC).
* **Mitigation Protocol:**
  * Compile standardized **ASCAP / BMI Music Cue Sheet** for post-production.
  * Execute dual Master Sync License + Mechanical Synchronization License.

---

### 📞 Pipeline E — Screenplay PII & Telephone Number Sanitization
* **Trigger:** Screenplay dialogue, action slugs, or prop graphics containing telephone numbers or personal data.
* **Statutory Framework:** FCC / North American Numbering Plan Administration (NANPA) Fictitious Number Safe Harbor.
* **Reasoning Loop:**
  1. Scans all phone numbers against the reserved entertainment safe-harbor block: **`555-0100` through `555-0199`**.
  2. Working non-555 numbers strictly clamped to `CRITICAL` risk.
* **Mitigation Protocol:**
  * **MANDATORY:** Replace all on-screen graphics, dialogue lines, and ADR rerecordings with a valid 555-01XX number.

---

### 👤 Pipeline F — Defamation, Right of Publicity & Likeness Defense
* **Trigger:** Mentions of living public figures, real operating corporations portrayed criminally, or defamatory accusations in dialogue.
* **Statutory Framework:** Common law defamation, False Light, Lanham Act § 43(a) trade disparagement, and State Rights of Publicity.
* **Mitigation Protocol:**
  * Replace with a cleared fictional corporate alias.
  * Execute Script Supervisor legal vetting sign-off.

---

## 4. Dual Harness Boundaries & Statutory Invariants

1. **`ExtractorHarness` Invariants:**
   * Recurring keyframe and repeated script entity deduplication prevents runaway token and search API utilization.
   * Universal schema normalization ensures every candidate item arrives with timecodes and valid entity descriptions.
2. **`CriticHarness` Statutory Invariants:**
   * Modern corporate marks (`MODERN_CORPORATE_MARKS`) are strictly disallowed from being flagged as pre-1929 public domain.
   * `active_trademark_found == True` strictly enforces `is_public_domain = False`.
   * Unmasked telephone numbers are strictly clamped to `CRITICAL` risk.

---

## 5. Deliverables & Decision-Support Boundary (UPL)

CineClear AI is a **paralegal research accelerator**. Outputs are evidence-gathering dossiers for licensed production counsel / E&O brokers. They are **not** legal advice, **not** a distribution clearance, and **not** an insurance certificate.

Every completed audit provides:
1. **Interactive dashboard & SVG bounding boxes** plus a **Live Partner API Trace** (Gemini `generateContent` and Parallel `POST /v1/search` as they fire).
2. **NLE timeline markers (.EDL):** CMX 3600 with color-coded locators and a decision-support comment header.
3. **ReportLab E&O evidence dossier (PDF):** Risk matrix, ledgers, Fair Use scorecards, territory matrices, AWCPA notes, cue sheets, UPL footer on every page, and **licensed production attorney / E&O broker sign-off lines** (CineClear is the gatherer, not the certifier).
4. **Terms of Service** (`/terms`, TOS version 2026-09-06): AS-IS, limitation of liability ($0 on free/hackathon tier), indemnification, upload purge.

## 6. Access, Quota, and Retention Invariants

1. **Judge VIP** (`cineclear-judge-2026` via `?access=` or `X-Judge-Access`) is required for **all** live Gemini/Parallel audits, including bundled samples.
2. **Rate limit:** 12 live audits per hour per client IP.
3. **Zero retention of user uploads:** files under `uploads/` are deleted when the audit finishes. Bundled `sample_media/` is never deleted.
4. **Public guests** may view the landing page; live audit POSTs return 401 without the pass.
