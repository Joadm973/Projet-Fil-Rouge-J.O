# Guide d'installation — YPerf

## Prérequis

- Python **3.10** ou supérieur
- `pip` (inclus avec Python)
- Git

## 1. Cloner le dépôt

```bash
git clone https://github.com/Joadm973/Projet-Fil-Rouge-J.O.git
cd Projet-Fil-Rouge-J.O
```

## 2. Créer un environnement virtuel

```bash
python -m venv venv
```

Activation :

| OS | Commande |
|---|---|
| Windows | `venv\Scripts\activate` |
| Linux / macOS | `source venv/bin/activate` |

## 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

Principales bibliothèques installées :

| Bibliothèque | Version | Usage |
|---|---|---|
| pandas | 2.1.4 | Manipulation des données |
| numpy | 1.26.2 | Calculs numériques |
| scikit-learn | 1.3.2 | Machine Learning |
| statsmodels | 0.14.1 | Modèles statistiques |
| matplotlib | 3.8.2 | Visualisations statiques |
| seaborn | 0.13.0 | Visualisations statiques |
| plotly | 5.18.0 | Visualisations interactives |
| streamlit | 1.29.0+ | Application web |
| jupyter | 1.0.0 | Notebooks |
| pytest | 7.4.3 | Tests unitaires |

## 4. Placer le dataset

S'assurer que le fichier `olympics_dataset.csv` est présent dans :

```
data/raw/olympics_dataset.csv
```

> Le fichier contient l'historique des Jeux Olympiques d'été (1896–2024)  
> avec 252 565 lignes et les colonnes : `player_id`, `Name`, `Sex`, `Team`, `NOC`, `Year`, `Season`, `City`, `Sport`, `Event`, `Medal`.

## 5. Lancer l'application

```bash
python -m streamlit run src/app/app.py
```

Ouvrir ensuite : [http://localhost:8501](http://localhost:8501)

## 6. (Optionnel) Lancer les notebooks

```bash
jupyter notebook notebooks/
```

## 7. (Optionnel) Lancer les tests

```bash
python -m pytest tests/ -v
```

## Problèmes courants

| Problème | Solution |
|---|---|
| `streamlit` non reconnu | Utiliser `python -m streamlit run ...` |
| `ModuleNotFoundError` | Vérifier que l'environnement virtuel est activé et que `pip install -r requirements.txt` a été exécuté |
| Dataset introuvable | Vérifier que `olympics_dataset.csv` est dans `data/raw/` |
