#!/usr/bin/env python3
"""
Phase 1-3: Enhanced Feature Engineering for Premier League Predictions
Expands features from 20 to 30+ with injury, form, travel, and motivation factors
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime, timedelta
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RAW_DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DATA_DIR = Path(__file__).parent.parent / "data" / "processed"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


class EnhancedFeatureEngineer:
    """Creates 30+ predictive features for Premier League games"""
    
    def __init__(self):
        self.games_df = None
        self.stats_df = None
        self.injuries_df = None
        self.features = None
        self.team_distances = {}  # Stadium distances for travel fatigue
        self.team_historical_records = {}  # H2H records
        
    def _generate_synthetic_data(self, num_games=760):
        """Generate synthetic historical data for training if limited data available"""
        logger.info(f"Generating synthetic training data ({num_games} games)...")
        
        teams = [
            'Manchester City', 'Liverpool', 'Arsenal', 'Chelsea', 'Tottenham',
            'Newcastle', 'Manchester United', 'Aston Villa', 'Brighton', 'Wolverhampton',
            'Fulham', 'Bournemouth', 'Brentford', 'Everton', 'West Ham',
            'Crystal Palace', 'Nottingham Forest', 'Leicester', 'Southampton', 'Ipswich'
        ]
        
        # City stadium coordinates (for travel distance calculation)
        self.stadium_locations = {
            'Manchester City': (53.4830, -2.2001),
            'Liverpool': (53.4309, -2.9609),
            'Arsenal': (51.5549, -0.1084),
            'Chelsea': (51.4820, -0.1910),
            'Tottenham': (51.6039, -0.0666),
            'Newcastle': (54.9750, -1.6220),
            'Manchester United': (53.4630, -2.2913),
            'Aston Villa': (52.5086, -1.8853),
            'Brighton': (50.8604, -0.0832),
            'Wolverhampton': (52.6392, -2.1298),
            'Fulham': (51.4755, -0.2225),
            'Bournemouth': (50.7352, -1.8379),
            'Brentford': (51.4914, -0.2927),
            'Everton': (53.4387, -2.6660),
            'West Ham': (51.5388, -0.0161),
            'Crystal Palace': (51.3981, -0.0852),
            'Nottingham Forest': (52.9397, -1.1330),
            'Leicester': (52.6203, -1.1425),
            'Southampton': (50.9061, -1.3910),
            'Ipswich': (52.0473, 1.2194),
        }
        
        games = []
        np.random.seed(42)
        
        # Generate games across 2 seasons
        start_date = datetime(2022, 8, 1)
        game_count = 0
        
        for week in range(num_games // 10):  # 10 matches per week
            week_date = start_date + timedelta(weeks=week)
            available_teams = teams.copy()
            
            for _ in range(10):
                if len(available_teams) < 2:
                    available_teams = teams.copy()
                
                home_idx = np.random.randint(0, len(available_teams))
                home = available_teams.pop(home_idx)
                
                away_idx = np.random.randint(0, len(available_teams))
                away = available_teams.pop(away_idx)
                
                # Realistic score distribution
                rand = np.random.random()
                if rand < 0.45:  # Home win (45%)
                    home_score = np.random.choice([1, 2, 3, 4], p=[0.3, 0.5, 0.15, 0.05])
                    away_score = max(0, home_score - np.random.randint(1, 3))
                elif rand < 0.75:  # Draw or away win (30%)
                    home_score = np.random.randint(0, 3)
                    away_score = home_score
                else:  # Away win (25%)
                    away_score = np.random.choice([1, 2, 3], p=[0.5, 0.35, 0.15])
                    home_score = max(0, away_score - np.random.randint(1, 2))
                
                # Expected goals with some correlation
                home_xg = 0.8 + 0.5 * home_score + np.random.normal(0, 0.3)
                away_xg = 0.8 + 0.5 * away_score + np.random.normal(0, 0.3)
                
                games.append({
                    'game_id': f'PL_{week}_{_:03d}',
                    'date': week_date + timedelta(days=_),
                    'season': '2023-25' if week < 38 else '2024-25',
                    'home_team': home,
                    'away_team': away,
                    'home_score': int(home_score),
                    'away_score': int(away_score),
                    'home_xg': round(home_xg, 2),
                    'away_xg': round(away_xg, 2),
                    'home_shots': int(np.random.uniform(8, 18)),
                    'away_shots': int(np.random.uniform(6, 16)),
                    'home_possession': int(np.random.uniform(35, 65)),
                    'away_possession': int(np.random.uniform(35, 65)),
                })
                
                game_count += 1
                if game_count >= num_games:
                    break
            
            if game_count >= num_games:
                break
        
        return pd.DataFrame(games[:num_games])
    
    def load_data(self):
        """Load raw data or generate synthetic if limited"""
        logger.info("Loading raw data...")
        
        try:
            self.games_df = pd.read_csv(RAW_DATA_DIR / "games_2024-25.csv")
            if len(self.games_df) < 100:
                logger.warning(f"Limited games found ({len(self.games_df)}), augmenting with synthetic data...")
                synthetic = self._generate_synthetic_data(760)
                self.games_df = pd.concat([self.games_df, synthetic], ignore_index=True)
        except:
            logger.warning("No games data found, generating synthetic dataset...")
            self.games_df = self._generate_synthetic_data(760)
        
        try:
            self.stats_df = pd.read_csv(RAW_DATA_DIR / "team_stats_2024-25.csv")
        except:
            self.stats_df = pd.DataFrame()  # Empty, will handle below
        
        logger.info(f"✅ Loaded {len(self.games_df)} games")
        return self.games_df
    
    def create_team_form_features(self):
        """Create rolling average features for team form (last 3, 5, 10 games)"""
        logger.info("Engineering team form features...")
        
        # Ensure date is datetime
        self.games_df['date'] = pd.to_datetime(self.games_df['date'])
        self.games_df = self.games_df.sort_values('date').reset_index(drop=True)
        features = self.games_df[['game_id', 'date', 'home_team', 'away_team', 'home_score', 'away_score']].copy()
        
        # HOME TEAM FORM
        features['home_ppg_last_3'] = features.groupby('home_team')['home_score'].transform(
            lambda x: x.rolling(window=3, min_periods=1).mean()
        )
        features['home_ppg_last_5'] = features.groupby('home_team')['home_score'].transform(
            lambda x: x.rolling(window=5, min_periods=1).mean()
        )
        features['home_ppg_last_10'] = features.groupby('home_team')['home_score'].transform(
            lambda x: x.rolling(window=10, min_periods=1).mean()
        )
        
        # AWAY TEAM FORM
        features['away_ppg_last_3'] = features.groupby('away_team')['away_score'].transform(
            lambda x: x.rolling(window=3, min_periods=1).mean()
        )
        features['away_ppg_last_5'] = features.groupby('away_team')['away_score'].transform(
            lambda x: x.rolling(window=5, min_periods=1).mean()
        )
        features['away_ppg_last_10'] = features.groupby('away_team')['away_score'].transform(
            lambda x: x.rolling(window=10, min_periods=1).mean()
        )
        
        # RECENCY-WEIGHTED MOMENTUM (more weight to recent games)
        # Last 3 games with 60% weight on most recent
        def weighted_momentum_3(x):
            if len(x) == 0:
                return 0
            weights = np.array([0.2, 0.3, 0.5])
            values = x.tail(3).values
            if len(values) == 1:
                return values[0]
            elif len(values) == 2:
                weights = np.array([0.4, 0.6])
            return np.sum(values * weights[:len(values)])
        
        features['home_momentum'] = features.groupby('home_team')['home_score'].transform(weighted_momentum_3)
        features['away_momentum'] = features.groupby('away_team')['away_score'].transform(weighted_momentum_3)
        
        logger.info("✅ Created team form features (16 features)")
        return features
    
    def create_defensive_features(self):
        """Create defensive efficiency features"""
        logger.info("Engineering defensive features...")
        
        features = self.features.copy()
        
        # Goals against averages
        features['home_def_last_3'] = features.groupby('home_team')['away_score'].transform(
            lambda x: x.rolling(window=3, min_periods=1).mean()
        )
        features['home_def_last_5'] = features.groupby('home_team')['away_score'].transform(
            lambda x: x.rolling(window=5, min_periods=1).mean()
        )
        
        features['away_def_last_3'] = features.groupby('away_team')['home_score'].transform(
            lambda x: x.rolling(window=3, min_periods=1).mean()
        )
        features['away_def_last_5'] = features.groupby('away_team')['home_score'].transform(
            lambda x: x.rolling(window=5, min_periods=1).mean()
        )
        
        # Goal difference (offensive - defensive)
        features['home_goal_diff'] = features['home_ppg_last_5'] - features['home_def_last_5']
        features['away_goal_diff'] = features['away_ppg_last_5'] - features['away_def_last_5']
        
        logger.info("✅ Created defensive features (6 features)")
        return features
    
    def create_home_away_split_features(self):
        """Create separate home/away performance features"""
        logger.info("Engineering home/away split features...")
        
        features = self.features.copy()
        
        # For away teams, calculate their away record specifically
        features['away_ppg_away_last_5'] = features.groupby('away_team')['away_score'].transform(
            lambda x: x.rolling(window=5, min_periods=1).mean()
        )
        
        # Home team home record
        features['home_ppg_home_last_5'] = features.groupby('home_team')['home_score'].transform(
            lambda x: x.rolling(window=5, min_periods=1).mean()
        )
        
        # Win rates at home (simple calculation)
        def calc_home_win_rate(group):
            # For each game, check if home team won in last 5 games
            win_counts = []
            for i in range(len(group)):
                if i == 0:
                    win_counts.append(0.5)
                else:
                    last_5_wins = (group.iloc[max(0, i-5):i] > 0).sum()
                    last_5_games = min(i, 5)
                    win_counts.append(last_5_wins / last_5_games if last_5_games > 0 else 0.5)
            return pd.Series(win_counts, index=group.index)
        
        features['home_win_rate'] = features.groupby('home_team').apply(
            lambda x: calc_home_win_rate(x['home_score'])
        ).reset_index(level=0, drop=True)
        
        logger.info("✅ Created home/away split features (3 features)")
        return features
    
    def create_head_to_head_features(self):
        """Create head-to-head history features"""
        logger.info("Engineering head-to-head features...")
        
        features = self.features.copy()
        
        # Build H2H history
        def get_h2h_record(df, home_team, away_team, game_idx):
            """Get win % of home team in last 5 H2H matchups"""
            historical = df[:game_idx]
            h2h_games = historical[
                ((historical['home_team'] == home_team) & (historical['away_team'] == away_team)) |
                ((historical['home_team'] == away_team) & (historical['away_team'] == home_team))
            ]
            
            if len(h2h_games) == 0:
                return 0.5  # No history, assume 50%
            
            h2h_games = h2h_games.tail(5)  # Last 5 meetings
            wins = len(h2h_games[(h2h_games['home_team'] == home_team) & 
                               (h2h_games['home_score'] > h2h_games['away_score'])])
            return wins / len(h2h_games)
        
        h2h_records = []
        for idx, row in features.iterrows():
            h2h = get_h2h_record(self.games_df, row['home_team'], row['away_team'], idx)
            h2h_records.append(h2h)
        
        features['h2h_home_win_rate'] = h2h_records
        
        logger.info("✅ Created head-to-head features (1 feature)")
        return features
    
    def create_travel_fatigue_features(self):
        """Create travel fatigue features (rest days + distance)"""
        logger.info("Engineering travel fatigue features...")
        
        features = self.features.copy()
        
        # Calculate distance between stadiums
        def calc_distance(team1, team2):
            """Calculate distance between two stadiums in miles"""
            if team1 not in self.stadium_locations or team2 not in self.stadium_locations:
                return np.random.uniform(100, 400)  # Random distance if not found
            
            lat1, lon1 = self.stadium_locations[team1]
            lat2, lon2 = self.stadium_locations[team2]
            
            # Haversine formula
            from math import radians, sin, cos, sqrt, atan2
            R = 3959  # Earth's radius in miles
            
            dlat = radians(lat2 - lat1)
            dlon = radians(lon2 - lon1)
            a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            return R * c
        
        # Rest days between matches
        features['home_rest_days'] = features.groupby('home_team')['date'].transform(
            lambda x: x.diff().dt.days
        ).fillna(7)
        
        features['away_rest_days'] = features.groupby('away_team')['date'].transform(
            lambda x: x.diff().dt.days
        ).fillna(7)
        
        # Travel distance
        features['travel_distance'] = features.apply(
            lambda row: calc_distance(row['away_team'], row['home_team']), axis=1
        )
        
        # Travel fatigue score (distance / rest_days)
        features['away_travel_fatigue'] = features['travel_distance'] / (features['away_rest_days'] + 1)
        features['home_travel_advantage'] = -features['away_travel_fatigue']  # Home advantage from away fatigue
        
        logger.info("✅ Created travel fatigue features (4 features)")
        return features
    
    def create_weather_impact_features(self):
        """Create weather impact features"""
        logger.info("Engineering weather impact features...")
        
        features = self.features.copy()
        
        # Synthetic weather data (in real scenario, fetch from API)
        np.random.seed(features.index)
        features['temperature'] = np.random.uniform(35, 85, len(features))
        features['humidity'] = np.random.uniform(40, 95, len(features))
        features['wind_speed'] = np.random.exponential(2, len(features))  # mph
        features['precipitation_chance'] = np.random.uniform(0, 1, len(features))
        
        # Weather advantage modifier (home teams better adapted to local weather)
        # Bad weather generally reduces scoring
        features['adverse_weather'] = (features['wind_speed'] > 15) | (features['precipitation_chance'] > 0.6)
        features['weather_home_advantage_modifier'] = features['adverse_weather'].astype(float) * 0.15
        
        logger.info("✅ Created weather impact features (5 features)")
        return features
    
    def create_referee_bias_features(self):
        """Create referee bias features"""
        logger.info("Engineering referee bias features...")
        
        features = self.features.copy()
        
        # Synthetic referee data
        np.random.seed(features.index)
        features['ref_home_bias_history'] = np.random.uniform(-0.1, 0.2, len(features))
        
        # Home advantage in referee decisions (typically 0.1-0.15 goal difference)
        features['ref_bias_adjusted_ppg'] = features['home_ppg_last_5'] * (1 + features['ref_home_bias_history'])
        
        logger.info("✅ Created referee bias features (2 features)")
        return features
    
    def create_motivation_factors_features(self):
        """Create motivation factors (derbies, title race, relegation battle)"""
        logger.info("Engineering motivation factors...")
        
        features = self.features.copy()
        
        # Derby matches (same city/region)
        derby_pairs = [
            ('Manchester City', 'Manchester United'),
            ('Liverpool', 'Everton'),
            ('Arsenal', 'Tottenham'),
            ('Chelsea', 'Fulham'),
            ('West Ham', 'Tottenham'),
            ('Nottingham Forest', 'Leicester'),
        ]
        
        def is_derby(home, away):
            return any((home == d[0] and away == d[1]) or (home == d[1] and away == d[0]) for d in derby_pairs)
        
        features['is_derby'] = features.apply(lambda row: is_derby(row['home_team'], row['away_team']), axis=1).astype(int)
        
        # Title race position (top 6 = high motivation)
        # Relegation battle (bottom 4 = high motivation)
        top_6 = {'Manchester City', 'Liverpool', 'Arsenal', 'Chelsea', 'Tottenham', 'Newcastle'}
        bottom_4 = {'Southampton', 'Ipswich', 'Leicester', 'Everton'}
        
        features['home_in_title_race'] = features['home_team'].isin(top_6).astype(int)
        features['away_in_title_race'] = features['away_team'].isin(top_6).astype(int)
        features['home_in_relegation_battle'] = features['home_team'].isin(bottom_4).astype(int)
        features['away_in_relegation_battle'] = features['away_team'].isin(bottom_4).astype(int)
        
        # High motivation index
        features['home_motivation'] = (
            features['is_derby'] * 0.5 +
            features['home_in_title_race'] * 0.3 +
            features['home_in_relegation_battle'] * 0.4
        )
        features['away_motivation'] = (
            features['is_derby'] * 0.5 +
            features['away_in_title_race'] * 0.3 +
            features['away_in_relegation_battle'] * 0.4
        )
        
        logger.info("✅ Created motivation factors features (7 features)")
        return features
    
    def create_injury_impact_features(self):
        """Create injury impact features - key player absences"""
        logger.info("Engineering injury impact features...")
        
        features = self.features.copy()
        
        # Synthetic injury data - randomly assign key players as injured
        np.random.seed(42)
        teams = features['home_team'].unique()
        
        # Create injury impact (reduce expected goals by 10-30% per key player)
        features['home_key_injuries'] = np.random.uniform(0, 3, len(features)).astype(int)
        features['away_key_injuries'] = np.random.uniform(0, 3, len(features)).astype(int)
        
        # Injury impact on expected performance (each key player = 10% reduction)
        features['home_injury_impact'] = 1 - (features['home_key_injuries'] * 0.10)
        features['away_injury_impact'] = 1 - (features['away_key_injuries'] * 0.10)
        
        # Adjusted expected goals
        features['home_ppg_injury_adjusted'] = features['home_ppg_last_5'] * features['home_injury_impact']
        features['away_ppg_injury_adjusted'] = features['away_ppg_last_5'] * features['away_injury_impact']
        
        logger.info("✅ Created injury impact features (5 features)")
        return features
    
    def create_target_variable(self):
        """Create target variable (home win = 1, draw/loss = 0)"""
        logger.info("Creating target variable...")
        
        self.features['home_win'] = (self.features['home_score'] > self.features['away_score']).astype(int)
        
        home_wins = self.features['home_win'].sum()
        total = len(self.features)
        home_win_pct = (home_wins / total) * 100 if total > 0 else 0
        
        logger.info(f"✅ Home wins: {home_wins} / {total} ({home_win_pct:.1f}%)")
    
    def handle_missing_values(self):
        """Handle missing values"""
        logger.info("Handling missing values...")
        
        numeric_columns = self.features.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_columns:
            if self.features[col].isnull().any():
                self.features[col].fillna(self.features[col].mean(), inplace=True)
        
        logger.info("✅ Missing values handled")
    
    def select_features(self):
        """Select final features for modeling"""
        logger.info("Selecting final features...")
        
        feature_columns = [
            # Form features (8)
            'home_ppg_last_3', 'home_ppg_last_5', 'home_ppg_last_10', 'home_momentum',
            'away_ppg_last_3', 'away_ppg_last_5', 'away_ppg_last_10', 'away_momentum',
            
            # Defensive features (6)
            'home_def_last_3', 'home_def_last_5', 'away_def_last_3', 'away_def_last_5',
            'home_goal_diff', 'away_goal_diff',
            
            # Home/Away splits (3)
            'home_ppg_home_last_5', 'away_ppg_away_last_5', 'home_win_rate',
            
            # Head-to-head (1)
            'h2h_home_win_rate',
            
            # Travel & Fatigue (4)
            'home_rest_days', 'away_rest_days', 'away_travel_fatigue', 'home_travel_advantage',
            
            # Weather (1)
            'weather_home_advantage_modifier',
            
            # Referee Bias (1)
            'ref_home_bias_history',
            
            # Motivation (2)
            'home_motivation', 'away_motivation',
            
            # Injuries (3)
            'home_key_injuries', 'away_key_injuries', 'home_injury_impact', 'away_injury_impact'
        ]
        
        logger.info(f"✅ Selected {len(feature_columns)} features for modeling")
        return feature_columns
    
    def save_features(self, output_file="features_engineered_v2.csv"):
        """Save engineered features"""
        logger.info(f"Saving engineered features to {output_file}...")
        
        output_path = PROCESSED_DATA_DIR / output_file
        self.features.to_csv(output_path, index=False)
        
        logger.info(f"✅ Saved {len(self.features)} games with {len(self.features.columns)} columns")
        logger.info(f"   Output: {output_path}")
        
        return output_path
    
    def run(self):
        """Run complete feature engineering pipeline"""
        logger.info("=" * 70)
        logger.info("PHASE 1-3: ENHANCED FEATURE ENGINEERING PIPELINE")
        logger.info("=" * 70)
        
        self.load_data()
        self.features = self.create_team_form_features()
        self.features = self.create_defensive_features()
        self.features = self.create_home_away_split_features()
        self.features = self.create_head_to_head_features()
        self.features = self.create_travel_fatigue_features()
        self.features = self.create_weather_impact_features()
        self.features = self.create_referee_bias_features()
        self.features = self.create_motivation_factors_features()
        self.features = self.create_injury_impact_features()
        self.create_target_variable()
        self.handle_missing_values()
        feature_cols = self.select_features()
        
        output_path = self.save_features()
        
        logger.info("=" * 70)
        logger.info("✅ PHASE 1: FEATURE ENGINEERING COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Dataset size: {len(self.features)} games")
        logger.info(f"Feature count: {len(feature_cols)} features")
        logger.info(f"Output file: {output_path}")
        
        return feature_cols


if __name__ == "__main__":
    engineer = EnhancedFeatureEngineer()
    feature_cols = engineer.run()
    exit(0)
