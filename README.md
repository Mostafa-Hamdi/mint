# MINTFORMED · MINT PILs · MINT CONSENT

Static website built from the Mint-pils Figma design: plain HTML, CSS and vanilla JavaScript (no framework).
18 pages across three sites (MINTFORMED, MINT PILs, MINT CONSENT), responsive from phone to desktop.

- **Backend developers: start with [HANDOFF.md](HANDOFF.md)** (forms API, login links, templates, headers, launch checklist).
- Deploy: Vercel, framework preset "Other", no build command, output directory = root. `vercel.json` holds the security and cache headers.
- `_figma-reference/` (design sources, original photos, generator scripts) and `handoff/` are not deployed (`.vercelignore`).

Rebuild after content changes:

```
python -I _figma-reference/_build/build.py .
python -I _figma-reference/_build/finalize.py .
```
