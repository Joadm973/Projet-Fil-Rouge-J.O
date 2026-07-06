# Guide d'installation — YPerf

## Prérequis

- Python **3.10** ou supérieur
- `pip` (inclus avec Python)
- Node.js **18** ou supérieur (avec `npm`)
- Git

## 1. Cloner le dépôt

```bash
git clone https://github.com/Joadm973/Projet-Fil-Rouge-J.O.git
cd Projet-Fil-Rouge-J.O
```

## 2. Backend — créer un environnement virtuel

```bash
python -m venv .venv
```

Activation :

| OS | Commande |
|---|---|
| Windows | `.venv\Scripts\activate` |
| Linux / macOS | `source .venv/bin/activate` |

## 3. Backend — installer les dépendances

```bash
pip install -r requirements.txt
```

Principales bibliothèques installées :

| Bibliothèque | Usage |
|---|---|
| fastapi | API REST |
| uvicorn | Serveur ASGI |
| pandas | Manipulation des données |
| numpy | Calculs numériques |
| scikit-learn | Machine Learning |
| statsmodels | Modèles statistiques |
| matplotlib / seaborn | Visualisations statiques (notebooks) |
| jupyter | Notebooks |
| pytest | Tests unitaires |

## 4. Frontend — installer les dépendances

```bash
cd frontend
npm install
cd ..
```

Principales dépendances : React 19, TypeScript, Vite, TanStack React Query, Plotly.js (`react-plotly.js`), React Router.

## 5. Placer le dataset

S'assurer que le fichier `olympics_dataset.csv` est présent dans :

```
data/raw/olympics_dataset.csv
```

> Le fichier contient l'historique des Jeux Olympiques d'été (1896–2024)  
> avec 252 565 lignes et les colonnes : `player_id`, `Name`, `Sex`, `Team`, `NOC`, `Year`, `Season`, `City`, `Sport`, `Event`, `Medal`.

## 6. Lancer le backend

```bash
.venv\Scripts\python -m uvicorn backend.main:app --port 8000 --reload
```

L'API tourne sur [http://localhost:8000](http://localhost:8000) (docs interactives : `/docs`).

## 7. Lancer le frontend

Dans un second terminal :

```bash
cd frontend
npm run dev
```

Ouvrir ensuite : [http://localhost:5173](http://localhost:5173)

## 8. (Optionnel) Lancer les notebooks

```bash
jupyter notebook notebooks/
```

## 9. (Optionnel) Lancer les tests

```bash
python -m pytest tests/ -v
```

## Problèmes courants

| Problème | Solution |
|---|---|
| `ModuleNotFoundError` (backend) | Vérifier que l'environnement virtuel est activé et que `pip install -r requirements.txt` a été exécuté |
| `/api/*` renvoie 404 côté frontend | Vérifier que le backend tourne sur le port 8000 et que le proxy Vite (`vite.config.ts`) pointe dessus |
| Dataset introuvable | Vérifier que `olympics_dataset.csv` est dans `data/raw/` |
| Changement de données backend non pris en compte | `get_df()` est mis en cache (`lru_cache`) — redémarrer le processus uvicorn, pas seulement sauvegarder le fichier |
