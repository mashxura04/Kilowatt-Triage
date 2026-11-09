# Kilowatt Triage — project website

Team 7345 · NYAS Junior Academy · research and prototype stage.
A static site: plain HTML, CSS and JavaScript. No build step, no dependencies, no environment variables.

## Folder structure

```
kilowatt-triage/
├── index.html          all content and the data (as data-* attributes)
├── css/styles.css      design system, layouts, responsive rules
├── js/main.js          scroll thread, charts, zone explorer, approach diagram
├── assets/favicon.svg
├── vercel.json         clean URLs + cache headers
└── README.md
```

All artwork (the school drawing, the triage tag, the webs) is SVG/CSS made for this site. No images to go missing.
Fonts (Archivo, JetBrains Mono) load from Google Fonts. If they are blocked, the site falls back to system fonts and stays readable.

## Preview locally

```bash
cd kilowatt-triage
python3 -m http.server 8000
# open http://localhost:8000
```

## Deploy on Vercel

**Option A — dashboard (easiest)**
1. Put this folder in a GitHub repository (the folder's contents at the repo root).
2. On vercel.com choose **Add New → Project** and import the repository.
3. Framework Preset: **Other**. Build Command: leave empty. Output Directory: leave empty (the root is served).
4. Click **Deploy**.

**Option B — CLI**
```bash
npm i -g vercel
cd kilowatt-triage
vercel          # first deploy (preview)
vercel --prod   # production
```

No environment variables or extra configuration are needed.

## Editing the data

Every research figure lives in `index.html` as plain text and `data-*` attributes:

- Zone intensities: `.zbar` rows (`data-h`, `data-l`, `data-e`, `data-t`), World Bank Table 36
- Savings and investment: `.iv` rows (`data-save`, `data-cost`), World Bank Tables 42 and 47
- Chart scales: `MAX_INTENSITY`, `MAX_SAVE`, `MAX_COST` in `js/main.js`. Update the tick labels in `index.html` if you change them.

Progress stages (Section 05) are the `.step` items; the class `is-done`, `is-now` or `is-next` sets their status and the summary line updates automatically.

## Data provenance

| Label on site | Meaning |
|---|---|
| Published | Taken directly from World Bank (2021), *Uzbekistan: Deploying Energy Efficiency and Distributed Solar in Public Buildings* |
| Our arithmetic | A ratio or total we computed (62×, 1.95×, intensity × 4,000 m²) |
| Assumption | A working choice, not a finding |
| Not yet collected | School-specific bills, on-site validation, local feedback, verified grid-emissions factor |

The site deliberately contains no school-specific measurements, no carbon-reduction figure, and no claim that the reference school represents every school in Uzbekistan.

## Accessibility notes

Semantic landmarks, skip link, keyboard-operable controls (`aria-pressed` states), AA contrast, `prefers-reduced-motion` respected (all animation and smooth scrolling are switched off).
