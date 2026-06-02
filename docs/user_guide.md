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

## Raccourcis utiles

| Action | Commande |
|---|---|
| Recharger la page | `R` ou `F5` dans le navigateur |
| Arrêter l'application | `Ctrl + C` dans le terminal |
| Relancer l'app | `python -m streamlit run src/app/app.py` |
