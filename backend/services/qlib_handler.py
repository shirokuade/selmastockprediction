"""
Qlib integration for Indonesian stock prediction
"""
import qlib
from qlib.config import REG_CN
from qlib.contrib.model.gbdt import LGBModel
from qlib.contrib.data.handler import Alpha158
from qlib.contrib.strategy import TopkDropoutStrategy
from qlib.contrib.evaluate import backtest
from qlib.utils import init_instance_by_config
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger
from typing import Optional, Dict, List
import os
import pickle

from config import settings
from services.stock_data_fetcher import StockDataFetcher


class QlibHandler:
    """Handle Qlib operations for stock prediction"""

    def __init__(self):
        self.initialized = False
        self.stock_fetcher = StockDataFetcher()
        self.models = {}  # Cache for trained models
        self._initialize_qlib()

    def _initialize_qlib(self):
        """Initialize Qlib with custom configuration"""
        try:
            # Initialize Qlib
            provider_uri = settings.qlib_data_dir
            qlib.init(
                provider_uri=provider_uri,
                region=REG_CN,  # We'll use CN region as template
                auto_mount=False,
                custom_ops=[],
            )
            self.initialized = True
            logger.info("Qlib initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Qlib: {str(e)}")
            self.initialized = False

    async def prepare_data_for_qlib(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Fetch and prepare stock data in Qlib format

        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame in Qlib format or None
        """
        try:
            # Calculate dates if not provided
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start = datetime.now() - timedelta(days=settings.training_period)
                start_date = start.strftime("%Y-%m-%d")

            logger.info(f"Preparing data for {symbol} from {start_date} to {end_date}")

            # Fetch historical data
            days = (datetime.strptime(end_date, "%Y-%m-%d") -
                   datetime.strptime(start_date, "%Y-%m-%d")).days
            history = await self.stock_fetcher.get_stock_history(symbol, days=days)

            if history is None or history.empty:
                logger.error(f"No data available for {symbol}")
                return None

            # Prepare data in Qlib format
            df = history.copy()
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')

            # Rename columns to Qlib format (lowercase)
            column_mapping = {
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume',
                'Adj Close': 'adj_close'
            }
            df = df.rename(columns=column_mapping)

            # Add required columns
            df['symbol'] = symbol
            df['date'] = df.index

            # Calculate basic features
            df = self._add_technical_indicators(df)

            logger.info(f"Prepared {len(df)} records for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Error preparing data for Qlib: {str(e)}")
            return None

    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators as features

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with added technical indicators
        """
        try:
            # Returns
            df['return'] = df['close'].pct_change()
            df['log_return'] = np.log(df['close'] / df['close'].shift(1))

            # Moving averages
            df['ma5'] = df['close'].rolling(window=5).mean()
            df['ma10'] = df['close'].rolling(window=10).mean()
            df['ma20'] = df['close'].rolling(window=20).mean()
            df['ma60'] = df['close'].rolling(window=60).mean()

            # Volatility
            df['volatility'] = df['return'].rolling(window=20).std()

            # Volume indicators
            df['volume_ma5'] = df['volume'].rolling(window=5).mean()
            df['volume_ma20'] = df['volume'].rolling(window=20).mean()

            # Price momentum
            df['momentum'] = df['close'] - df['close'].shift(5)

            # RSI (Relative Strength Index)
            df['rsi'] = self._calculate_rsi(df['close'])

            # MACD
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = exp1 - exp2
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)

            return df

        except Exception as e:
            logger.error(f"Error adding technical indicators: {str(e)}")
            return df

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate RSI (Relative Strength Index)

        Args:
            prices: Price series
            period: RSI period

        Returns:
            RSI series
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def get_feature_columns(self) -> List[str]:
        """
        Get list of feature columns for model training

        Returns:
            List of feature column names
        """
        return [
            'return', 'log_return',
            'ma5', 'ma10', 'ma20', 'ma60',
            'volatility',
            'volume_ma5', 'volume_ma20',
            'momentum',
            'rsi',
            'macd', 'macd_signal',
            'bb_middle', 'bb_upper', 'bb_lower'
        ]

    async def save_model(self, model, symbol: str) -> bool:
        """
        Save trained model to disk

        Args:
            model: Trained model object
            symbol: Stock symbol

        Returns:
            True if successful
        """
        try:
            model_path = os.path.join(settings.model_dir, f"{symbol}_model.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)

            logger.info(f"Model saved for {symbol} at {model_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False

    async def load_model(self, symbol: str):
        """
        Load trained model from disk

        Args:
            symbol: Stock symbol

        Returns:
            Loaded model or None
        """
        try:
            model_path = os.path.join(settings.model_dir, f"{symbol}_model.pkl")

            if not os.path.exists(model_path):
                logger.warning(f"No saved model found for {symbol}")
                return None

            with open(model_path, 'rb') as f:
                model = pickle.load(f)

            logger.info(f"Model loaded for {symbol}")
            return model

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return None

    def get_model_info(self, symbol: str) -> Dict:
        """
        Get information about saved model

        Args:
            symbol: Stock symbol

        Returns:
            Model information dictionary
        """
        try:
            model_path = os.path.join(settings.model_dir, f"{symbol}_model.pkl")

            if not os.path.exists(model_path):
                return {
                    "exists": False,
                    "symbol": symbol
                }

            # Get file stats
            stats = os.stat(model_path)
            modified_time = datetime.fromtimestamp(stats.st_mtime)

            return {
                "exists": True,
                "symbol": symbol,
                "path": model_path,
                "size_bytes": stats.st_size,
                "last_modified": modified_time.isoformat(),
                "age_days": (datetime.now() - modified_time).days
            }

        except Exception as e:
            logger.error(f"Error getting model info: {str(e)}")
            return {"exists": False, "symbol": symbol, "error": str(e)}
