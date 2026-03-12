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
│   │   └── statistics.py         # Indicateurs statistiques
│   ├── models/
│   │   ├── predictor.py          # Modèle de prédiction JO 2028
│   │   └── evaluator.py          # Évaluation des modèles ML
│   ├── visualization/
│   │   ├── charts.py             # Graphiques Plotly / Matplotlib
│   │   └── maps.py               # Cartes choroplèthes
│   └── app/
│       ├── app.py                # Point d'entrée Streamlit
│       ├── views/                # Pages de l'application
│       │   ├── home.py
│       │   ├── exploration.py
│       │   ├── athletes.py
│       │   └── predictions.py
│       └── components/           # Composants réutilisables (cards, filtres)
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
                    ├── Ajout colonne Has_Medal (0/1)
                    └── DataFrame prêt pour l'analyse
```

## Modèle de Machine Learning

**Algorithme :** Régression Linéaire (`sklearn.linear_model.LinearRegression`)  
**Fichier :** `src/models/predictor.py`

### Fonctionnement

Un modèle indépendant est entraîné **par pays** :

1. Calcul du total de médailles par pays par édition
2. Entraînement d'une régression linéaire sur la série temporelle `Year → Total médailles`
3. Prédiction pour `Year = 2028`
4. Les valeurs négatives sont ramenées à 0

**Paramètres ML** (définis dans `config.py`) :

| Paramètre | Valeur |
|---|---|
| `test_size` | 0.2 |
| `random_state` | 42 |
| `cv_folds` | 5 |

### Limites connues

- Les pays disparus (URSS, RDA) ont des séries longues et des valeurs élevées qui faussent le classement prédit
- La régression linéaire extrapole sans contrainte : les prédictions doivent être interprétées comme des tendances, pas des certitudes

## Navigation de l'application

L'application utilise une navigation **manuelle** via `st.radio()` dans la sidebar.  
Le dossier contenant les pages s'appelle `views/` (et non `pages/`) pour éviter la détection automatique multi-pages de Streamlit.

| Page | Fichier | Description |
|---|---|---|
| Accueil | `views/home.py` | KPIs, médailles par édition, participation |
| Exploration | `views/exploration.py` | Filtres, top pays, carte, évolution |
| Athlètes | `views/athletes.py` | Top athlètes, détail médailles, tableau |
| Prédictions 2028 | `views/predictions.py` | Modèle ML, projections par pays |

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
