# Dual-shell static pages (ML monitoring)

This folder builds **recruiter** and **commercial** static shells for the ML monitoring & data-quality pipeline using `render-shell.mjs`.

## Layout outputs

| Profile | Output directory | Intended host |
|--------|------------------|---------------|
| `recruiter` | `layout-shell/` | `ml-monitoring.vahdetkaratas.com` |
| `commercial` | `layout-shell-commercial/` | `ml-monitoring.vahdetlabs.com` |

The **Streamlit artifact viewer** stays separate (e.g. `monitoring.vahdetkaratas.com`). These shells are **static HTML + assets** only — no FastAPI layer is introduced here.

## Files

- `index.html` — template with placeholders
- `shell.css`, `demo-content.css`, `shell.js`, `favicon.svg`, `avatar-commercial.svg`
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

Outputs include `index.html`, copied CSS/JS, `favicon.svg`, `avatar-commercial.svg` (used by the commercial profile), and embedded `profile.json` for debugging.

## Rules enforced in this adaptation

- Commercial profile avoids `vahdetkaratas.com` domains/subdomains and uses a labs-local avatar (`avatar-commercial.svg`).
- Recruiter profile may reference the Streamlit viewer on `monitoring.vahdetkaratas.com` and personal portfolio URLs.
- Shared template uses neutral `.shell-project-page` / `.shell-project-footer` classes — no RAG-specific naming.
