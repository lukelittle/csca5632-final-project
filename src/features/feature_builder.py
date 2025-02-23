"""
Feature engineering for NBA team pattern analysis.

This module provides a feature engineering pipeline for NBA team pattern analysis,
creating features for clustering, dimensionality reduction, and anomaly detection.
"""
import pandas as pd
import numpy as np
from datetime import datetime

class FeatureBuilder:
    def __init__(self):
        """Initialize the FeatureBuilder with required column definitions."""
        self.feature_stats = {}
        
        # Define required columns for each data source
        self._required_team_cols = [
            'season', 'team', 'pts_per_game', 'fg_per_game',
            'fga_per_game', 'ft_per_game', 'fta_per_game', 'x3p_per_game',
            'x3pa_per_game', 'orb_per_game', 'drb_per_game', 'ast_per_game',
            'stl_per_game', 'blk_per_game', 'tov_per_game'
        ]
        
        self._required_player_cols = [
            'season', 'team', 'experience', 'age', 'player'
        ]
        
        self._required_injury_cols = [
            'year', 'team', 'count'
        ]
    
    def _validate_columns(self, df: pd.DataFrame, required_cols: list, source: str) -> None:
        """Validate that required columns are present in the DataFrame."""
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in {source} data: {missing_cols}")

    def create_style_features(self, team_stats: pd.DataFrame) -> pd.DataFrame:
        """Create features that capture team playing styles and strategies."""
        self._validate_columns(team_stats, self._required_team_cols, "team")
        df = team_stats.copy()
        
        # Offensive style features
        df['pace_factor'] = (
            df['fga_per_game'] + 
            0.44 * df['fta_per_game'] - 
            df['orb_per_game'] + 
            df['tov_per_game']
        )
        df['three_point_rate'] = df['x3pa_per_game'] / df['fga_per_game']
        df['assist_rate'] = df['ast_per_game'] / df['fg_per_game']
        
        # Defensive style features
        df['defensive_pressure'] = df['stl_per_game'] + df['blk_per_game']
        df['paint_protection'] = df['blk_per_game'] / (df['fga_per_game'] - df['x3pa_per_game'])
        df['transition_rate'] = df['stl_per_game'] / df['tov_per_game']
        
        # Ball movement features
        df['ball_control'] = df['ast_per_game'] / df['tov_per_game']
        df['passing_efficiency'] = df['ast_per_game'] / df['fga_per_game']
        
        # Shot selection features
        df['inside_focus'] = (df['fga_per_game'] - df['x3pa_per_game']) / df['fga_per_game']
        df['free_throw_rate'] = df['fta_per_game'] / df['fga_per_game']
        
        self.feature_stats['style_features'] = {
            'n_features': len(df.columns),
            'n_samples': len(df)
        }
        
        return df[['team', 'season'] + [col for col in df.columns if col not in ['team', 'season']]]

    def create_composition_features(self, player_stats: pd.DataFrame, injuries: pd.DataFrame) -> pd.DataFrame:
        """Create features that describe team roster composition."""
        self._validate_columns(player_stats, self._required_player_cols, "player")
        self._validate_columns(injuries, self._required_injury_cols, "injuries")
        
        # Process player stats
        player_stats = player_stats.copy()
        injuries = injuries.copy()
        
        # Calculate roster stability
        roster_changes = player_stats.groupby(['team', 'season'])['player'].agg([
            ('roster_size', 'count'),
            ('unique_players', 'nunique')
        ])
        roster_changes['roster_stability'] = roster_changes['roster_size'] / roster_changes['unique_players']
        
        # Experience distribution features
        exp_stats = player_stats.groupby(['team', 'season'])['experience'].agg([
            ('experience_mean', 'mean'),
            ('experience_var', 'var'),
            ('experience_skew', lambda x: x.skew())
        ]).fillna(0)
        
        # Age distribution features
        age_stats = player_stats.groupby(['team', 'season'])['age'].agg([
            ('age_mean', 'mean'),
            ('age_var', 'var'),
            ('age_skew', lambda x: x.skew())
        ]).fillna(0)
        
        # Injury features
        injuries = injuries.rename(columns={'year': 'season'})
        injury_stats = injuries.groupby(['team', 'season']).agg({
            'count': ['sum', 'mean']
        }).fillna(0)
        injury_stats.columns = ['injury_total', 'injury_rate']
        
        # Combine all features
        features = pd.concat([
            roster_changes,
            exp_stats,
            age_stats,
            injury_stats
        ], axis=1).reset_index()
        
        # Calculate depth score
        features['depth_score'] = features['roster_stability'] * (1 / (features['injury_rate'] + 1))
        
        self.feature_stats['composition_features'] = {
            'n_features': len(features.columns),
            'n_samples': len(features)
        }
        
        return features

    def create_pattern_features(self, team_stats: pd.DataFrame) -> pd.DataFrame:
        """Create features that capture team performance patterns."""
        self._validate_columns(team_stats, self._required_team_cols, "team")
        df = team_stats.copy()
        
        # Efficiency features
        df['true_shooting'] = df['pts_per_game'] / (2 * (df['fga_per_game'] + 0.44 * df['fta_per_game']))
        df['off_efficiency'] = df['pts_per_game'] / (
            df['fga_per_game'] + 
            0.44 * df['fta_per_game'] - 
            df['orb_per_game'] + 
            df['tov_per_game']
        )
        df['def_efficiency'] = (df['stl_per_game'] + df['blk_per_game']) / df['tov_per_game']
        
        # Performance consistency features
        df['scoring_consistency'] = df['pts_per_game'] / df['fga_per_game']
        df['defensive_consistency'] = (df['stl_per_game'] + df['blk_per_game']) / df['tov_per_game']
        
        # Strategic tendency features
        df['inside_outside_balance'] = df['x3pa_per_game'] / (df['fga_per_game'] - df['x3pa_per_game'])
        df['playmaking_tendency'] = df['ast_per_game'] / (df['fga_per_game'] + df['fta_per_game'])
        
        # Create composite scores
        df['offensive_rating'] = (
            0.4 * df['true_shooting'] +
            0.3 * df['off_efficiency'] +
            0.3 * df['scoring_consistency']
        )
        df['defensive_rating'] = (
            0.4 * df['def_efficiency'] +
            0.3 * df['defensive_consistency'] +
            0.3 * (df['stl_per_game'] + df['blk_per_game'])
        )
        df['consistency_score'] = (
            df['offensive_rating'] * df['defensive_rating']
        )
        
        self.feature_stats['pattern_features'] = {
            'n_features': len(df.columns),
            'n_samples': len(df)
        }
        
        return df[['team', 'season'] + [col for col in df.columns if col not in ['team', 'season']]]

    def combine_features(self, style_features: pd.DataFrame, composition_features: pd.DataFrame,
                        pattern_features: pd.DataFrame) -> pd.DataFrame:
        """Combine all feature sets for unsupervised learning analysis."""
        # Create copies to avoid modifying originals
        style_features = style_features.copy()
        composition_features = composition_features.copy()
        pattern_features = pattern_features.copy()
        
        # Ensure team and season columns are the correct type
        for df in [style_features, composition_features, pattern_features]:
            df['team'] = df['team'].astype(str)
            df['season'] = df['season'].astype(int)
        
        # Merge all features
        features = style_features.merge(
            composition_features,
            on=['team', 'season'],
            how='left'
        ).merge(
            pattern_features,
            on=['team', 'season'],
            how='left'
        )
        
        # Handle missing values
        numeric_cols = features.select_dtypes(include=['int64', 'float64']).columns
        features[numeric_cols] = features[numeric_cols].fillna(features[numeric_cols].mean())
        
        # Update feature statistics
        self.feature_stats['combined_features'] = {
            'n_features': len(features.columns) - 2,  # Exclude team and season
            'n_samples': len(features),
            'feature_names': list(features.columns),
            'feature_types': {
                'style': list(style_features.columns),
                'composition': list(composition_features.columns),
                'pattern': list(pattern_features.columns)
            }
        }
        
        return features
