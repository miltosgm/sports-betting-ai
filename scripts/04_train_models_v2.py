#!/usr/bin/env python3
"""
Phase 2: Enhanced Model Training
Trains XGBoost, LightGBM, RandomForest with optimized hyperparameters
Creates weighted ensemble voting
"""

import pandas as pd
import numpy as np
import pickle
import json
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, f1_score, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROCESSED_DATA_DIR = Path(__file__).parent.parent / "data" / "processed"
MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


class EnhancedModelTrainer:
    """Trains multiple ML models with optimized hyperparameters"""
    
    def __init__(self):
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.models = {}
        self.metrics = {}
        self.model_weights = {}
        self.feature_names = []
        self.scaler = StandardScaler()
        
    def load_features(self):
        """Load engineered features"""
        logger.info("Loading features...")
        
        # Try v2 features first, fall back to v1
        feature_file = PROCESSED_DATA_DIR / "features_engineered_v2.csv"
        if not feature_file.exists():
            feature_file = PROCESSED_DATA_DIR / "features_engineered.csv"
        
        df = pd.read_csv(feature_file)
        
        # Define features - match what feature engineering created
        feature_cols = [col for col in df.columns if col not in 
                       ['game_id', 'date', 'home_team', 'away_team', 'home_score', 'away_score', 
                        'feature_count', 'home_win', 'temperature', 'humidity', 'wind_speed', 
                        'precipitation_chance', 'adverse_weather']]
        
        # Remove non-numeric columns
        feature_cols = [col for col in feature_cols if df[col].dtype in ['float64', 'int64']]
        
        self.feature_names = feature_cols
        
        X = df[feature_cols].fillna(0)
        y = df['home_win'] if 'home_win' in df.columns else (df['home_score'] > df['away_score']).astype(int)
        
        logger.info(f"✅ Loaded {len(X)} samples with {len(feature_cols)} features")
        logger.info(f"   Class distribution: {y.value_counts().to_dict()}")
        logger.info(f"   Features: {feature_cols[:5]}...")
        
        return X, y, feature_cols
    
    def split_data(self, X, y, test_size=0.2):
        """Split data for training/testing"""
        logger.info(f"Splitting data ({int((1-test_size)*100)}/{int(test_size*100)})...")
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
        )
        
        # Scale features
        self.X_train = self.scaler.fit_transform(self.X_train)
        self.X_test = self.scaler.transform(self.X_test)
        
        logger.info(f"✅ Train set: {len(self.X_train)} samples")
        logger.info(f"   Test set: {len(self.X_test)} samples")
    
    def train_xgboost(self):
        """Train optimized XGBoost model"""
        logger.info("Training XGBoost (optimized hyperparameters)...")
        
        model = XGBClassifier(
            n_estimators=200,           # More trees than baseline
            max_depth=6,                # Slightly deeper trees
            learning_rate=0.05,         # Lower learning rate for better generalization
            subsample=0.8,              # Subsample 80% of training data
            colsample_bytree=0.8,       # Subsample 80% of features
            min_child_weight=1,
            gamma=1,                    # Regularization
            reg_alpha=0.1,              # L1 regularization
            reg_lambda=1,               # L2 regularization
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss',
            n_jobs=-1
        )
        
        model.fit(self.X_train, self.y_train, verbose=0)
        self.models['xgboost'] = model
        logger.info("✅ XGBoost trained")
        
        return model
    
    def train_lightgbm(self):
        """Train optimized LightGBM model"""
        logger.info("Training LightGBM (optimized hyperparameters)...")
        
        model = LGBMClassifier(
            n_estimators=200,
            max_depth=7,
            learning_rate=0.05,
            num_leaves=31,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_samples=5,
            reg_alpha=0.1,
            reg_lambda=1,
            random_state=42,
            verbose=-1,
            n_jobs=-1
        )
        
        model.fit(self.X_train, self.y_train)
        self.models['lightgbm'] = model
        logger.info("✅ LightGBM trained")
        
        return model
    
    def train_random_forest(self):
        """Train RandomForest as third model"""
        logger.info("Training RandomForest...")
        
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features='sqrt',
            bootstrap=True,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(self.X_train, self.y_train)
        self.models['random_forest'] = model
        logger.info("✅ RandomForest trained")
        
        return model
    
    def evaluate_model(self, name, model, y_pred, y_pred_proba=None):
        """Evaluate model performance"""
        logger.info(f"Evaluating {name}...")
        
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred, zero_division=0)
        recall = recall_score(self.y_test, y_pred, zero_division=0)
        f1 = f1_score(self.y_test, y_pred, zero_division=0)
        
        metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
        }
        
        if y_pred_proba is not None:
            try:
                auc = roc_auc_score(self.y_test, y_pred_proba)
                metrics['auc_roc'] = float(auc)
            except:
                pass
        
        self.metrics[name] = metrics
        
        logger.info(f"  Accuracy:  {accuracy:.4f}")
        logger.info(f"  Precision: {precision:.4f}")
        logger.info(f"  Recall:    {recall:.4f}")
        logger.info(f"  F1-Score:  {f1:.4f}")
        
        return metrics
    
    def evaluate_all_models(self):
        """Evaluate all models"""
        logger.info("=" * 60)
        logger.info("MODEL EVALUATION")
        logger.info("=" * 60)
        
        for name, model in self.models.items():
            y_pred = model.predict(self.X_test)
            try:
                y_proba = model.predict_proba(self.X_test)[:, 1]
            except:
                y_proba = None
            
            self.evaluate_model(name, model, y_pred, y_proba)
    
    def create_weighted_ensemble(self):
        """Create weighted ensemble based on model accuracy"""
        logger.info("Creating weighted ensemble...")
        
        # Calculate weights based on accuracy
        total_accuracy = sum(m['accuracy'] for m in self.metrics.values())
        
        for name, metrics in self.metrics.items():
            weight = metrics['accuracy'] / total_accuracy if total_accuracy > 0 else 1 / len(self.metrics)
            self.model_weights[name] = weight
            logger.info(f"  {name}: weight = {weight:.4f} (accuracy: {metrics['accuracy']:.4f})")
        
        logger.info("✅ Ensemble weights calculated")
        
        return self.model_weights
    
    def predict_ensemble(self, X):
        """Make ensemble predictions with weighted voting"""
        ensemble_proba = np.zeros(len(X))
        
        for name, model in self.models.items():
            weight = self.model_weights.get(name, 1 / len(self.models))
            
            try:
                proba = model.predict_proba(X)[:, 1]
            except:
                proba = model.predict(X).astype(float)
            
            ensemble_proba += weight * proba
        
        return (ensemble_proba > 0.5).astype(int), ensemble_proba
    
    def get_feature_importance(self):
        """Extract feature importance from models"""
        logger.info("Extracting feature importance...")
        
        importance_dict = {}
        
        # XGBoost importance
        if 'xgboost' in self.models:
            xgb_importance = self.models['xgboost'].feature_importances_
            importance_dict['xgboost'] = dict(zip(self.feature_names, xgb_importance))
        
        # LightGBM importance
        if 'lightgbm' in self.models:
            lgb_importance = self.models['lightgbm'].feature_importances_
            importance_dict['lightgbm'] = dict(zip(self.feature_names, lgb_importance))
        
        # RandomForest importance
        if 'random_forest' in self.models:
            rf_importance = self.models['random_forest'].feature_importances_
            importance_dict['random_forest'] = dict(zip(self.feature_names, rf_importance))
        
        # Ensemble importance (average across models)
        ensemble_importance = {}
        for feature in self.feature_names:
            importances = []
            for model_imp in importance_dict.values():
                importances.append(model_imp.get(feature, 0))
            ensemble_importance[feature] = np.mean(importances)
        
        # Sort by importance
        sorted_importance = sorted(ensemble_importance.items(), key=lambda x: x[1], reverse=True)
        
        logger.info("\n🎯 TOP 20 MOST IMPORTANT FEATURES:")
        print("-" * 60)
        for idx, (feature, importance) in enumerate(sorted_importance[:20], 1):
            print(f"{idx:2d}. {feature:40s} {importance:8.4f}")
        print("-" * 60)
        
        return importance_dict, dict(sorted_importance)
    
    def save_models(self):
        """Save trained models"""
        logger.info("Saving models...")
        
        # Save individual models
        for name, model in self.models.items():
            path = MODELS_DIR / f"{name}_model_v2.pkl"
            pickle.dump(model, open(path, 'wb'))
            logger.info(f"  Saved {name} to {path}")
        
        # Save scaler
        scaler_path = MODELS_DIR / "scaler_v2.pkl"
        pickle.dump(self.scaler, open(scaler_path, 'wb'))
        
        # Save ensemble with weights
        ensemble_dict = {
            'models': self.models,
            'weights': self.model_weights,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }
        
        ensemble_path = MODELS_DIR / "ensemble_model_v2.pkl"
        pickle.dump(ensemble_dict, open(ensemble_path, 'wb'))
        logger.info(f"  Saved ensemble to {ensemble_path}")
        
        # Save metrics
        metrics_path = MODELS_DIR / "model_metrics_v2.json"
        with open(metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        logger.info(f"  Saved metrics to {metrics_path}")
        
        # Save feature importance
        importance_path = MODELS_DIR / "feature_importance_v2.json"
        _, sorted_importance = self.get_feature_importance()
        with open(importance_path, 'w') as f:
            json.dump(sorted_importance, f, indent=2)
        logger.info(f"  Saved feature importance to {importance_path}")
    
    def print_summary(self):
        """Print training summary"""
        logger.info("=" * 70)
        logger.info("TRAINING SUMMARY - MODEL COMPARISON")
        logger.info("=" * 70)
        
        print("\nModel Performance Comparison:")
        print("-" * 80)
        print(f"{'Model':<15} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
        print("-" * 80)
        
        for name, metrics in self.metrics.items():
            acc = metrics['accuracy']
            prec = metrics['precision']
            rec = metrics['recall']
            f1 = metrics['f1_score']
            print(f"{name:<15} {acc:.4f}       {prec:.4f}       {rec:.4f}       {f1:.4f}")
        
        print("-" * 80)
        
        # Ensemble evaluation
        ensemble_pred, _ = self.predict_ensemble(self.X_test)
        ensemble_acc = accuracy_score(self.y_test, ensemble_pred)
        ensemble_prec = precision_score(self.y_test, ensemble_pred, zero_division=0)
        ensemble_rec = recall_score(self.y_test, ensemble_pred, zero_division=0)
        ensemble_f1 = f1_score(self.y_test, ensemble_pred, zero_division=0)
        
        print(f"{'ENSEMBLE':<15} {ensemble_acc:.4f}       {ensemble_prec:.4f}       {ensemble_rec:.4f}       {ensemble_f1:.4f}")
        print("-" * 80)
        print("\n💡 RECOMMENDATION: Use WEIGHTED ENSEMBLE for best performance")
        print(f"   Weights: {', '.join([f'{k}={v:.3f}' for k, v in self.model_weights.items()])}")
        print("=" * 70)
    
    def run(self):
        """Run complete training pipeline"""
        logger.info("=" * 70)
        logger.info("PHASE 2: ENHANCED MODEL TRAINING PIPELINE")
        logger.info("=" * 70)
        
        X, y, feature_cols = self.load_features()
        self.split_data(X, y, test_size=0.2)
        
        # Train all models
        self.train_xgboost()
        self.train_lightgbm()
        self.train_random_forest()
        
        # Evaluate models
        self.evaluate_all_models()
        
        # Create weighted ensemble
        self.create_weighted_ensemble()
        
        # Save everything
        self.save_models()
        
        # Print summary
        self.print_summary()
        
        logger.info("=" * 70)
        logger.info("✅ PHASE 2: MODEL TRAINING COMPLETE")
        logger.info("=" * 70)
        
        return True


if __name__ == "__main__":
    trainer = EnhancedModelTrainer()
    success = trainer.run()
    exit(0 if success else 1)
