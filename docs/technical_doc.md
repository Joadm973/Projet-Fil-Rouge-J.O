# Documentation Technique — YPerf

## Architecture du projet

L'application est composée de deux processus distincts : une **API FastAPI** (backend) qui expose les données et modèles, et une **SPA React/Vite** (frontend) qui les consomme via HTTP (`fetch` + TanStack React Query). Le code d'analyse et de modélisation (`src/`) est partagé et importé directement par les routers FastAPI.

```
Projet-Fil-Rouge-J.O/
├── config.py                     # Chemins, paramètres globaux
├── requirements.txt              # Dépendances Python (backend + analyse)
├── data/
│   ├── raw/                      # Données brutes (olympics_dataset.csv)
│   └── processed/                # Cache World Bank API, fichiers intermédiaires
├── backend/                      # API FastAPI
│   ├── main.py                   # Point d'entrée, montage des routers, CORS
│   ├── deps.py                   # get_df() — chargement + nettoyage en cache (lru_cache)
│   └── routers/
│       ├── home.py               # KPIs, médailles par édition, participation
│       ├── exploration.py        # Top pays/sports, tendances, heatmap, choroplèthe
│       ├── athletes.py           # Classement athlètes, détail, filtres
│       ├── predictions.py        # Modèle ML 2028, côtes, domination, recommandations, timeline
│       ├── annotations.py        # CRUD annotations utilisateurs
│       ├── generations.py        # Nouveaux talents, breakouts, renouvellement, nouvelles nations
│       └── multisource.py        # Fusion CSV × World Bank API
├── frontend/                     # Application React + TypeScript + Vite
│   ├── vite.config.ts            # Proxy /api → http://localhost:8000
│   └── src/
│       ├── pages/                # Home, Exploration, Athletes, Predictions, Annotations,
│       │                         #   Generations, Multisource
│       ├── components/           # PlotlyChart, Sidebar, Tabs, SectionHeader, InsightBox…
│       └── lib/                  # Client API (fetchJSON, api), config Plotly (couleurs, marges)
├── src/                          # Code source d'analyse et de modélisation (partagé)
│   ├── data/
│   │   ├── data_loader.py        # Lecture du CSV brut
│   │   ├── data_cleaner.py       # Nettoyage et feature engineering
│   │   └── api_fetcher.py        # World Bank API (population, PIB, région) + cache JSON
│   ├── analysis/
│   │   ├── exploratory.py        # Agrégats métier (médailles par pays, athlètes, etc.)
│   │   └── statistics.py         # Stats descriptives & inférentielles (χ², Gini, Pearson)
│   ├── models/
│   │   ├── predictor.py          # Modèle de prédiction JO 2028 (nations actives)
│   │   ├── evaluator.py          # Métriques & comparaison des modèles ML
│   │   ├── ratings.py            # Côtes de dominance par discipline + recommandations 2028
│   │   ├── records.py            # Timeline des records olympiques par édition
│   │   ├── generations.py        # Détection nouvelles générations (débuts, breakouts, renouvellement)
│   │   └── annotations.py        # CRUD annotations utilisateurs (stockage JSON local)
│   └── app/                      # Ancienne application Streamlit (legacy, non déployée)
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_analysis.ipynb
│   ├── 04_modeling.ipynb
│   └── 05_nouvelles_analyses.ipynb   # Côtes, générations, records, multi-sources
├── tests/
│   ├── conftest.py                   # Fixture : mini-dataset synthétique
│   ├── test_data.py
│   ├── test_analysis.py
│   └── test_models.py
```

## Dataset

**Fichier :** `data/raw/olympics_dataset.csv`  
**Lignes :** 252 565  
**Couverture :** JO d'été, 1896–2024

| Colonne | Type | Description |
|---|---|---|
| `player_id` | int | Identifiant unique de l'athlète |
| `Name` | str | Nom de l'athlète |
| `Sex` | str | Genre (`M` / `F`) |
| `Team` | str | Nom complet du pays |
| `NOC` | str | Code pays ISO 3 lettres |
| `Year` | int | Année de l'édition |
| `Season` | str | Saison (`Summer` uniquement) |
| `City` | str | Ville hôte |
| `Sport` | str | Discipline sportive |
| `Event` | str | Épreuve précise |
| `Medal` | str | `Gold` / `Silver` / `Bronze` / `No medal` |

> Le dataset ne contient **aucune colonne d'âge, taille ou poids** — toute fonctionnalité basée sur ces attributs (ex. pyramide des âges) n'est pas réalisable avec ces données.

