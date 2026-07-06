# Guide Utilisateur — YPerf

## Lancer l'application

Deux processus à lancer, dans deux terminaux séparés.

```bash
# Terminal 1 — backend
.venv\Scripts\python -m uvicorn backend.main:app --port 8000 --reload

# Terminal 2 — frontend
cd frontend
npm run dev
```

Ouvrir [http://localhost:5174](http://localhost:5174) dans votre navigateur.

---

## Navigation

La barre latérale gauche contient le menu de navigation. Cliquez sur une option pour changer de page :

| Option | Description |
|---|---|
| Accueil | Vue d'ensemble du projet et des données |
| Exploration | Analyse interactive par pays, sport et année |
| Athlètes | Palmarès et performances individuelles |
| Prédictions 2028 | Prévisions des médailles pour Los Angeles 2028, côtes, domination pays |
| Annotations | Avis et notes personnelles sur athlètes, pays, sports, éditions |
| Générations | Détection des talents émergents, renouvellement, nouvelles nations |
| Multi-sources | Analyses enrichies avec données World Bank (population, PIB) |

---

## Page Accueil

Affiche une vue synthétique :

- **Indicateurs clés** : nombre d'éditions, athlètes uniques, pays participants, disciplines, médailles d'or
- **Médailles par édition** : histogramme empilé or/argent/bronze
- **Évolution de la parité** : graphique en aires hommes/femmes
- **Rayonnement mondial** : carte choroplèthe + top 10 pays
- **Tendances & disciplines** : courbe athlètes/pays/sports par année + treemap des sports

---

## Page Exploration

Permet d'explorer les données en filtrant par période et genre.

### Filtres disponibles

| Filtre | Description |
|---|---|
| Période | Bornes min/max sur les éditions |
| Genre | Hommes / Femmes / Tous |
| Top N pays | Glissière (5–30) |

### Onglets (Pays · Sports · Tendances · Heatmap)

- **Pays** : médailles empilées par type + carte mondiale choroplèthe
- **Sports** : barres groupées par genre pour le top N disciplines
- **Tendances** : évolution des médailles d'or par édition
- **Heatmap** : médailles d'or par pays et par édition

---

## Page Athlètes

Analyse les performances individuelles.

### Filtres disponibles

| Filtre | Description |
|---|---|
| Sport | Filtrer par discipline |
| Pays | Filtrer par équipe nationale |
| Période | Bornes min/max sur les éditions |
| Rechercher | Recherche par nom |

### Onglets

- **Classement** : top athlètes (barres horizontales) + répartition par genre
- **Genre** : comparaison médailles hommes/femmes
- **Fiche athlète** : sélection d'un athlète du top 10, détail des médailles par type et par édition

---

## Page Prédictions 2028

Génère des prévisions de médailles pour les JO de Los Angeles 2028.

### Utilisation

1. Choisir l'**algorithme** (Régression Linéaire, Ridge, Gradient Boosting, Polynomiale deg. 2)
2. Choisir le **nombre de pays** à afficher (glissière 5–30)
3. Cliquer sur **Calculer →**
4. Consulter les onglets :
   - **Classement 2028** : barres horizontales des médailles prédites
   - **Historique pays** : courbe historique + projection 2028 pour un pays sélectionné
   - **Côtes athlètes** : score pondéré Or=3/Argent=2/Bronze=1 + bonus régularité
   - **Domination pays** : part des médailles d'une discipline captée par un pays depuis 2016
   - **Recommandations** : nations en progression, top disciplines France
   - **Timeline** : diversité olympique (pays médaillés et disciplines) par édition

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
4. Saisir des **tags** séparés par des virgules (ex : `record, à surveiller`)
5. Écrire la **note** et cliquer sur **Enregistrer →**

### Consulter et filtrer

- Filtrer par type ou par recherche textuelle (nom, note, tag)
- Supprimer une annotation avec le bouton **×**

> Les annotations sont stockées dans `data/annotations.json` et persistent entre les sessions.

---

## Page Générations

Identifie les athlètes et nations émergents en vue de 2028.

### Onglets

| Onglet | Description |
|---|---|
| Nouveaux talents | Athlètes dont la 1ère participation date de 2016 ou après, classés par score (Or=3pts, Argent=2pts, Bronze=1pt) |
| Révélations | Athlètes sans médaille avant 2020, comptés par édition de leur première médaille |
| Renouvellement | Taux de renouvellement des athlètes dominants par discipline (2008–2016 vs 2020–2024) |
| Nouvelles nations | Pays remportant leur 1ère médaille depuis 2016, classés par total de médailles remportées |

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
| Par habitant | Classement per-capita (médailles/million d'habitants) |
| Régions | Camembert + courbes par région du monde (depuis 1992) |
| PIB × Médailles | Scatter PIB/habitant vs médailles/million (échelle log) |
| Tableau | Données fusionnées complètes (pays, région, médailles, PIB, population) |

---

## Raccourcis utiles

| Action | Commande |
|---|---|
| Recharger la page | `R` ou `F5` dans le navigateur |
| Arrêter le backend/frontend | `Ctrl + C` dans le terminal correspondant |
| Relancer le backend | `.venv\Scripts\python -m uvicorn backend.main:app --port 8000 --reload` |
| Relancer le frontend | `npm run dev` (dans `frontend/`) |
