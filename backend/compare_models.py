"""
Model comparison script to find best algorithm for Indonesian stocks
Based on research showing different algorithms work best for different markets
"""
import asyncio
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import xgboost as xgb
import lightgbm as lgb
from loguru import logger
import time

from services.qlib_handler import QlibHandler
from config import settings


class ModelComparator:
    """Compare different ML algorithms for stock prediction"""

    def __init__(self):
        self.qlib_handler = QlibHandler()
        self.models = {
            'Gradient Boosting': GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            ),
            'Random Forest': RandomForestRegressor(
                n_estimators=100,
                max_depth=5,
                random_state=42,
                n_jobs=-1  # Use all CPU cores
            ),
            'XGBoost': xgb.XGBRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            ),
            'LightGBM': lgb.LGBMRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42,
                verbose=-1
            ),
            'SVR (RBF)': SVR(
                kernel='rbf',
                C=1.0,
                gamma='scale'
            ),
            'Ridge Regression': Ridge(
                alpha=1.0,
                random_state=42
            )
        }

    async def compare_models(self, symbol: str = 'BBCA'):
        """
        Compare all models for a given stock

        Args:
            symbol: Stock symbol to test

        Returns:
            DataFrame with model comparison results
        """
        logger.info(f"Starting model comparison for {symbol}")

        # Prepare data
        data = await self.qlib_handler.prepare_data_for_analysis(symbol)
        if data is None or data.empty:
            logger.error(f"No data available for {symbol}")
            return None

        # Get features
        feature_cols = self.qlib_handler.get_feature_columns()
        data['target'] = data['return'].shift(-1)
        data = data.dropna(subset=feature_cols + ['target'])

        if len(data) < 100:
            logger.error(f"Insufficient data: {len(data)} records")
            return None

        X = data[feature_cols].values
        y = data['target'].values

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, shuffle=False
        )

        results = []

        # Test each model
        for model_name, model in self.models.items():
            logger.info(f"Testing {model_name}...")

            try:
                # Training time
                start_time = time.time()
                model.fit(X_train, y_train)
                train_time = time.time() - start_time

                # Predictions
                y_train_pred = model.predict(X_train)
                y_test_pred = model.predict(X_test)

                # Metrics
                train_r2 = r2_score(y_train, y_train_pred)
                test_r2 = r2_score(y_test, y_test_pred)
                test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
                test_mae = mean_absolute_error(y_test, y_test_pred)

                # Cross-validation score (time-consuming, so we do fewer folds)
                cv_scores = cross_val_score(
                    model, X_train, y_train,
                    cv=3,  # 3-fold cross-validation
                    scoring='r2'
                )

                results.append({
                    'Model': model_name,
                    'Train R²': f'{train_r2:.4f}',
                    'Test R²': f'{test_r2:.4f}',
                    'CV R² (mean)': f'{cv_scores.mean():.4f}',
                    'CV R² (std)': f'{cv_scores.std():.4f}',
                    'Test RMSE': f'{test_rmse:.6f}',
                    'Test MAE': f'{test_mae:.6f}',
                    'Train Time (s)': f'{train_time:.2f}',
                    'Overfitting': f'{(train_r2 - test_r2):.4f}'
                })

                logger.info(f"✓ {model_name}: Test R²={test_r2:.4f}, Time={train_time:.2f}s")

            except Exception as e:
                logger.error(f"✗ {model_name} failed: {str(e)}")
                results.append({
                    'Model': model_name,
                    'Error': str(e)
                })

        # Create results DataFrame
        df_results = pd.DataFrame(results)

        # Sort by Test R² (descending)
        if 'Test R²' in df_results.columns:
            df_results = df_results.sort_values('Test R²', ascending=False)

        return df_results


async def main():
    """Run model comparison"""
    comparator = ModelComparator()

    # Test stocks
    test_stocks = ['BBCA', 'BMRI', 'TLKM']

    for stock in test_stocks:
        logger.info(f"\n{'='*60}")
        logger.info(f"Model Comparison for {stock}")
        logger.info(f"{'='*60}\n")

        results = await comparator.compare_models(stock)

        if results is not None:
            print(f"\n{stock} Results:")
            print(results.to_string(index=False))
            print()

            # Save to CSV
            results.to_csv(f'model_comparison_{stock}.csv', index=False)
            logger.info(f"Results saved to model_comparison_{stock}.csv")


if __name__ == "__main__":
    asyncio.run(main())
