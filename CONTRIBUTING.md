# Guide de contribution — Workflow Git

## Modèle de branches (Git Flow adapté)

```
main
 ├── develop
 │    ├── feature/data-acquisition
 │    ├── feature/data-processing
 │    ├── feature/analysis
 │    ├── feature/visualization
 │    ├── feature/modeling
 │    ├── feature/predictions
 │    ├── feature/streamlit-app
 │    ├── feature/documentation
 │    ├── feature/notebooks
 │    ├── feature/finalisation-livrables
 │    └── fix/*                          # corrections ciblées (NOC historiques, Pylint…)
 └── new-front                           # migration FastAPI + React (phase finale)
```

## Description des branches

| Branche | Rôle | Critère d'évaluation |
|---|---|---|
| `main` | Code stable, déployable en production | — |
| `develop` | Branche d'intégration — toutes les features convergent ici avant `main` | — |
| `feature/data-acquisition` | Chargement des données (CSV, API, sources ouvertes) | Acquérir des données (coef. 4) |
| `feature/data-processing` | Nettoyage, formatage, gestion des valeurs manquantes | Préparer et nettoyer (coef. 3) |
| `feature/analysis` | Analyse exploratoire (EDA) et statistiques inférentielles | Explorer et analyser (coef. 3) |
| `feature/visualization` | Graphiques Plotly/Seaborn, cartes choroplèthes | Visualiser des données (coef. 3) |
| `feature/modeling` | Modèles ML (régression, clustering), évaluation des métriques | Appliquer un modèle ML (coef. 4) |
| `feature/predictions` | Prédictions JO 2028, simulations de scénarios | Prédire et recommander (coef. 4) |
| `feature/streamlit-app` | Interface Streamlit interactive (legacy — remplacée depuis par FastAPI + React, voir `docs/technical_doc.md`) | Interface interactive (coef. 2) |
| `feature/documentation` | Docs techniques, guide utilisateur, installation | Documenter (coef. 2) |
| `feature/notebooks` | Jupyter Notebooks (démarche, analyses, visualisations) | Livrable notebook |
| `feature/finalisation-livrables` | Notebooks finaux, suite de tests, corrections avant rendu | Livrables |
| `fix/*` | Corrections ciblées mergées en `--no-ff` (fusion NOC historiques, warnings Pylint…) | — |
| `new-front` | Migration de l'interface Streamlit vers FastAPI + React | Interface interactive (coef. 2) |

## Conventions de commits

Format : `type(scope): message court` — le `scope` est optionnel
(les commits de la phase finale utilisent la forme courte `type: message`).

| Type | Usage |
|---|---|
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correction de bug |
| `docs` | Documentation uniquement |
| `refactor` | Refactoring sans changement fonctionnel |
| `test` | Ajout ou modification de tests |
| `chore` | Maintenance, dépendances |
| `merge` | Merge d'une branche |

**Exemples :**
```bash
feat(data): Implémenter chargement CSV avec gestion d'erreurs
fix(analysis): Corriger calcul du coefficient de Gini
docs(readme): Mettre à jour les instructions d'installation
feat(modeling): Ajouter RandomForestRegressor pour prédictions 2028
```

## Workflow standard

### 1. Démarrer une nouvelle feature

```bash
git checkout develop
git pull origin develop
git checkout -b feature/<nom>
```

### 2. Travailler sur la feature

```bash
# Committer régulièrement avec des messages clairs
git add <fichiers>
git commit -m "feat(scope): description"
```

### 3. Mettre à jour avec develop

```bash
git merge develop --no-edit
# Résoudre les conflits si nécessaire
```

### 4. Pousser et ouvrir une Pull Request

```bash
git push origin feature/<nom>
# Aller sur GitHub → New Pull Request → feature/<nom> → develop
```

### 5. Merger dans develop (après review)

```bash
git checkout develop
git merge feature/<nom> --no-ff -m "merge(feature/<nom>): Description de la feature"
git push origin develop
```

### 6. Release vers main

```bash
git checkout main
git merge develop --no-ff -m "release: Description de la version"
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin main --tags
```

## Règles (phase de développement principale)

- **Ne jamais** committer directement sur `main`
- **Toujours** passer par `develop` avant `main`
- Chaque Pull Request doit être relue avant le merge
- Un commit = une modification logique cohérente
- Les branches `feature/*` sont supprimées après merge dans `develop`

## Évolution du workflow (phase finale)

Ce Git Flow a été suivi pendant toute la phase de construction (features et
correctifs mergés en `--no-ff` dans `develop`, puis release vers `main` —
l'historique des merges en témoigne). Après le merge de
`feature/finalisation-livrables` et la migration de l'interface vers
FastAPI + React (branche `new-front`), le projet est passé en **cycle court** :
les correctifs de fin de projet sont commités directement sur `main` (binôme,
relecture des commits a posteriori), et `develop` est gelée à ce point.
Aucun tag de version n'a été posé ; la version soutenue est la tête de `main`.
