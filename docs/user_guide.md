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

- **Indicateurs clés** : nombre d'éditions, athlètes uniques, pays participants, disciplines
- **Médailles par édition** : histogramme empilé or/argent/bronze
- **Répartition par genre** : camembert hommes/femmes
- **Évolution de la participation** : courbe athlètes, pays et sports par année

---

## Page Exploration

Permet d'explorer les données en filtrant par période.

### Filtres disponibles (barre latérale)

| Filtre | Description |
|---|---|
| Fourchette d'années | Glissière pour sélectionner une plage d'éditions |

### Visualisations

- **Top 15 pays** : médailles empilées par type
- **Top 10 sports** : barres horizontales
- **Évolution médailles d'or** : courbe pour les 5 premiers pays
- **Carte mondiale** : choroplèthe colorée par total de médailles

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

1. Choisir le **nombre de pays** à afficher (glissière 5–30)
2. Cliquer sur **🚀 Lancer les prédictions**
3. Consulter :
   - Le classement prédit sous forme de barres horizontales
   - Le tableau détaillé
   - La courbe historique + projection pour un pays sélectionné

### Interprétation

Le modèle est une **régression linéaire** entraînée sur l'historique de chaque pays.  
Les résultats représentent une **tendance statistique**, pas une certitude.

> ⚠️ Les pays dont l'équipe nationale a changé de nom (ex. URSS → Russie) peuvent apparaître avec des valeurs atypiques.

---

## Raccourcis utiles

| Action | Commande |
|---|---|
| Recharger la page | `R` ou `F5` dans le navigateur |
| Arrêter l'application | `Ctrl + C` dans le terminal |
| Relancer l'app | `python -m streamlit run src/app/app.py` |
