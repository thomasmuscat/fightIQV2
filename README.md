# FightIQ Data Engine GitHub V2

Scraper cloud gratuit via GitHub Actions pour récupérer les données UFC Stats et générer/importer les CSV Supabase de FightIQ.

## Contenu important

- `.github/workflows/fightiq-sync.yml` : workflow GitHub Actions
- `main.py` : lance le scraper
- `scraper/` : modules UFC Stats
- `database/` : export CSV et upload Supabase
- `exports/` : CSV générés
- `docs/SUPABASE_SETUP.md` : configuration Supabase

## Première exécution recommandée

Dans GitHub > Actions > FightIQ UFCStats Sync > Run workflow :

- `upload_to_supabase` : `false`
- `max_events` : `5`
- `max_fighters` : `20`

Ça teste le scraper sans toucher à Supabase.

## Après test réussi

Ajoute les secrets GitHub :

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

Puis relance avec :

- `upload_to_supabase` : `true`

## Artifacts

Après chaque run, les fichiers CSV sont disponibles dans les artifacts GitHub Actions.
