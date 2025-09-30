# Checkmate V8: CORE Project Manifest & Links

**Purpose:** To provide a visual org chart and a complete, actionable list of raw file links for the active **CORE** Penta-Hybrid architecture ONLY.

---

## CORE Architecture Org Chart

```
.
├── .env
├── ARCHITECTURAL_MANDATE.md
├── README.md
├── STATUS.md
├── desktop_app
│   ├── App.xaml
│   ├── App.xaml.cs
│   ├── CheckmateDeck.csproj
│   ├── Models
│   │   ├── AdapterStatusDisplay.cs
│   │   └── DisplayRace.cs
│   ├── Services
│   │   ├── DatabaseService.cs
│   │   └── IDatabaseService.cs
│   ├── ViewModels
│   │   └── MainViewModel.cs
│   ├── Views
│   │   ├── MainWindow.xaml
│   │   └── MainWindow.xaml.cs
│   └── app_config.json
├── python_service
│   ├── __init__.py
│   ├── checkmate_service.py
│   ├── requirements.txt
│   └── windows_service_wrapper.py
├── rust_engine
│   ├── Cargo.lock
│   ├── Cargo.toml
│   └── src
│       ├── ffi.rs
│       ├── lib.rs
│       └── main.rs
├── setup_windows.bat
├── shared_database
│   ├── schema.sql
│   └── web_schema.sql
├── vba_source
│   ├── Module_Charts.bas
│   ├── Module_DB.bas
│   └── Module_UI.bas
└── web_platform
    ├── api_gateway
    │   ├── .env
    │   ├── package-lock.json
    │   ├── package.json
    │   ├── src
    │   │   ├── server.ts
    │   │   └── services
    │   │       └── DatabaseService.ts
    │   └── tsconfig.json
    └── frontend
        ├── app
        │   ├── globals.css
        │   ├── layout.tsx
        │   └── page.tsx
        ├── package-lock.json
        ├── package.json
        ├── postcss.config.js
        ├── src
        │   ├── components
        │   │   ├── LiveRaceDashboard.tsx
        │   │   ├── RaceCard.tsx
        │   │   ├── ScoreBadge.tsx
        │   │   └── TrifectaFactors.tsx
        │   ├── hooks
        │   │   └── useRealTimeRaces.ts
        │   └── types
        │       └── racing.ts
        └── tailwind.config.ts
```

---

## CORE File Links

### Root
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/.env
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/ARCHITECTURAL_MANDATE.md
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/README.md
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/STATUS.md
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/setup_windows.bat

### C# Command Deck (`desktop_app`)
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/desktop_app/App.xaml
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/desktop_app/App.xaml.cs
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/desktop_app/CheckmateDeck.csproj
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/desktop_app/app_config.json
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/desktop_app/Models/AdapterStatusDisplay.cs
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/desktop_app/Models/DisplayRace.cs
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/desktop_app/Services/DatabaseService.cs
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/desktop_app/Services/IDatabaseService.cs
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/desktop_app/ViewModels/MainViewModel.cs
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/desktop_app/Views/MainWindow.xaml
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/desktop_app/Views/MainWindow.xaml.cs

### Python Collection Corps (`python_service`)
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/python_service/__init__.py
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/python_service/checkmate_service.py
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/python_service/requirements.txt
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/python_service/windows_service_wrapper.py

### Rust Analysis Core (`rust_engine`)
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/rust_engine/Cargo.lock
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/rust_engine/Cargo.toml
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/rust_engine/src/ffi.rs
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/rust_engine/src/lib.rs
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/rust_engine/src/main.rs

### Shared Database (`shared_database`)
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/shared_database/schema.sql
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/shared_database/web_schema.sql

### Excel VBA Familiar Frontend (`vba_source`)
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/vba_source/Module_Charts.bas
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/vba_source/Module_DB.bas
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/vba_source/Module_UI.bas

### TypeScript Live Cockpit (`web_platform`)
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/web_platform/api_gateway/.env
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/web_platform/api_gateway/package-lock.json
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/web_platform/api_gateway/package.json
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/web_platform/api_gateway/tsconfig.json
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/web_platform/api_gateway/src/server.ts
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/web_platform/api_gateway/src/services/DatabaseService.ts
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/web_platform/frontend/package-lock.json
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/web_platform/frontend/package.json
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/web_platform/frontend/postcss.config.js
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/web_platform/frontend/tailwind.config.ts
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/web_platform/frontend/app/globals.css
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/web_platform/frontend/app/layout.tsx
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/web_platform/frontend/app/page.tsx
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/web_platform/frontend/src/components/LiveRaceDashboard.tsx
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/web_platform/frontend/src/components/RaceCard.tsx
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/web_platform/frontend/src/components/ScoreBadge.tsx
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/web_platform/frontend/src/components/TrifectaFactors.tsx
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/web_platform/frontend/src/hooks/useRealTimeRaces.ts
https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/main/web_platform/frontend/src/types/racing.ts