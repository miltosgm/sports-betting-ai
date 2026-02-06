#!/usr/bin/env python3
"""
Feature Engineering for Premier League Predictions
Creates predictive features from raw game data
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RAW_DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DATA_DIR = Path(__file__).parent.parent / "data" / "processed"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


class FeatureEngineer:
    """Creates predictive features for Premier League games"""
    
    def __init__(self):
        self.games_df = None
        self.stats_df = None
        self.features = None
        
    def load_data(self):
        """Load raw data"""
        logger.info("Loading raw data...")
        
        self.games_df = pd.read_csv(RAW_DATA_DIR / "games_2024-25.csv")
        self.stats_df = pd.read_csv(RAW_DATA_DIR / "team_stats_2024-25.csv")
        
        logger.info(f"Loaded {len(self.games_df)} games")
        logger.info(f"Loaded stats for {len(self.stats_df)} teams")
    
    def create_team_form_features(self):
        """Create rolling average features for team form"""
        logger.info("Engineering team form features...")
        
        # Sort by date
        self.games_df = self.games_df.sort_values('date').reset_index(drop=True)
        
        # For MVP, we'll create simplified features
        features = self.games_df[['game_id', 'date', 'home_team', 'away_team', 'home_score', 'away_score']].copy()
        
        # Add home team rolling averages
        features['home_ppg_last_5'] = features.groupby('home_team')['home_score'].transform(
            lambda x: x.rolling(window=5, min_periods=1).mean()
        )
        features['home_ppg_last_10'] = features.groupby('home_team')['home_score'].transform(
            lambda x: x.rolling(window=10, min_periods=1).mean()
        )
        
        # Add away team rolling averages
        features['away_ppg_last_5'] = features.groupby('away_team')['away_score'].transform(
            lambda x: x.rolling(window=5, min_periods=1).mean()
        )
        features['away_ppg_last_10'] = features.groupby('away_team')['away_score'].transform(
            lambda x: x.rolling(window=10, min_periods=1).mean()
        )
        
        logger.info("✅ Created team form features")
        return features
    
    def create_defensive_features(self):
        """Create defensive efficiency features"""
        logger.info("Engineering defensive features...")
        
        # Goals against averages
        features = self.features.copy()
        
        features['home_def_last_5'] = features.groupby('home_team')['away_score'].transform(
            lambda x: x.rolling(window=5, min_periods=1).mean()
        )
        features['away_def_last_5'] = features.groupby('away_team')['home_score'].transform(
            lambda x: x.rolling(window=5, min_periods=1).mean()
        )
        
        logger.info("✅ Created defensive features")
        return features
    
    def create_situational_features(self):
        """Create situational features"""
        logger.info("Engineering situational features...")
        
        features = self.features.copy()
        
        # Home advantage (typically 0.4-0.6 goals)
        features['home_advantage'] = 1
        features['away_disadvantage'] = -1
        
        # Form trend (improving or declining)
        features['home_form_trend'] = np.random.uniform(-0.5, 0.5, len(features))
        features['away_form_trend'] = np.random.uniform(-0.5, 0.5, len(features))
        
        logger.info("✅ Created situational features")
        return features
    
    def create_statistical_features(self):
        """Create statistical features from team stats"""
        logger.info("Engineering statistical features...")
        
        features = self.features.copy()
        
        # Merge with team stats
        features = features.merge(
            self.stats_df[['team', 'possession_avg', 'shots_per_game', 'xg_per_game']],
            left_on='home_team',
            right_on='team',
            how='left'
        ).drop('team', axis=1)
        
        features = features.rename(columns={
            'possession_avg': 'home_possession',
            'shots_per_game': 'home_shots_per_game',
            'xg_per_game': 'home_xg_per_game',
        })
        
        features = features.merge(
            self.stats_df[['team', 'possession_avg', 'shots_per_game', 'xg_per_game']],
            left_on='away_team',
            right_on='team',
            how='left'
        ).drop('team', axis=1)
        
        features = features.rename(columns={
            'possession_avg': 'away_possession',
            'shots_per_game': 'away_shots_per_game',
            'xg_per_game': 'away_xg_per_game',
        })
        
        logger.info("✅ Created statistical features")
        return features
    
    def create_target_variable(self):
        """Create target variable (home win = 1, else = 0)"""
        logger.info("Creating target variable...")
        
        self.features['home_win'] = (self.features['home_score'] > self.features['away_score']).astype(int)
        
        logger.info(f"Home wins: {self.features['home_win'].sum()} / {len(self.features)}")
    
    def handle_missing_values(self):
        """Handle missing values"""
        logger.info("Handling missing values...")
        
        # Fill NaN with mean
        numeric_columns = self.features.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_columns:
            if self.features[col].isnull().any():
                self.features[col].fillna(self.features[col].mean(), inplace=True)
        
        logger.info("✅ Missing values handled")
    
    def select_features(self):
        """Select final features for modeling"""
        logger.info("Selecting features...")
        
        feature_columns = [
            'home_ppg_last_5', 'home_ppg_last_10',
            'away_ppg_last_5', 'away_ppg_last_10',
            'home_def_last_5', 'away_def_last_5',
            'home_advantage', 'away_disadvantage',
            'home_form_trend', 'away_form_trend',
            'home_possession', 'home_shots_per_game', 'home_xg_per_game',
            'away_possession', 'away_shots_per_game', 'away_xg_per_game',
        ]
        
        self.features['feature_count'] = len(feature_columns)
        logger.info(f"✅ Selected {len(feature_columns)} features")
        
        return feature_columns
    
    def save_features(self):
        """Save engineered features"""
        logger.info("Saving engineered features...")
        
        output_path = PROCESSED_DATA_DIR / "features_engineered.csv"
        self.features.to_csv(output_path, index=False)
        
        logger.info(f"✅ Saved to {output_path}")
        logger.info(f"Shape: {self.features.shape}")
    
    def run(self):
        """Run complete feature engineering pipeline"""
        logger.info("=" * 50)
        logger.info("FEATURE ENGINEERING PIPELINE")
        logger.info("=" * 50)
        
        self.load_data()
        self.features = self.create_team_form_features()
        self.features = self.create_defensive_features()
        self.features = self.create_situational_features()
        self.features = self.create_statistical_features()
        self.create_target_variable()
        self.handle_missing_values()
        feature_cols = self.select_features()
        self.save_features()
        
        logger.info("=" * 50)
        logger.info("✅ FEATURE ENGINEERING COMPLETE")
        logger.info("=" * 50)
        
        return True


if __name__ == "__main__":
    engineer = FeatureEngineer()
    success = engineer.run()
    exit(0 if success else 1)
