# Dual-shell static pages (ML monitoring)

This folder builds **recruiter** and **commercial** static shells for the ML monitoring & data-quality pipeline using `render-shell.mjs`.

## Layout outputs

| Profile | Output directory | Intended host |
|--------|------------------|---------------|
| `recruiter` | `layout-shell/` | karatas / portfolio-side host only |
| `commercial` | `layout-shell-commercial/` | **`*.vahdetlabs.com` only** (no `vahdetkaratas.com` URLs inside this build) |

Labs Streamlit demo: **`ml-monitoring.vahdetlabs.com`**. Portfolio/recruiter Streamlit (when used): **`monitoring.vahdetkaratas.com`**. Shell builds contain **no FastAPI**.

## Files

- `index.html` — template with placeholders
- `shell.css`, `demo-content.css`, `shell.js`, `favicon.svg`, `avatar-vk.svg`
- `profiles/recruiter.json`, `profiles/commercial.json`
- `projects/monitoring.json` — project metadata + per-profile overrides
- `body/monitoring.html` — recruiter / proof-of-work body
- `body/monitoring-commercial.html` — commercial body (separate copy)

## Render commands

From the **repository root**:

**Recruiter shell**

```bash
node shell/render-shell.mjs \
  --project shell/projects/monitoring.json \
  --body shell/body/monitoring.html \
  --out layout-shell \
  --profile recruiter
```

**Commercial shell**

```bash
node shell/render-shell.mjs \
  --project shell/projects/monitoring.json \
  --body shell/body/monitoring-commercial.html \
  --out layout-shell-commercial \
  --profile commercial
```

Outputs include `index.html`, copied CSS/JS, `favicon.svg`, `avatar-vk.svg` (shared VK monogram avatar), and embedded `profile.json` for debugging.

**Brand separation:** the **`commercial`** render must stay on **VahdetLabs** links only (`vahdetlabs.com`, `*.vahdetlabs.com`). Do not add portfolio / `vahdetkaratas.com` URLs to `profiles.commercial`, `monitoring.json` → `profiles.commercial`, or `monitoring-commercial.html`.

## Rules enforced in this adaptation

- **`commercial`** shell: labs-only outbound links; **`recruiter`** shell may use portfolio / `vahdetkaratas.com` where appropriate.
- Shared template uses neutral `.shell-project-page` / `.shell-project-footer` classes — no RAG-specific naming.
