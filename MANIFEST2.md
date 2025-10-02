# Checkmate Ultimate Solo: CORE Manifest (Total Recall Edition)

**Purpose:** To provide a complete, verified, and actionable list of all source code files that constitute the active CORE Ultimate Solo architecture. This is the definitive manifest for application code review.

---

## 1.0 CORE Architecture Org Chart

```
.
├── python_service/
│   ├── __init__.py
│   ├── api.py
│   ├── engine.py
│   ├── models.py
│   └── adapters/
│       ├── __init__.py
│       ├── base.py
│       ├── utils.py
│       ├── betfair_adapter.py
│       ├── pointsbet_adapter.py
│       ├── racing_and_sports_adapter.py
│       └── tvg_adapter.py
└── web_platform/
    └── frontend/
        ├── next.config.mjs
        ├── package-lock.json
        ├── package.json
        ├── tailwind.config.ts
        ├── tsconfig.json
        └── src/
            └── app/
                ├── globals.css
                ├── layout.tsx
                └── page.tsx
```

---

## 2.0 Python Backend (`python_service/`)

### Core Logic
*   `api.py` - The Flask API entry point.
*   `engine.py` - The central orchestration engine.
*   `models.py` - Pydantic data models for validation.

### Adapters (`python_service/adapters/`)
*   `__init__.py` - Defines the 'adapters' package.
*   `base.py` - The abstract base class for all adapters.
*   `utils.py` - Shared utility functions for adapters.
*   `betfair_adapter.py` - Betfair data source adapter.
*   `pointsbet_adapter.py` - PointsBet data source adapter.
*   `racing_and_sports_adapter.py` - Racing and Sports data source adapter.
*   `tvg_adapter.py` - TVG data source adapter.

## 3.0 TypeScript Frontend (`web_platform/frontend/`)

### Configuration
*   `package.json` - Lists all Node.js dependencies.
*   `package-lock.json` - Locks exact versions for reproducible builds.
*   `next.config.mjs` - Build configuration for Next.js.
*   `tailwind.config.ts` - Tailwind CSS theme and UI configuration.
*   `tsconfig.json` - TypeScript compiler options.

### Application Source (`web_platform/frontend/src/app/`)
*   `page.tsx` - The main application UI component.
*   `layout.tsx` - The root layout and HTML structure.
*   `globals.css` - Global CSS styles.

---

## 4.0 Raw File Links

### Python Backend
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/api.py
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/engine.py
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/models.py
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/__init__.py
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/base.py
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/utils.py
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/betfair_adapter.py
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/pointsbet_adapter.py
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/racing_and_sports_adapter.py
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/tvg_adapter.py

### TypeScript Frontend
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/web_platform/frontend/package.json
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/web_platform/frontend/package-lock.json
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/web_platform/frontend/next.config.mjs
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/web_platform/frontend/tailwind.config.ts
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/web_platform/frontend/tsconfig.json
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/web_platform/frontend/src/app/page.tsx
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/web_platform/frontend/src/app/layout.tsx
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/web_platform/frontend/src/app/globals.css