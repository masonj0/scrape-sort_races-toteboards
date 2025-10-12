# Fortuna Faucet: CORE Application Manifest

**Purpose:** To provide a complete, verified list of all files constituting the CORE two-pillar application (`python_service` and `web_platform`).

---

## 1.0 Python Backend (`python_service`)

### Core
- `python_service/__init__.py`
- `python_service/api.py`
- `python_service/analyzer.py`
- `python_service/config.py`
- `python_service/engine.py`
- `python_service/logging_config.py`
- `python_service/models.py`
- `python_service/security.py`
- `python_service/cache_manager.py`
- `python_service/etl.py`
- `python_service/middleware/error_handler.py`
- `python_service/models_v3.py`


### Adapters
- `python_service/adapters/__init__.py`
- `python_service/adapters/base.py`
- `python_service/adapters/utils.py`
- `python_service/adapters/template_adapter.py`
- `python_service/adapters/betfair_adapter.py`
- `python_service/adapters/betfair_greyhound_adapter.py`
- `python_service/adapters/greyhound_adapter.py`
- `python_service/adapters/harness_adapter.py`
- `python_service/adapters/at_the_races_adapter.py`
- `python_service/adapters/racing_and_sports_adapter.py`
- `python_service/adapters/tvg_adapter.py`
- `python_service/adapters/oddschecker_adapter.py`
- `python_service/adapters/sporting_life_adapter.py`
- `python_service/adapters/timeform_adapter.py`
- `python_service/adapters/drf_adapter.py`
- `python_service/adapters/equibase_adapter.py`
- `python_service/adapters/racingpost_adapter.py`
- `python_service/adapters/racingtv_adapter.py`
- `python_service/adapters/tab_adapter.py`
- `python_service/adapters/brisnet_adapter.py`
- `python_service/adapters/fanduel_adapter.py`
- `python_service/adapters/horseracingnation_adapter.py`
- `python_service/adapters/nyrabets_adapter.py`
- `python_service/adapters/punters_adapter.py`
- `python_service/adapters/twinspires_adapter.py`
- `python_service/adapters/xpressbet_adapter.py`
- `python_service/adapters/universal_adapter.py`
- `python_service/adapters/racing_and_sports_greyhound_adapter.py`
- `python_service/adapters/pointsbet_greyhound_adapter.py`
- `python_service/adapters/gbgb_api_adapter.py`
- `python_service/adapters/betfair_auth_mixin.py`
- `python_service/adapters/base_v3.py`
- `python_service/adapters/betfair_datascientist_adapter.py`


## 2.0 TypeScript Frontend (`web_platform`)

- `web_platform/frontend/package.json`
- `web_platform/frontend/postcss.config.js`
- `web_platform/frontend/tailwind.config.ts`
- `web_platform/frontend/tsconfig.json`
- `web_platform/frontend/src/components/RaceCard.tsx`
