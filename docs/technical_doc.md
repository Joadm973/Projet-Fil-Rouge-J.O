# Documentation Technique — YPerf

## Architecture du projet

```
Projet-Fil-Rouge-J.O/
├── config.py                     # Chemins, paramètres globaux, config Streamlit
├── requirements.txt              # Dépendances Python
├── data/
│   ├── raw/                      # Données brutes (olympics_dataset.csv)
│   └── processed/                # Fichiers CSV intermédiaires générés
├── src/
│   ├── data/
│   │   ├── data_loader.py        # Lecture du CSV brut
│   │   └── data_cleaner.py       # Nettoyage et feature engineering
│   ├── analysis/
│   │   ├── exploratory.py        # Agrégats métier (médailles par pays, athlètes, etc.)
│   │   └── statistics.py         # Stats descriptives & inférentielles (χ², Gini, Pearson)
│   ├── data/
│   │   ├── data_loader.py        # Lecture du CSV brut
│   │   ├── data_cleaner.py       # Nettoyage et feature engineering
│   │   └── api_fetcher.py        # World Bank API (population, PIB, région) + cache JSON
│   ├── models/
│   │   ├── predictor.py          # Modèle de prédiction JO 2028 (nations actives)
│   │   ├── evaluator.py          # Métriques & comparaison des modèles ML
│   │   ├── ratings.py            # Côtes de dominance par discipline + recommandations 2028
│   │   ├── records.py            # Timeline des records olympiques par édition
│   │   ├── generations.py        # Détection nouvelles générations (débuts, breakouts, renouvellement)
│   │   └── annotations.py        # CRUD annotations utilisateurs (stockage JSON local)
│   └── app/
│       ├── app.py                # Point d'entrée Streamlit
│       ├── views/                # Pages de l'application
│       │   ├── home.py
│       │   ├── exploration.py
│       │   ├── athletes.py
│       │   ├── predictions.py    # Inclut onglets Côtes & Timeline
│       │   ├── annotations.py    # Page annotations utilisateurs
│       │   ├── generations.py    # Page nouvelles générations
│       │   └── multisource.py    # Page analyse multi-sources
│       └── components/           # Composants réutilisables (cards, style)
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_analysis.ipynb
│   └── 04_modeling.ipynb
├── tests/
│   ├── test_data.py
└───   └── test_models.py
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

## Pipeline de données

```
olympics_dataset.csv
    └── data_loader.load_raw_data()
            └── data_cleaner.clean_data()
                    ├── Filtre : Season == "Summer"
                    ├── Suppression des doublons
                    ├── Fusion des NOC historiques :
                    │       GDR/FRG → GER, ROC → RUS, SCG → SRB, BOH → CZE
                    ├── Ajout colonne Has_Medal (0/1)
                    └── DataFrame prêt pour l'analyse
```

## Modèle de Machine Learning

**Algorithmes :** Régression Linéaire, Ridge, Gradient Boosting, Régression Polynomiale (deg. 2)  
**Fichiers :** `src/models/predictor.py` (modèle de référence), `src/app/views/predictions.py` (comparaison multi-modèles), `src/models/evaluator.py` (métriques)

### Fonctionnement

Un modèle indépendant est entraîné **par pays** :

1. Calcul du total de médailles par pays par édition
2. **Filtrage aux nations actives** : seuls les pays présents à au moins une édition depuis 2016 sont prédits (`get_active_nocs`)
3. Entraînement sur la série temporelle `Year → Total médailles`
4. Prédiction pour `Year = 2028`
5. Les valeurs négatives sont ramenées à 0

### Évaluation

`src/models/evaluator.py` fournit les métriques **MAE**, **RMSE** et **R²**, ainsi qu'une
validation croisée temporelle (`TimeSeriesSplit`). L'onglet « Comparaison modèles » de
l'application affiche ces scores pour comparer les algorithmes sur un pays donné.

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

## Navigation de l'application

L'application utilise une navigation **manuelle** via `st.radio()` dans la sidebar.  
Le dossier contenant les pages s'appelle `views/` (et non `pages/`) pour éviter la détection automatique multi-pages de Streamlit.

| Page | Fichier | Description |
|---|---|---|
| Accueil | `views/home.py` | KPIs, médailles par édition, participation |
| Exploration | `views/exploration.py` | Filtres, top pays, carte, évolution |
| Athlètes | `views/athletes.py` | Top athlètes, détail médailles, tableau |
| Prédictions 2028 | `views/predictions.py` | Modèle ML, projections + Côtes & Timeline (7 onglets) |
| Annotations | `views/annotations.py` | Notes utilisateurs sur athlètes/pays/sports/éditions |
| Nouvelles générations | `views/generations.py` | Talents 2016+, breakouts 2020+, renouvellement, nouvelles nations |
| Multi-sources | `views/multisource.py` | Fusion CSV × World Bank API (per-capita, région, PIB) |

## Modules d'analyse complémentaires

### `src/models/ratings.py` — Côtes de dominance

| Fonction | Description |
|---|---|
| `compute_sport_dominance(df)` | % de médailles par pays par sport depuis 2016 (HHI inclus) |
| `compute_athlete_ratings(df)` | Score pondéré Or=3/Argent=2/Bronze=1 + bonus régularité (+15%/édition) |
| `generate_recommendations(df)` | Nations en progression, sports ouverts/dominés, spotlight France |

### `src/models/records.py` — Timeline

| Fonction | Description |
|---|---|
| `get_edition_summary(df, year)` | Top pays/athlètes, nouvelles disciplines, débuts historiques pour une édition |
| `get_all_time_records(df)` | Meilleures performances nationales et individuelles toutes éditions |
| `get_first_medals_timeline(df)` | Cumul des pays ayant remporté leur 1ère médaille par année |

### `src/models/generations.py` — Nouvelles générations

| Fonction | Description |
|---|---|
| `detect_new_gen_athletes(df)` | Athlètes débutant en 2016+, classés par score pondéré |
| `detect_breakout_athletes(df)` | Athlètes sans médaille avant 2020, percée récente |
| `detect_generation_shift(df)` | Taux de renouvellement des top 10 dominants par sport |
| `detect_new_medaling_nations(df)` | Pays remportant leur 1ère médaille depuis 2016 |

### `src/models/annotations.py` — Annotations

Stockage JSON dans `data/annotations.json`. CRUD complet :
- `add_annotation(type, target, note, author, tags)` → crée et sauvegarde
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
| `APP_CONFIG` | Paramètres `set_page_config` Streamlit |
| `COLORS` | Palette de couleurs (or, argent, bronze, primaire) |
| `ML_CONFIG` | Paramètres du modèle ML |
| `TARGET_YEAR` | Année cible des prédictions (2028) |
