# Guide Utilisateur — YPerf

## Lancer l'application

```bash
python -m streamlit run src/app/app.py
```

Ouvrir [http://localhost:8501](http://localhost:8501) dans votre navigateur.

---

## Navigation

La barre latérale gauche contient le menu de navigation. Cliquez sur une option pour changer de page :

| Option | Description |
|---|---|
| 🏠 Accueil | Vue d'ensemble du projet et des données |
| 🔍 Exploration | Analyse interactive par pays, sport et année |
| 🏃 Athlètes | Palmarès et performances individuelles |
| 🔮 Prédictions 2028 | Prévisions des médailles pour Los Angeles 2028 |
| 📝 Annotations | Avis et notes personnelles sur athlètes, pays, sports |
| 🌱 Nouvelles générations | Détection des talents émergents et nations montantes |
| 🌐 Multi-sources | Analyses enrichies avec données World Bank (population, PIB) |

---

## Page Accueil

Affiche une vue synthétique :

- **Indicateurs clés** : nombre d'éditions, athlètes uniques, pays participants, disciplines, médailles d'or
- **Médailles par édition** : histogramme empilé or/argent/bronze
- **Évolution de la parité** : graphique en aires hommes/femmes
- **Rayonnement mondial** : carte choroplèthe + top 10 pays
- **Évolution de la participation** : courbe athlètes, pays et sports par année

---

## Page Exploration

Permet d'explorer les données en filtrant par période.

### Filtres disponibles (barre latérale)

| Filtre | Description |
|---|---|
| Période | Glissière pour sélectionner une plage d'éditions |
| Saison | Été / Hiver / Toutes |
| Genre | Hommes / Femmes / Tous |

### Visualisations (onglets Pays · Sports · Tendances · Heatmap)

- **Top pays** : médailles empilées par type + carte mondiale + sunburst
- **Top sports** : barres horizontales, répartition par genre, treemap
- **Tendances** : évolution des médailles d'or et de la parité
- **Heatmap** : médailles d'or par pays et par édition

---

## Page Athlètes

Analyse les performances individuelles.

### Filtres disponibles (barre latérale)

| Filtre | Description |
|---|---|
| Sport | Filtrer par discipline |
| Pays | Filtrer par équipe nationale |
| Médailles | Sélectionner or, argent et/ou bronze |

### Visualisations

- **Top 20 athlètes** : barres horizontales colorées par sport
- **Détail or/argent/bronze** : barres groupées pour le Top 10
- **Tableau** : liste complète des athlètes retenus par les filtres

---

## Page Prédictions 2028

Génère des prévisions de médailles pour les JO de Los Angeles 2028.

### Utilisation

1. Choisir l'**algorithme** (Linéaire, Ridge, Gradient Boosting, Polynomiale)
2. Choisir le **nombre de pays** à afficher (glissière 5–30)
3. Cliquer sur **🚀 Calculer les prédictions**
4. Consulter les onglets :
   - **Classement 2028** : barres horizontales + podium
   - **Historique pays** : courbe historique + projection + intervalle de confiance
   - **Comparaison modèles** : métriques MAE / R² par algorithme
   - **Carte prédite** : choroplèthe des médailles 2028

### Interprétation

Plusieurs **modèles de régression** sont entraînés sur l'historique de chaque pays.  
Les résultats représentent une **tendance statistique**, pas une certitude.

> ⚠️ Seules les **nations encore actives** (présentes depuis 2016) sont prédites :
> les pays disparus (URSS, RDA…) sont exclus pour ne pas fausser le classement.

---

## Page Annotations

Permet d'ajouter des notes personnelles sur n'importe quel élément du dataset.

### Ajouter une annotation

1. Choisir le **type** : Athlète / Pays / Sport / Édition
2. Sélectionner la **cible** dans la liste déroulante (suggestions tirées du dataset)
3. Renseigner l'**auteur** (optionnel, défaut : « Utilisateur »)
4. Saisir des **tags** séparés par des virgules (ex : `record, à_surveiller`)
5. Écrire la **note** et cliquer sur **Enregistrer**

### Consulter et filtrer

- Filtrer par type ou par recherche textuelle (nom, note, tag)
- Supprimer une annotation avec le bouton **✕**

> Les annotations sont stockées dans `data/annotations.json` et persistent entre les sessions.

---

## Page Nouvelles générations

Identifie les athlètes et nations émergents en vue de 2028.

### Onglets

| Onglet | Description |
|---|---|
| 🚀 Talents 2016+ | Athlètes dont la 1ère participation date de 2016 ou après, classés par score (Or=3pts, Argent=2pts, Bronze=1pt) |
| ⚡ Breakouts 2020+ | Athlètes sans médaille avant 2020, percée récente |
| 🔄 Renouvellement | Taux de renouvellement des dominants par sport (2008–2016 vs 2020–2024) |
| 🌍 Nouvelles nations | Pays remportant leur 1ère médaille depuis 2016 — carte choroplèthe |

---

## Page Multi-sources

Fusionne les données JO (CSV Kaggle) avec les métadonnées de la **World Bank API**.

### Données enrichies

| Source | Contenu |
|---|---|
| CSV Kaggle | Participations, médailles, sports (1896–2024) |
| World Bank API | Population, PIB/habitant, région géographique, niveau de revenu |

> Les données World Bank sont mises en cache dans `data/processed/countries_api.json` pour éviter les appels répétés.

### Onglets

| Onglet | Description |
|---|---|
| 🏅 Médailles par habitant | Classement per-capita, scatter population vs médailles |
| 🌍 Analyse par région | Camembert + stacked area (1992–2024) par région World Bank |
| 💰 Médailles vs PIB | Scatter PIB/hab. vs médailles/million + sur/sous-performers |
| 📊 Données fusionnées | Tableau téléchargeable (export CSV) |

---

## Raccourcis utiles

| Action | Commande |
|---|---|
| Recharger la page | `R` ou `F5` dans le navigateur |
| Arrêter l'application | `Ctrl + C` dans le terminal |
| Relancer l'app | `python -m streamlit run src/app/app.py` |