## Pipeline de données

```
olympics_dataset.csv
    └── data_loader.load_raw_data()
            └── data_cleaner.clean_data()
                    ├── Filtre : Season == "Summer"
                    ├── Suppression des doublons
                    ├── Correction de ~30 noms d'athlètes corrompus dans le CSV source
                    ├── Harmonisation des noms « NOM Prénom » des éditions 2020+
                    │       ("McKEON Emma" → "Emma Mckeon" — sinon les carrières
                    │       sont scindées en deux identités entre 2016 et 2020)
                    ├── Fusion des NOC historiques :
                    │       GDR/FRG → GER, ROC → RUS, SCG → SRB, BOH → CZE
                    ├── Standardisation des noms d'équipe : un NOC = un libellé unique
                    │       (élimine les clubs 1904 "Vesper Boat Club" et les suffixes
                    │       d'embarcation "United States-1" qui dupliquaient les pays)
                    ├── Ajout colonne Has_Medal (0/1)
                    └── DataFrame prêt pour l'analyse
```

Le module expose aussi `is_ambiguous_athlete_name()` : certains noms tronqués du CSV
source (« William Jr. », « John Jr. ») regroupent plusieurs athlètes réels sous un même
libellé, sans réattribution possible. Ces noms sont **exclus des classements individuels**
(côtes, top athlètes, générations) mais leurs médailles restent comptées au niveau pays.

Côté backend, `backend/deps.py::get_df()` appelle ce pipeline une seule fois par processus
(`functools.lru_cache(maxsize=1)`). **Un changement dans `data_cleaner.py` ou dans le CSV
nécessite un redémarrage du processus uvicorn** — `--reload` recharge le code mais pas
nécessairement ce cache si un processus orphelin reste lié au port.

## API FastAPI (`backend/`)

Toutes les routes sont préfixées par `/api/<domaine>` et déclarées dans `backend/main.py`.
CORS autorise les origines de développement locales (`http://localhost:5173`, `:5174` et `:3000`).

| Router | Prefix | Endpoints principaux |
|---|---|---|
| `home` | `/api/home` | `kpis`, `medals-by-year`, `gender-participation`, `medals-by-country`, `participation`, `medals-by-sport` |
| `exploration` | `/api/exploration` | `meta`, `top-countries`, `top-sports`, `trends`, `heatmap`, `choropleth` |
| `athletes` | `/api/athletes` | `filters-meta`, `top`, `gender-medals`, `detail`, `timeline` |
| `predictions` | `/api/predictions` | `predict`, `country-trend`, `athlete-ratings`, `dominance`, `recommendations`, `editions`, `edition-summary`, `timeline-diversity` |
| `annotations` | `/api/annotations` | `GET /`, `POST /`, `DELETE /{id}`, `targets` |
| `generations` | `/api/generations` | `new-gen`, `breakouts`, `generation-shift`, `new-nations` |
| `multisource` | `/api/multisource` | `overview`, `per-capita`, `scatter`, `by-region`, `region-trend`, `gdp-scatter`, `table` |

`GET /api/health` renvoie `{"status": "ok"}` pour un check de disponibilité.

## Frontend (`frontend/`)

- **React 19 + TypeScript + Vite**, routage via `react-router-dom`.
- **TanStack React Query** pour le fetching : chaque page déclare ses `useQuery` avec une
  `queryKey` incluant les filtres actifs (période, genre, top N…), ce qui déclenche
  automatiquement un refetch quand un filtre change.
- **Plotly.js** (`react-plotly.js`) pour tous les graphiques, via le composant partagé
  `components/PlotlyChart.tsx` et la config commune `lib/plotly.ts` (palette de couleurs,
  marges par défaut).
- Le proxy Vite (`vite.config.ts`) redirige `/api/*` vers `http://localhost:8000` en dev.

## Modèle de Machine Learning

**Algorithmes :** Régression Linéaire, Ridge, Gradient Boosting, Régression Polynomiale (deg. 2)  
**Fichiers :** `src/models/predictor.py` (modèle de référence), `backend/routers/predictions.py`
(exposition API du modèle sélectionné), `src/models/evaluator.py` (métriques)

### Fonctionnement

Un modèle indépendant est entraîné **par pays** :

1. Calcul du total de médailles par pays par édition
2. **Filtrage aux nations actives** : seuls les pays présents à au moins une édition depuis 2016 sont prédits (`get_active_nocs`)
3. Entraînement sur la série temporelle `Year → Total médailles`
4. Prédiction pour `Year = 2028`
5. Les valeurs négatives sont ramenées à 0

