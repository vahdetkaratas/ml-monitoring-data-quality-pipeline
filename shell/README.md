# Dual-shell static pages (ML monitoring)

This folder builds **recruiter** and **commercial** static shells for the ML monitoring & data-quality pipeline using `render-shell.mjs`.

## Layout outputs

| Profile | Output directory | Intended host |
|--------|------------------|---------------|
| `recruiter` | `layout-shell/` | project-specific (often portfolio subdomain on karatas) |
| `commercial` | `layout-shell-commercial/` | **`ml-monitoring.vahdetkaratas.com`** (commercial introduction) |

Labs Streamlit demo only: **`ml-monitoring.vahdetlabs.com`**. Portfolio/recruiter Streamlit (when used): **`monitoring.vahdetkaratas.com`**. Shell builds contain **no FastAPI**.

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

**Commercial static host:** **`https://ml-monitoring.vahdetkaratas.com/`** (`layout-shell-commercial`). **Labs Streamlit demo:** **`https://ml-monitoring.vahdetlabs.com/`** — separate subdomain from the intro page.

## Rules enforced in this adaptation

- Commercial shell deploy targets **`ml-monitoring.vahdetkaratas.com`**; Labs Streamlit uses **`ml-monitoring.vahdetlabs.com`**. Recruiter and commercial share **`avatar-vk.svg`**.
- Recruiter profile references **`monitoring.vahdetkaratas.com`** Streamlit and portfolio URLs as needed.
- Shared template uses neutral `.shell-project-page` / `.shell-project-footer` classes — no RAG-specific naming.
