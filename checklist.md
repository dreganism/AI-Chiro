# Chiro-Reporter – Master Implementation Checklist

Consolidated, de-duplicated, and sequenced roadmap for the full Chiro-Reporter application (Rust + Actix-Web backend, Tauri/Web frontend).

## ✅ 1. Core Backend (Rust + Actix-Web)

- [ ] Multi-mode `/generate` endpoint  
  → Accept `?mode=appeal|summary|legal|status|custom` (default: status)  
  → Return 422 on invalid mode
- [ ] Modular Prompt Template System  
  → `templates/` directory with `.md` or `.yaml` files per mode  
  → Dynamic loading + caching + auto-reload on file change  
  → Schema validation for required placeholders/tokens
- [ ] Structured Report Renderer  
  → Markdown → HTML → PDF (`printpdf`, `lopdf`, or `wkhtmltopdf`)  
  → Optional Markdown → DOCX via Pandoc subprocess  
  → JSON metadata export option
- [ ] Section Formatters & Output Structure  
  → Reusable functions for intro, background, rationale, citations, conclusion, physician header, subject line, signature block
- [ ] System Endpoints  
  → `/healthz`, `/version` (Git SHA + build time), `/docs`, `/metrics`

## 📊 2. Data Pre-processing & Extraction

- [ ] Patient Metadata Auto-Extraction (PDF/DICOM/DOCX)  
  → `pdf-extract`, `PyMuPDF`, `lopdf` + Tesseract OCR fallback  
  → Regex + layout heuristics for name, DOB, MRN, insurer, policy ID, DOS, etc.
- [ ] Denial Reason & Code Parsing  
  → Extract quoted denial text and codes (PR-49, CO-109, etc.)  
  → Normalize for prompt injection
- [ ] ICD-10 / CPT Code Validation  
  → Local CSV or CMS/NCCI API lookup  
  → Flag invalid/unsupported combinations
- [ ] Knowledge Base Upload (optional per-user/session)  
  → Accept rebuttal PDFs, LCD/NCD docs, custom guidelines  
  → Store in `/data/knowledge/{session|user}/`  
  → Summarize or embed in-context for GPT

## 🧠 3. Prompt Engineering & GPT Layer

- [ ] Template-Driven Prompt Injection  
  → Inject extracted data + denial text + uploaded knowledge into selected template
- [ ] Inline Citation Engine  
  → Auto-inject CMS LCD/NCD, PubMed, or uploaded references  
  → Format as inline superscripts + reference list
- [ ] Regeneration Endpoint  
  → `/regenerate` with stricter/more aggressive clinical prompt variant

## 🌐 4. Frontend (Tauri or Static Web)

- [ ] Drag-and-Drop Upload Zone  
  → Support PDF, DICOM, DOCX, images  
  → Progress feedback + preview thumbnails
- [ ] Multi-Mode Input Form  
  → Mode dropdown drives conditional field visibility  
  → Editable auto-extracted fields with live validation
- [ ] Error Feedback & Re-analysis  
  → Inline error display (extraction failures, GPT errors)  
  → “Re-analyze” button

## 🚀 5. Deployment & Packaging

- [ ] Docker + Docker Compose stack  
  → Rust API container + NGINX reverse proxy + Certbot companion  
  → Volume mounts for templates, uploads, knowledge base
- [ ] .deb Installer (bare-metal/offline)  
  → Bundle to `/opt/chiro-reporter`  
  → Systemd service + auto NGINX/Certbot setup
- [ ] CI/CD Pipeline (GitHub Actions)  
  → Lint → test → build → push Docker → deploy
- [ ] One-click Linode/VM deployment script (optional)

## 🔬 6. Testing & Validation

- [ ] Unit & Integration Tests (Rust + Frontend)
- [ ] Snapshot Testing for generated reports
- [ ] Offline Validation CLI  
  → Validate CPT/ICD combos, required fields, file parseability
- [ ] Comprehensive `/healthz` checks  
  → OCR deps, GPT connectivity, template loading

## 📄 7. Documentation & Assets

- [ ] Sample files in `/samples/`  
  → denial_letter.pdf, SOAP_notes.pdf, imaging DICOM, expected outputs
- [ ] Comprehensive `README.md` + usage guide for all report modes

## 🚧 8. Future / Low-Priority Enhancements

- [ ] HIPAA-compliant encryption (Vault + at-rest encryption)
- [ ] OAuth2 login (Authelia/Keycloak) for multi-user
- [ ] Built-in PDF/DICOM viewer
- [ ] Batch processing & secure ZIP export
- [ ] Auto-report-type detection via keyword scoring
- [ ] Payment metering (Stripe/Square)
- [ ] OpenTelemetry tracing
- [ ] ICD-10 → HCC risk scoring

---
*Last updated: November 19, 2025*  
This document is the single source of truth for Chiro-Reporter development.
