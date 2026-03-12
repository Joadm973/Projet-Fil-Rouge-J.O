# 🏅 YPerf - Analyse des Performances Olympiques pour les JO 2028

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

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
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone https://github.com/Joadm973/Projet-Fil-Rouge-J.O.git
cd Projet-Fil-Rouge-J.O
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Placer le dataset**
```
Assurez-vous que le fichier olympics_dataset.csv est dans data/raw/
```

## 💻 Utilisation

### Lancer l'application Streamlit

```bash
python -m streamlit run src/app/app.py
```

L'application sera accessible à l'adresse : `http://localhost:8501`

### Explorer les notebooks

```bash
jupyter notebook notebooks/
```

## 📁 Structure du projet

```
Projet-Fil-Rouge-J.O/
├── src/                          # Code source
│   ├── data/                     # Chargement et nettoyage des données
│   ├── analysis/                 # Analyses exploratoires et statistiques
│   ├── models/                   # Modèles de machine learning
│   ├── visualization/            # Graphiques et cartes
│   └── app/                      # Application Streamlit
│       ├── views/                # Pages de l'application (home, exploration, athletes, predictions)
│       └── components/           # Composants réutilisables
├── notebooks/                    # Jupyter Notebooks
├── data/
│   ├── raw/                      # Données brutes
│   └── processed/                # Données traitées
├── docs/                         # Documentation
├── tests/                        # Tests unitaires
├── assets/                       # Images et ressources
├── requirements.txt              # Dépendances Python
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
| Season | Saison (Summer/Winter) |
| City | Ville hôte |
| Sport | Sport |
| Event | Épreuve |
| Medal | Médaille obtenue |

## 🛠️ Technologies utilisées

- **Python** - Langage principal
- **Pandas & NumPy** - Manipulation des données
- **Scikit-learn** - Machine Learning
- **Matplotlib & Seaborn** - Visualisations statiques
- **Plotly** - Visualisations interactives
- **Streamlit** - Application web interactive
- **Jupyter Notebook** - Analyses exploratoires

## 👥 Équipe

- **Josué Adami** - [GitHub](https://github.com/Joadm973)
- **Nicolas Gouy** - [GitHub](https://github.com/gonicolas12)

## 📝 License

Ce projet est réalisé dans le cadre pédagogique du Bachelor 3 Ynov Informatique.

---

*Projet réalisé pour l'UF Spécialité Data & IA - Ynov Informatique*