"""
Module pour nettoyer et préparer les données des Jeux Olympiques
"""

import pandas as pd
import numpy as np
from typing import Optional
import config


class DataCleaner:
    """Classe pour nettoyer et préparer les données des JO"""
    
    def __init__(self):
        """Initialise le nettoyeur de données"""
        self.cleaning_report = {}
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applique toutes les opérations de nettoyage
        
        Args:
            df: DataFrame brut
            
        Returns:
            DataFrame nettoyé
        """
        print("\n🧹 Nettoyage des données en cours...")
        
        df_clean = df.copy()
        
        # Supprimer les doublons
        df_clean = self.remove_duplicates(df_clean)
        
        # Nettoyer les valeurs manquantes
        df_clean = self.handle_missing_values(df_clean)
        
        # Standardiser les valeurs
        df_clean = self.standardize_values(df_clean)
        
        # Ajouter des colonnes calculées
        df_clean = self.add_calculated_columns(df_clean)
        
        # Filtrer les données pertinentes
        df_clean = self.filter_relevant_data(df_clean)
        
        print("✅ Nettoyage terminé!\n")
        return df_clean
    
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Supprime les lignes dupliquées
        
        Args:
            df: DataFrame à nettoyer
            
        Returns:
            DataFrame sans doublons
        """
        n_before = len(df)
        df_clean = df.drop_duplicates()
        n_after = len(df_clean)
        n_removed = n_before - n_after
        
        self.cleaning_report['duplicates_removed'] = n_removed
        print(f"  ❌ {n_removed} doublons supprimés")
        
        return df_clean
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Gère les valeurs manquantes
        
        Args:
            df: DataFrame à nettoyer
            
        Returns:
            DataFrame avec valeurs manquantes traitées
        """
        df_clean = df.copy()
        
        # Afficher les valeurs manquantes par colonne
        missing = df_clean.isnull().sum()
        if missing.sum() > 0:
            print("  🔍 Valeurs manquantes détectées:")
            for col, count in missing[missing > 0].items():
                pct = (count / len(df_clean)) * 100
                print(f"    - {col}: {count} ({pct:.1f}%)")
        
        # Remplacer 'NA' dans Medal par 'No medal'
        if 'Medal' in df_clean.columns:
            df_clean['Medal'] = df_clean['Medal'].fillna('No medal')
        
        # Supprimer les lignes avec des valeurs manquantes critiques
        critical_columns = ['Name', 'Year', 'Sport', 'Event', 'Team', 'NOC']
        existing_critical = [col for col in critical_columns if col in df_clean.columns]
        
        n_before = len(df_clean)
        df_clean = df_clean.dropna(subset=existing_critical)
        n_after = len(df_clean)
        n_removed = n_before - n_after
        
        if n_removed > 0:
            print(f"  ❌ {n_removed} lignes supprimées (valeurs critiques manquantes)")
        
        self.cleaning_report['rows_with_missing_critical'] = n_removed
        
        return df_clean
    
    def standardize_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardise les valeurs (majuscules, espaces, etc.)
        
        Args:
            df: DataFrame à standardiser
            
        Returns:
            DataFrame standardisé
        """
        df_clean = df.copy()
        
        # Nettoyer les espaces dans les colonnes textuelles
        text_columns = df_clean.select_dtypes(include=['object']).columns
        for col in text_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()
        
        # Standardiser le genre
        if 'Sex' in df_clean.columns:
            df_clean['Sex'] = df_clean['Sex'].map({'M': 'Male', 'F': 'Female'})
        
        # Standardiser les médailles
        if 'Medal' in df_clean.columns:
            medal_mapping = {
                'Gold': 'Gold',
                'Silver': 'Silver',
                'Bronze': 'Bronze',
                'No medal': 'No medal',
                'nan': 'No medal',
                None: 'No medal'
            }
            df_clean['Medal'] = df_clean['Medal'].astype(str).map(
                lambda x: medal_mapping.get(x, 'No medal')
            )
        
        print("  ✅ Valeurs standardisées")
        return df_clean
    
    def add_calculated_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ajoute des colonnes calculées utiles pour l'analyse
        
        Args:
            df: DataFrame
            
        Returns:
            DataFrame avec colonnes supplémentaires
        """
        df_clean = df.copy()
        
        # Indicateur de médaille obtenue
        if 'Medal' in df_clean.columns:
            df_clean['Has_Medal'] = df_clean['Medal'] != 'No medal'
            df_clean['Is_Gold'] = df_clean['Medal'] == 'Gold'
            df_clean['Is_Silver'] = df_clean['Medal'] == 'Silver'
            df_clean['Is_Bronze'] = df_clean['Medal'] == 'Bronze'
        
        # Score de médaille pondéré
        if 'Medal' in df_clean.columns:
            df_clean['Medal_Score'] = df_clean['Medal'].map(
                {'Gold': 3, 'Silver': 2, 'Bronze': 1, 'No medal': 0}
            )
        
        # Décennie
        if 'Year' in df_clean.columns:
            df_clean['Decade'] = (df_clean['Year'] // 10) * 10
        
        print("  ✅ Colonnes calculées ajoutées")
        return df_clean
    
    def filter_relevant_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filtre les données pour ne garder que celles pertinentes
        
        Args:
            df: DataFrame à filtrer
            
        Returns:
            DataFrame filtré
        """
        df_clean = df.copy()
        
        # Filtrer uniquement les JO d'été (focus du projet)
        if 'Season' in df_clean.columns:
            n_before = len(df_clean)
            df_clean = df_clean[df_clean['Season'] == 'Summer']
            n_removed = n_before - len(df_clean)
            print(f"  🏖️ Focus JO d'été: {n_removed} entrées JO d'hiver retirées")
        
        # Garder uniquement les années modernes (depuis 1960)
        if 'Year' in df_clean.columns:
            n_before = len(df_clean)
            df_clean = df_clean[df_clean['Year'] >= 1960]
            n_removed = n_before - len(df_clean)
            print(f"  📅 Focus ère moderne: {n_removed} entrées anciennes retirées")
        
        return df_clean
    
    def save_cleaned_data(self, df: pd.DataFrame, filename: Optional[str] = None):
        """
        Sauvegarde les données nettoyées
        
        Args:
            df: DataFrame à sauvegarder
            filename: Nom du fichier (optionnel)
        """
        if filename is None:
            filepath = config.CLEANED_DATA_FILE
        else:
            filepath = config.PROCESSED_DATA_DIR / filename
        
        # Créer le répertoire si nécessaire
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder
        df.to_csv(filepath, index=False)
        print(f"💾 Données sauvegardées: {filepath}")
    
    def get_cleaning_report(self) -> dict:
        """
        Retourne le rapport de nettoyage
        
        Returns:
            Dictionnaire avec les statistiques de nettoyage
        """
        return self.cleaning_report
    
    def generate_aggregated_datasets(self, df: pd.DataFrame):
        """
        Génère des datasets agrégés pour l'analyse
        
        Args:
            df: DataFrame nettoyé
        """
        print("\n📊 Génération des datasets agrégés...")
        
        # Médailles par pays
        medals_by_country = self._aggregate_medals_by_country(df)
        medals_by_country.to_csv(config.MEDALS_BY_COUNTRY_FILE, index=False)
        print(f"  ✅ Médailles par pays sauvegardées")
        
        # Médailles par sport
        medals_by_sport = self._aggregate_medals_by_sport(df)
        medals_by_sport.to_csv(config.MEDALS_BY_SPORT_FILE, index=False)
        print(f"  ✅ Médailles par sport sauvegardées")
        
        # Statistiques des athlètes
        athletes_stats = self._aggregate_athlete_stats(df)
        athletes_stats.to_csv(config.ATHLETES_STATS_FILE, index=False)
        print(f"  ✅ Statistiques des athlètes sauvegardées")
    
    def _aggregate_medals_by_country(self, df: pd.DataFrame) -> pd.DataFrame:
        """Agrège les médailles par pays et année"""
        medals_only = df[df['Has_Medal']].copy()
        
        agg = medals_only.groupby(['Year', 'NOC', 'Team', 'Medal']).size().reset_index(name='Count')
        
        # Pivot pour avoir Gold, Silver, Bronze en colonnes
        pivot = agg.pivot_table(
            index=['Year', 'NOC', 'Team'],
            columns='Medal',
            values='Count',
            fill_value=0
        ).reset_index()
        
        # Calculer le total
        pivot['Total'] = pivot.get('Gold', 0) + pivot.get('Silver', 0) + pivot.get('Bronze', 0)
        
        # Score pondéré
        pivot['Score'] = (
            pivot.get('Gold', 0) * 3 +
            pivot.get('Silver', 0) * 2 +
            pivot.get('Bronze', 0) * 1
        )
        
        return pivot
    
    def _aggregate_medals_by_sport(self, df: pd.DataFrame) -> pd.DataFrame:
        """Agrège les médailles par sport et année"""
        medals_only = df[df['Has_Medal']].copy()
        
        agg = medals_only.groupby(['Year', 'Sport', 'Medal']).size().reset_index(name='Count')
        
        return agg
    
    def _aggregate_athlete_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcule les statistiques des athlètes"""
        # Identifier les colonnes disponibles
        id_col = 'player_id' if 'player_id' in df.columns else 'Name'
        
        stats = df.groupby([id_col, 'Name', 'Sex', 'Team', 'NOC']).agg({
            'Year': ['min', 'max', 'count'],
            'Medal': lambda x: (x != 'No medal').sum(),
            'Is_Gold': 'sum' if 'Is_Gold' in df.columns else lambda x: 0,
            'Is_Silver': 'sum' if 'Is_Silver' in df.columns else lambda x: 0,
            'Is_Bronze': 'sum' if 'Is_Bronze' in df.columns else lambda x: 0,
            'Sport': lambda x: ', '.join(x.unique())
        }).reset_index()
        
        stats.columns = [
            id_col, 'Name', 'Sex', 'Team', 'NOC',
            'First_Year', 'Last_Year', 'Participations',
            'Total_Medals', 'Gold_Count', 'Silver_Count', 'Bronze_Count',
            'Sports'
        ]
        
        return stats


if __name__ == "__main__":
    # Test du module
    from data_loader import DataLoader
    
    loader = DataLoader()
    df_raw = loader.load_data()
    
    cleaner = DataCleaner()
    df_clean = cleaner.clean_data(df_raw)
    
    print("\n📋 Rapport de nettoyage:")
    report = cleaner.get_cleaning_report()
    for key, value in report.items():
        print(f"  - {key}: {value}")
    
    print(f"\n📊 Dataset final: {len(df_clean)} lignes, {len(df_clean.columns)} colonnes")
    
    # Sauvegarder
    cleaner.save_cleaned_data(df_clean)
    cleaner.generate_aggregated_datasets(df_clean)
