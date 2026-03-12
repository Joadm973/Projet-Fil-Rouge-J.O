"""
Module pour charger les données des Jeux Olympiques
"""

import pandas as pd
from pathlib import Path
from typing import Optional
import config


class DataLoader:
    """Classe pour charger les données des JO"""
    
    def __init__(self, filepath: Optional[Path] = None):
        """
        Initialise le chargeur de données
        
        Args:
            filepath: Chemin vers le fichier CSV (optionnel)
        """
        self.filepath = filepath or config.RAW_OLYMPICS_FILE
    
    def load_data(self) -> pd.DataFrame:
        """
        Charge les données brutes depuis le fichier CSV
        
        Returns:
            DataFrame contenant les données brutes
        """
        if not self.filepath.exists():
            raise FileNotFoundError(
                f"Le fichier {self.filepath} n'existe pas. "
                f"Assurez-vous que le dataset est dans {config.RAW_DATA_DIR}"
            )
        
        print(f"📂 Chargement des données depuis {self.filepath}...")
        df = pd.read_csv(self.filepath)
        print(f"✅ {len(df)} lignes chargées")
        
        return df
    
    def get_data_info(self, df: pd.DataFrame) -> dict:
        """
        Obtient des informations sur le dataset
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire contenant les informations
        """
        info = {
            "n_rows": len(df),
            "n_columns": len(df.columns),
            "columns": list(df.columns),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024**2,
            "missing_values": df.isnull().sum().to_dict(),
            "dtypes": df.dtypes.to_dict()
        }
        
        return info
    
    def load_processed_data(self, filename: str) -> pd.DataFrame:
        """
        Charge des données déjà traitées
        
        Args:
            filename: Nom du fichier dans le dossier processed
            
        Returns:
            DataFrame contenant les données traitées
        """
        filepath = config.PROCESSED_DATA_DIR / filename
        
        if not filepath.exists():
            raise FileNotFoundError(
                f"Le fichier {filepath} n'existe pas. "
                "Exécutez d'abord le nettoyage des données."
            )
        
        return pd.read_csv(filepath)
    
    def filter_summer_olympics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filtre uniquement les JO d'été
        
        Args:
            df: DataFrame complet
            
        Returns:
            DataFrame filtré pour les JO d'été
        """
        return df[df['Season'] == 'Summer'].copy()
    
    def filter_by_years(self, df: pd.DataFrame, years: list) -> pd.DataFrame:
        """
        Filtre les données par années spécifiques
        
        Args:
            df: DataFrame à filtrer
            years: Liste des années à conserver
            
        Returns:
            DataFrame filtré
        """
        return df[df['Year'].isin(years)].copy()
    
    def get_unique_values(self, df: pd.DataFrame, column: str) -> list:
        """
        Obtient les valeurs uniques d'une colonne
        
        Args:
            df: DataFrame
            column: Nom de la colonne
            
        Returns:
            Liste des valeurs uniques triées
        """
        return sorted(df[column].unique().tolist())


if __name__ == "__main__":
    # Test du module
    loader = DataLoader()
    df = loader.load_data()
    
    print("\n📊 Informations sur les données:")
    info = loader.get_data_info(df)
    print(f"Lignes: {info['n_rows']}")
    print(f"Colonnes: {info['n_columns']}")
    print(f"Mémoire: {info['memory_usage_mb']:.2f} MB")
    
    print("\n📅 Années disponibles:")
    years = loader.get_unique_values(df, 'Year')
    print(f"De {min(years)} à {max(years)}")
    
    print("\n🏅 Sports disponibles:")
    sports = loader.get_unique_values(df, 'Sport')
    print(f"{len(sports)} sports différents")
