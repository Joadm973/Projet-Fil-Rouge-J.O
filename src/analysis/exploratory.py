"""
Module pour les analyses exploratoires des données olympiques
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import config


class ExploratoryAnalysis:
    """Classe pour effectuer des analyses exploratoires sur les données des JO"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialise l'analyseur
        
        Args:
            df: DataFrame contenant les données nettoyées
        """
        self.df = df
    
    def get_dataset_overview(self) -> Dict:
        """
        Obtient un aperçu général du dataset
        
        Returns:
            Dictionnaire contenant les statistiques générales
        """
        overview = {
            'total_rows': len(self.df),
            'total_athletes': self.df['Name'].nunique() if 'Name' in self.df.columns else 0,
            'total_countries': self.df['NOC'].nunique() if 'NOC' in self.df.columns else 0,
            'total_sports': self.df['Sport'].nunique() if 'Sport' in self.df.columns else 0,
            'total_events': self.df['Event'].nunique() if 'Event' in self.df.columns else 0,
            'year_range': (
                int(self.df['Year'].min()),
                int(self.df['Year'].max())
            ) if 'Year' in self.df.columns else (None, None),
            'total_medals': len(self.df[self.df['Has_Medal']]) if 'Has_Medal' in self.df.columns else 0,
        }
        
        return overview
    
    def analyze_medals_distribution(self) -> pd.DataFrame:
        """
        Analyse la distribution des médailles
        
        Returns:
            DataFrame avec la distribution des médailles par type
        """
        if 'Medal' not in self.df.columns:
            return pd.DataFrame()
        
        medal_counts = self.df['Medal'].value_counts().reset_index()
        medal_counts.columns = ['Medal_Type', 'Count']
        
        total = medal_counts['Count'].sum()
        medal_counts['Percentage'] = (medal_counts['Count'] / total * 100).round(2)
        
        return medal_counts
    
    def get_top_countries(self, n: int = 10, metric: str = 'Total') -> pd.DataFrame:
        """
        Obtient les meilleurs pays en termes de médailles
        
        Args:
            n: Nombre de pays à retourner
            metric: Métrique à utiliser ('Total', 'Gold', 'Silver', 'Bronze', 'Score')
            
        Returns:
            DataFrame avec les top pays
        """
        medals_df = self.df[self.df['Has_Medal']].copy()
        
        # Compter les médailles par pays
        country_medals = medals_df.groupby('NOC').agg({
            'Is_Gold': 'sum',
            'Is_Silver': 'sum',
            'Is_Bronze': 'sum',
            'Medal': 'count'
        }).reset_index()
        
        country_medals.columns = ['NOC', 'Gold', 'Silver', 'Bronze', 'Total']
        
        # Calculer le score pondéré
        country_medals['Score'] = (
            country_medals['Gold'] * 3 +
            country_medals['Silver'] * 2 +
            country_medals['Bronze'] * 1
        )
        
        # Trier par la métrique choisie
        country_medals = country_medals.sort_values(metric, ascending=False)
        
        return country_medals.head(n)
    
    def get_top_athletes(self, n: int = 10) -> pd.DataFrame:
        """
        Obtient les meilleurs athlètes
        
        Args:
            n: Nombre d'athlètes à retourner
            
        Returns:
            DataFrame avec les top athlètes
        """
        medals_df = self.df[self.df['Has_Medal']].copy()
        
        athlete_medals = medals_df.groupby(['Name', 'NOC', 'Sport']).agg({
            'Is_Gold': 'sum',
            'Is_Silver': 'sum',
            'Is_Bronze': 'sum',
            'Medal': 'count'
        }).reset_index()
        
        athlete_medals.columns = ['Name', 'Country', 'Sport', 'Gold', 'Silver', 'Bronze', 'Total']
        
        # Calculer le score
        athlete_medals['Score'] = (
            athlete_medals['Gold'] * 3 +
            athlete_medals['Silver'] * 2 +
            athlete_medals['Bronze'] * 1
        )
        
        athlete_medals = athlete_medals.sort_values('Score', ascending=False)
        
        return athlete_medals.head(n)
    
    def analyze_gender_distribution(self) -> pd.DataFrame:
        """
        Analyse la distribution par genre
        
        Returns:
            DataFrame avec les statistiques par genre
        """
        if 'Sex' not in self.df.columns:
            return pd.DataFrame()
        
        gender_stats = self.df.groupby('Sex').agg({
            'Name': 'count',
            'Has_Medal': 'sum',
            'Is_Gold': 'sum',
            'Is_Silver': 'sum',
            'Is_Bronze': 'sum'
        }).reset_index()
        
        gender_stats.columns = ['Gender', 'Participations', 'Total_Medals', 'Gold', 'Silver', 'Bronze']
        
        # Taux de médailles
        gender_stats['Medal_Rate'] = (
            gender_stats['Total_Medals'] / gender_stats['Participations'] * 100
        ).round(2)
        
        return gender_stats
    
    def analyze_sport_popularity(self) -> pd.DataFrame:
        """
        Analyse la popularité des sports
        
        Returns:
            DataFrame avec les statistiques par sport
        """
        if 'Sport' not in self.df.columns:
            return pd.DataFrame()
        
        sport_stats = self.df.groupby('Sport').agg({
            'Name': 'count',
            'Event': 'nunique',
            'NOC': 'nunique',
            'Has_Medal': 'sum'
        }).reset_index()
        
        sport_stats.columns = ['Sport', 'Participations', 'Events', 'Countries', 'Medals']
        sport_stats = sport_stats.sort_values('Participations', ascending=False)
        
        return sport_stats
    
    def analyze_evolution_over_time(self, country: Optional[str] = None) -> pd.DataFrame:
        """
        Analyse l'évolution des médailles au fil du temps
        
        Args:
            country: Pays spécifique à analyser (optionnel)
            
        Returns:
            DataFrame avec l'évolution temporelle
        """
        df_analysis = self.df.copy()
        
        if country:
            df_analysis = df_analysis[df_analysis['NOC'] == country]
        
        medals_df = df_analysis[df_analysis['Has_Medal']].copy()
        
        evolution = medals_df.groupby('Year').agg({
            'Is_Gold': 'sum',
            'Is_Silver': 'sum',
            'Is_Bronze': 'sum',
            'Medal': 'count'
        }).reset_index()
        
        evolution.columns = ['Year', 'Gold', 'Silver', 'Bronze', 'Total']
        
        return evolution
    
    def get_country_performance_by_sport(self, country: str) -> pd.DataFrame:
        """
        Analyse les performances d'un pays par sport
        
        Args:
            country: Code pays NOC
            
        Returns:
            DataFrame avec les performances par sport
        """
        country_df = self.df[self.df['NOC'] == country].copy()
        medals_df = country_df[country_df['Has_Medal']].copy()
        
        sport_performance = medals_df.groupby('Sport').agg({
            'Is_Gold': 'sum',
            'Is_Silver': 'sum',
            'Is_Bronze': 'sum',
            'Medal': 'count'
        }).reset_index()
        
        sport_performance.columns = ['Sport', 'Gold', 'Silver', 'Bronze', 'Total']
        
        # Score pondéré
        sport_performance['Score'] = (
            sport_performance['Gold'] * 3 +
            sport_performance['Silver'] * 2 +
            sport_performance['Bronze'] * 1
        )
        
        sport_performance = sport_performance.sort_values('Score', ascending=False)
        
        return sport_performance
    
    def identify_emerging_countries(self, recent_years: int = 12) -> pd.DataFrame:
        """
        Identifie les pays émergents (forte progression récente)
        
        Args:
            recent_years: Nombre d'années récentes à considérer
            
        Returns:
            DataFrame avec les pays en progression
        """
        if 'Year' not in self.df.columns:
            return pd.DataFrame()
        
        max_year = self.df['Year'].max()
        cutoff_year = max_year - recent_years
        
        # Médailles anciennes
        old_medals = self.df[
            (self.df['Year'] < cutoff_year) &
            (self.df['Has_Medal'])
        ].groupby('NOC')['Medal'].count().reset_index()
        old_medals.columns = ['NOC', 'Old_Medals']
        
        # Médailles récentes
        recent_medals = self.df[
            (self.df['Year'] >= cutoff_year) &
            (self.df['Has_Medal'])
        ].groupby('NOC')['Medal'].count().reset_index()
        recent_medals.columns = ['NOC', 'Recent_Medals']
        
        # Fusionner
        comparison = pd.merge(old_medals, recent_medals, on='NOC', how='outer').fillna(0)
        
        # Calculer la croissance
        comparison['Growth'] = comparison['Recent_Medals'] - comparison['Old_Medals']
        comparison['Growth_Rate'] = (
            (comparison['Recent_Medals'] / (comparison['Old_Medals'] + 1)) * 100
        ).round(2)
        
        # Filtrer les pays avec croissance significative
        emerging = comparison[comparison['Growth'] > 0].sort_values('Growth', ascending=False)
        
        return emerging.head(20)
    
    def get_host_country_advantage(self) -> pd.DataFrame:
        """
        Analyse l'avantage du pays hôte
        
        Returns:
            DataFrame montrant la performance des pays hôtes
        """
        if 'City' not in self.df.columns:
            return pd.DataFrame()
        
        # Mapper les villes aux pays (simplifié)
        city_to_country = {
            'Tokyo': 'JPN',
            'Rio de Janeiro': 'BRA',
            'London': 'GBR',
            'Beijing': 'CHN',
            'Athens': 'GRE',
            'Sydney': 'AUS',
            'Atlanta': 'USA',
            'Barcelona': 'ESP',
            'Seoul': 'KOR',
            'Los Angeles': 'USA',
            'Montreal': 'CAN',
            'Munich': 'GER',
            'Mexico City': 'MEX',
            'Rome': 'ITA',
            'Melbourne': 'AUS'
        }
        
        results = []
        
        for city, country in city_to_country.items():
            year_data = self.df[self.df['City'].str.contains(city, case=False, na=False)]
            
            if len(year_data) > 0:
                year = year_data['Year'].iloc[0]
                
                country_medals = year_data[
                    (year_data['NOC'] == country) &
                    (year_data['Has_Medal'])
                ]
                
                gold = country_medals['Is_Gold'].sum()
                silver = country_medals['Is_Silver'].sum()
                bronze = country_medals['Is_Bronze'].sum()
                total = len(country_medals)
                
                results.append({
                    'Year': year,
                    'City': city,
                    'Country': country,
                    'Gold': gold,
                    'Silver': silver,
                    'Bronze': bronze,
                    'Total': total
                })
        
        return pd.DataFrame(results)


if __name__ == "__main__":
    # Test du module
    from src.data.data_loader import DataLoader
    from src.data.data_cleaner import DataCleaner
    
    loader = DataLoader()
    df_raw = loader.load_data()
    
    cleaner = DataCleaner()
    df_clean = cleaner.clean_data(df_raw)
    
    analyzer = ExploratoryAnalysis(df_clean)
    
    print("\n📊 Aperçu du dataset:")
    overview = analyzer.get_dataset_overview()
    for key, value in overview.items():
        print(f"  - {key}: {value}")
    
    print("\n🥇 Top 10 des pays:")
    top_countries = analyzer.get_top_countries(10)
    print(top_countries[['NOC', 'Gold', 'Silver', 'Bronze', 'Total', 'Score']].to_string(index=False))
    
    print("\n🏃 Top 10 des athlètes:")
    top_athletes = analyzer.get_top_athletes(10)
    print(top_athletes[['Name', 'Country', 'Gold', 'Silver', 'Bronze', 'Total']].head().to_string(index=False))
