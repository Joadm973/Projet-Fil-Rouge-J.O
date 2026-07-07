# 🏅 YPerf - Analyse des Performances Olympiques pour les JO 2028

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.139-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
![Usage](https://img.shields.io/badge/Usage-P%C3%A9dagogique_Ynov_B3-green.svg)

> **Projet Fil Rouge - Bachelor 3 Ynov Informatique**  
> UF : Spécialité Data & IA

## 📋 Description

**YPerf** est une application de data storytelling permettant d'explorer les performances historiques des Jeux Olympiques et de prédire les tendances pour les JO 2028 à Los Angeles.

### Objectifs du projet

- 📊 Analyser les résultats des JO précédents par sport, pays et genre
- 📈 Visualiser l'évolution des performances sportives par discipline
- 🔍 Identifier les athlètes et pays en progression
- 🎯 Créer des prédictions pour les JO 2028

## 🚀 Installation

### Prérequis

- Python 3.10 ou supérieur
- Node.js 18 ou supérieur (avec npm)
- Git

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone https://github.com/Joadm973/Projet-Fil-Rouge-J.O.git
cd Projet-Fil-Rouge-J.O
```

2. **Backend — créer un environnement virtuel et installer les dépendances**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

3. **Frontend — installer les dépendances**
```bash
cd frontend
npm install
cd ..
```

4. **Placer le dataset**
```
Assurez-vous que le fichier olympics_dataset.csv est dans data/raw/
```

## 💻 Utilisation

### Lancer le backend (FastAPI)

```bash
.venv\Scripts\python -m uvicorn backend.main:app --port 8000 --reload
```

L'API est accessible à l'adresse : `http://localhost:8000` (documentation interactive sur `http://localhost:8000/docs`).

### Lancer le frontend (React/Vite)

```bash
cd frontend
npm run dev
```

L'application est accessible à l'adresse : `http://localhost:5174` (proxy `/api` → backend `:8000`).

### Explorer les notebooks

```bash
jupyter notebook notebooks/
```

### Lancer les tests unitaires

```bash
.venv\Scripts\python -m pytest tests/ -v
```

## 📚 Documentation

| Document | Contenu |
|---|---|
| [docs/installation.md](docs/installation.md) | Guide d'installation pas à pas |
| [docs/user_guide.md](docs/user_guide.md) | Manuel d'utilisation de l'application (pages, filtres, onglets) |
| [docs/technical_doc.md](docs/technical_doc.md) | Architecture, pipeline de données, API, modèles ML |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Workflow Git de l'équipe (branches, conventions de commits) |

## 📁 Structure du projet

```
Projet-Fil-Rouge-J.O/
├── backend/                      # API FastAPI
│   ├── main.py                   # Point d'entrée, montage des routers, CORS
│   ├── deps.py                   # Chargement du DataFrame en cache (get_df)
│   └── routers/                  # Endpoints REST par domaine (home, exploration, athletes,
│                                  #   predictions, annotations, generations, multisource)
├── frontend/                     # Application React + Vite + TypeScript
│   └── src/
│       ├── pages/                # 7 pages (Home, Exploration, Athletes, Predictions,
│                                  #   Annotations, Generations, Multisource)
│       ├── components/           # Composants réutilisables (PlotlyChart, Sidebar, etc.)
│       └── lib/                  # Client API, config Plotly
├── src/                          # Code source d'analyse et de modélisation (partagé)
│   ├── data/                     # Chargement et nettoyage des données, World Bank API
│   ├── analysis/                 # Analyses exploratoires et statistiques (χ², Gini, Pearson)
│   ├── models/                   # Modèles ML, cotes, générations, records, annotations
│   └── app/                      # Ancienne application Streamlit (legacy, non déployée)
├── notebooks/                    # Jupyter Notebooks (démarche du projet)
├── data/
│   ├── raw/                      # Données brutes
│   └── processed/                # Données traitées / cache API
├── docs/                         # Documentation
├── tests/                        # Tests unitaires
├── requirements.txt              # Dépendances Python (backend)
├── config.py                     # Configuration du projet
└── README.md
```

## 📊 Dataset

Le dataset `olympics_dataset.csv` contient les données historiques des Jeux Olympiques :

| Colonne | Description |
|---------|-------------|
| player_id | Identifiant unique de l'athlète |
| Name | Nom de l'athlète |
| Sex | Genre (M/F) |
| Team | Équipe/Pays |
| NOC | Code pays (3 lettres) |
| Year | Année des JO |
| Season | Saison (`Summer` uniquement dans ce dataset) |
| City | Ville hôte |
| Sport | Sport |
| Event | Épreuve |
| Medal | Médaille obtenue |

## 🛠️ Technologies utilisées

- **Python & FastAPI** — API REST
- **Pandas & NumPy** — Manipulation des données
- **Scikit-learn** — Machine Learning
- **React 19 + TypeScript + Vite** — Frontend SPA
- **TanStack React Query** — Fetching et cache des données côté client
- **Plotly.js** — Visualisations interactives
- **Jupyter Notebook** — Analyses exploratoires

## 👥 Équipe

- **Josué Adami** - [GitHub](https://github.com/Joadm973)
- **Nicolas Gouy** - [GitHub](https://github.com/gonicolas12)

## 📝 License

Ce projet est réalisé dans le cadre pédagogique du Bachelor 3 Ynov Informatique.

---

*Projet réalisé pour l'UF Spécialité Data & IA - Ynov Informatique*
