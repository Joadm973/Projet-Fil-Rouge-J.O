"""
Module pour les analyses statistiques avancées des données olympiques
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Optional, Tuple
import config


class StatisticalAnalysis:
    """Classe pour effectuer des analyses statistiques sur les données des JO"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialise l'analyseur statistique
        
        Args:
            df: DataFrame contenant les données nettoyées
        """
        self.df = df
    
    def compute_descriptive_stats(self, column: str) -> Dict:
        """
        Calcule les statistiques descriptives pour une colonne
        
        Args:
            column: Nom de la colonne à analyser
            
        Returns:
            Dictionnaire contenant les statistiques descriptives
        """
        if column not in self.df.columns:
            return {}
        
        data = self.df[column].dropna()
        
        if pd.api.types.is_numeric_dtype(data):
            stats_dict = {
                'count': int(len(data)),
                'mean': float(data.mean()),
                'median': float(data.median()),
                'std': float(data.std()),
                'min': float(data.min()),
                'max': float(data.max()),
                'q25': float(data.quantile(0.25)),
                'q75': float(data.quantile(0.75)),
                'skewness': float(data.skew()),
                'kurtosis': float(data.kurtosis())
            }
        else:
            value_counts = data.value_counts()
            stats_dict = {
                'count': int(len(data)),
                'unique': int(data.nunique()),
                'mode': str(data.mode()[0]) if len(data.mode()) > 0 else None,
                'most_common': str(value_counts.index[0]) if len(value_counts) > 0 else None,
                'most_common_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0
            }
        
        return stats_dict
    
    def test_gender_medal_difference(self) -> Dict:
        """
        Test si la différence de médailles entre genres est significative
        
        Returns:
            Dictionnaire avec les résultats du test
        """
        if 'Sex' not in self.df.columns or 'Has_Medal' not in self.df.columns:
            return {}
        
        male_medals = self.df[self.df['Sex'] == 'Male']['Has_Medal'].mean()
        female_medals = self.df[self.df['Sex'] == 'Female']['Has_Medal'].mean()
        
        male_data = self.df[self.df['Sex'] == 'Male']['Has_Medal']
        female_data = self.df[self.df['Sex'] == 'Female']['Has_Medal']
        
        # Test t de Student
        t_stat, p_value = stats.ttest_ind(male_data, female_data)
        
        return {
            'male_medal_rate': float(male_medals),
            'female_medal_rate': float(female_medals),
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'interpretation': (
                "Différence significative" if p_value < 0.05
                else "Pas de différence significative"
            )
        }
    
    def correlation_analysis(self) -> pd.DataFrame:
        """
        Analyse les corrélations entre variables numériques
        
        Returns:
            DataFrame contenant la matrice de corrélation
        """
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return pd.DataFrame()
        
        correlation_matrix = self.df[numeric_cols].corr()
        
        return correlation_matrix
    
    def analyze_medal_concentration(self) -> Dict:
        """
        Analyse la concentration des médailles (coefficient de Gini)
        
        Returns:
            Dictionnaire avec les indicateurs de concentration
        """
        medals_df = self.df[self.df['Has_Medal']].copy()
        
        country_medals = medals_df.groupby('NOC')['Medal'].count().sort_values()
        
        # Calculer le coefficient de Gini
        n = len(country_medals)
        cumsum = country_medals.cumsum()
        gini = (2 * cumsum.sum() / (n * country_medals.sum())) - (n + 1) / n
        
        # Pourcentage de médailles pour le top 10%
        top_10_pct = country_medals.tail(max(1, n // 10)).sum() / country_medals.sum() * 100
        
        return {
            'gini_coefficient': float(gini),
            'top_10_percent_share': float(top_10_pct),
            'n_countries_with_medals': int(n),
            'interpretation': (
                "Forte concentration" if gini > 0.6
                else "Concentration modérée" if gini > 0.4
                else "Faible concentration"
            )
        }
    
    def compute_medal_probabilities_by_sport(self, sport: str) -> Dict:
        """
        Calcule les probabilités de médaille par sport
        
        Args:
            sport: Nom du sport
            
        Returns:
            Dictionnaire avec les probabilités
        """
        sport_df = self.df[self.df['Sport'] == sport].copy()
        
        if len(sport_df) == 0:
            return {}
        
        total = len(sport_df)
        medals = sport_df['Has_Medal'].sum()
        
        probs = {
            'total_participations': int(total),
            'total_medals': int(medals),
            'medal_probability': float(medals / total),
            'gold_probability': float(sport_df['Is_Gold'].sum() / total),
            'silver_probability': float(sport_df['Is_Silver'].sum() / total),
            'bronze_probability': float(sport_df['Is_Bronze'].sum() / total),
        }
        
        return probs
    
    def identify_outlier_performances(self, threshold: float = 3.0) -> pd.DataFrame:
        """
        Identifie les performances aberrantes (athlètes exceptionnels)
        
        Args:
            threshold: Seuil en nombre d'écarts-types
            
        Returns:
            DataFrame avec les performances aberrantes
        """
        # Compter les médailles par athlète
        athlete_medals = self.df[self.df['Has_Medal']].groupby('Name').agg({
            'Medal': 'count',
            'NOC': 'first',
            'Sport': lambda x: ', '.join(x.unique())
        }).reset_index()
        
        athlete_medals.columns = ['Name', 'Total_Medals', 'Country', 'Sports']
        
        # Calculer z-score
        mean_medals = athlete_medals['Total_Medals'].mean()
        std_medals = athlete_medals['Total_Medals'].std()
        
        athlete_medals['z_score'] = (
            (athlete_medals['Total_Medals'] - mean_medals) / std_medals
        )
        
        # Filtrer les outliers
        outliers = athlete_medals[
            np.abs(athlete_medals['z_score']) > threshold
        ].sort_values('Total_Medals', ascending=False)
        
        return outliers
    
    def compute_country_consistency(self, min_years: int = 5) -> pd.DataFrame:
        """
        Calcule la constance des performances des pays
        
        Args:
            min_years: Nombre minimum d'années de participation
            
        Returns:
            DataFrame avec les scores de constance
        """
        medals_df = self.df[self.df['Has_Medal']].copy()
        
        # Médailles par pays et année
        country_year = medals_df.groupby(['NOC', 'Year'])['Medal'].count().reset_index()
        country_year.columns = ['NOC', 'Year', 'Medals']
        
        # Calculer la variance et moyenne par pays
        country_stats = country_year.groupby('NOC').agg({
            'Medals': ['mean', 'std', 'count']
        }).reset_index()
        
        country_stats.columns = ['NOC', 'Mean_Medals', 'Std_Medals', 'Years']
        
        # Filtrer les pays avec assez d'années
        country_stats = country_stats[country_stats['Years'] >= min_years]
        
        # Coefficient de variation (plus faible = plus constant)
        country_stats['Consistency_Score'] = (
            country_stats['Mean_Medals'] / (country_stats['Std_Medals'] + 1)
        )
        
        country_stats = country_stats.sort_values('Consistency_Score', ascending=False)
        
        return country_stats
    
    def chi_square_test_sport_gender(self) -> Dict:
        """
        Test du chi-carré pour l'indépendance entre sport et genre
        
        Returns:
            Dictionnaire avec les résultats du test
        """
        if 'Sport' not in self.df.columns or 'Sex' not in self.df.columns:
            return {}
        
        # Table de contingence
        contingency_table = pd.crosstab(self.df['Sport'], self.df['Sex'])
        
        # Test du chi-carré
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        return {
            'chi2_statistic': float(chi2),
            'p_value': float(p_value),
            'degrees_of_freedom': int(dof),
            'significant': p_value < 0.05,
            'interpretation': (
                "Le sport et le genre sont dépendants" if p_value < 0.05
                else "Le sport et le genre sont indépendants"
            )
        }
    
    def compute_trend_significance(self, country: str) -> Dict:
        """
        Teste la significativité de la tendance temporelle pour un pays
        
        Args:
            country: Code pays NOC
            
        Returns:
            Dictionnaire avec les résultats du test de tendance
        """
        country_df = self.df[
            (self.df['NOC'] == country) &
            (self.df['Has_Medal'])
        ].copy()
        
        if len(country_df) == 0:
            return {}
        
        # Médailles par année
        medals_by_year = country_df.groupby('Year')['Medal'].count().reset_index()
        medals_by_year.columns = ['Year', 'Medals']
        
        if len(medals_by_year) < 2:
            return {}
        
        # Régression linéaire
        x = medals_by_year['Year'].values
        y = medals_by_year['Medals'].values
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        return {
            'slope': float(slope),
            'intercept': float(intercept),
            'r_squared': float(r_value ** 2),
            'p_value': float(p_value),
            'significant_trend': p_value < 0.05,
            'trend_direction': (
                "Croissance" if slope > 0 and p_value < 0.05
                else "Décroissance" if slope < 0 and p_value < 0.05
                else "Stable"
            )
        }
    
    def compute_confidence_interval(
        self,
        country: str,
        confidence: float = 0.95
    ) -> Dict:
        """
        Calcule l'intervalle de confiance pour les médailles d'un pays
        
        Args:
            country: Code pays NOC
            confidence: Niveau de confiance (défaut: 0.95)
            
        Returns:
            Dictionnaire avec l'intervalle de confiance
        """
        country_medals = self.df[
            (self.df['NOC'] == country) &
            (self.df['Has_Medal'])
        ].groupby('Year')['Medal'].count()
        
        if len(country_medals) < 2:
            return {}
        
        mean = country_medals.mean()
        std_err = country_medals.std() / np.sqrt(len(country_medals))
        
        # Intervalle de confiance
        ci = stats.t.interval(
            confidence,
            len(country_medals) - 1,
            loc=mean,
            scale=std_err
        )
        
        return {
            'mean': float(mean),
            'std_error': float(std_err),
            'confidence_level': confidence,
            'ci_lower': float(ci[0]),
            'ci_upper': float(ci[1]),
            'sample_size': int(len(country_medals))
        }
    
    def perform_anova_sports(self) -> Dict:
        """
        ANOVA pour comparer les taux de médailles entre sports
        
        Returns:
            Dictionnaire avec les résultats de l'ANOVA
        """
        if 'Sport' not in self.df.columns or 'Has_Medal' not in self.df.columns:
            return {}
        
        # Préparer les groupes
        sports = self.df['Sport'].unique()
        groups = [
            self.df[self.df['Sport'] == sport]['Has_Medal'].values
            for sport in sports[:20]  # Limiter à 20 sports pour éviter trop de groupes
        ]
        
        # ANOVA
        f_stat, p_value = stats.f_oneway(*groups)
        
        return {
            'f_statistic': float(f_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'interpretation': (
                "Les taux de médailles diffèrent significativement entre sports"
                if p_value < 0.05
                else "Pas de différence significative entre sports"
            )
        }


if __name__ == "__main__":
    # Test du module
    from src.data.data_loader import DataLoader
    from src.data.data_cleaner import DataCleaner
    
    loader = DataLoader()
    df_raw = loader.load_data()
    
    cleaner = DataCleaner()
    df_clean = cleaner.clean_data(df_raw)
    
    analyzer = StatisticalAnalysis(df_clean)
    
    print("\n📊 Test de différence de genre:")
    gender_test = analyzer.test_gender_medal_difference()
    for key, value in gender_test.items():
        print(f"  - {key}: {value}")
    
    print("\n📈 Concentration des médailles:")
    concentration = analyzer.analyze_medal_concentration()
    for key, value in concentration.items():
        print(f"  - {key}: {value}")
    
    print("\n🌟 Performances exceptionnelles:")
    outliers = analyzer.identify_outlier_performances(threshold=2.5)
    print(outliers.head(10).to_string(index=False))