### Évaluation

`src/models/evaluator.py` fournit les métriques **MAE**, **RMSE** et **R²**, ainsi qu'une
validation croisée temporelle (`TimeSeriesSplit`).

**Paramètres ML** (définis dans `config.py`) :

| Paramètre | Valeur |
|---|---|
| `test_size` | 0.2 |
| `random_state` | 42 |
| `cv_folds` | 5 |

### Limites connues

- Les nations disparues (URSS, RDA, Tchécoslovaquie) sont **exclues des projections** via le filtre `get_active_nocs`, car leurs séries historiques fausseraient le classement 2028
- La régression linéaire extrapole sans contrainte : les prédictions doivent être interprétées comme des tendances, pas des certitudes
- Le modèle ne tient pas compte des changements de programme olympique (nouvelles disciplines) ni du contexte géopolitique

## Modules d'analyse complémentaires

### `src/models/ratings.py` — Côtes de dominance

| Fonction | Description |
|---|---|
| `compute_sport_dominance(df)` | % de médailles par pays par sport depuis 2016 |
| `compute_athlete_ratings(df)` | Score pondéré Or=3/Argent=2/Bronze=1 + bonus régularité (+15%/édition), noms ambigus exclus |
| `generate_recommendations(df)` | Nations en progression, sports ouverts/dominés (indice HHI), spotlight France |

Exposé côté API par `backend/routers/predictions.py` : `athlete-ratings` (`compute_athlete_ratings`),
`dominance` (`compute_sport_dominance`), `recommendations` (`generate_recommendations`).

### `src/models/records.py` — Timeline

| Fonction | Description |
|---|---|
| `get_edition_summary(df, year)` | Top pays/athlètes, nouvelles disciplines, débuts historiques pour une édition |
| `get_all_time_records(df)` | Meilleures performances nationales et individuelles toutes éditions |
| `get_first_medals_timeline(df)` | Cumul des pays ayant remporté leur 1ère médaille par année |

### `src/models/generations.py` — Nouvelles générations

| Fonction | Description | Colonnes retournées |
|---|---|---|
| `detect_new_gen_athletes(df)` | Athlètes débutant en 2016+, classés par score pondéré | `Name, Team, Sport, debut_year, nb_editions, nb_medals, gold, silver, bronze, score` |
| `detect_breakout_athletes(df)` | Athlètes sans médaille avant 2020, percée récente | `Name, Team, Sport, first_medal_year, medals_recent, gold, silver, bronze, score` |
| `detect_generation_shift(df)` | Taux de renouvellement des top 10 dominants par sport (2008–2016 vs 2020–2024) | `Sport, top_old_count, top_new_count, overlap, renewal_rate` |
| `detect_new_medaling_nations(df)` | Pays remportant leur 1ère médaille depuis 2016 | `NOC, Team, first_medal_year, medals_total, Sports` |

### `src/models/annotations.py` — Annotations

Stockage JSON dans `data/annotations.json`. CRUD complet :
- `add_annotation(type, target, note, author, tags)` → crée et sauvegarde (champ `timestamp`)
- `get_annotations(type, target)` → filtre par type/cible
- `delete_annotation(id)` → suppression par UUID

### `src/data/api_fetcher.py` — World Bank API

Appelle 3 endpoints REST :
- `/v2/country` → région, niveau de revenu, capitale
- `/v2/country/all/indicator/SP.POP.TOTL` → population (dernière année disponible)
- `/v2/country/all/indicator/NY.GDP.PCAP.CD` → PIB par habitant (USD)

Cache local : `data/processed/countries_api.json`.  
Mapping NOC → ISO3 pour 100+ codes olympiques non-standard.

## Configuration (`config.py`)

| Variable | Description |
|---|---|
| `ROOT_DIR` | Répertoire racine du projet |
| `RAW_OLYMPICS_FILE` | Chemin vers le CSV brut |
| `CLEANED_DATA_FILE` | Chemin vers le CSV nettoyé |
| `COLORS` | Palette de couleurs (or, argent, bronze, primaire) |
| `ML_CONFIG` | Paramètres du modèle ML |
| `TARGET_YEAR` | Année cible des prédictions (2028) |

## Application Streamlit (legacy)

Une première version de l'interface a été construite avec Streamlit (`src/app/`). Elle reste
présente dans le dépôt pour référence mais n'est plus maintenue ni déployée — l'interface
active est l'application React (`frontend/`) servie par l'API FastAPI (`backend/`).
