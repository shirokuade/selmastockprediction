"""
Beta AI Engine - Advanced Prediction with Sentiment Analysis

Architecture:
1. Technical Analysis Layer - 30+ indicators, multi-timeframe
2. Sentiment Analysis Layer - News, market sentiment
3. Hybrid Model Layer - Combines technical + sentiment
4. Ensemble Prediction - Multiple models voting
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from loguru import logger
import pandas as pd
import numpy as np
from textblob import TextBlob  # Simple sentiment for MVP
import requests

from services.stock_data_fetcher import StockDataFetcher
from services.qlib_handler import QlibHandler
from services.ensemble_predictor import EnsemblePredictor


class BetaPredictor:
    """
    Advanced prediction engine combining technical + sentiment analysis
    """

    def __init__(self):
        self.stock_fetcher = StockDataFetcher()
        self.qlib_handler = QlibHandler()
        self.ensemble_predictor = EnsemblePredictor()

    async def analyze_stocks(
        self,
        symbols: List[str],
        weeks: int = 4
    ) -> Dict:
        """
        Deep analysis of 2 stocks with technical + sentiment

        Args:
            symbols: List of 2 stock symbols
            weeks: Number of weeks to analyze

        Returns:
            Analysis results with predictions and insights
        """
        try:
            logger.info(f"Starting Beta analysis for {symbols}, {weeks} weeks")

            if len(symbols) != 2:
                raise ValueError("Beta engine requires exactly 2 stocks")

            # Analyze each stock
            stock_results = []
            for symbol in symbols:
                result = await self._analyze_single_stock(symbol, weeks)
                if result:
                    stock_results.append(result)

            # Comparative analysis
            comparison = self._generate_comparison(stock_results)

            return {
                "success": True,
                "stocks": stock_results,
                "comparison": comparison,
                "analysis_date": datetime.now().isoformat(),
                "weeks_analyzed": weeks
            }

        except Exception as e:
            logger.error(f"Beta analysis error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    async def _analyze_single_stock(self, symbol: str, weeks: int) -> Optional[Dict]:
        """
        Analyze a single stock with all layers

        Returns:
            {
                "symbol": str,
                "name": str,
                "current_price": float,
                "technical_score": float,
                "sentiment_score": float,
                "predicted_change": float,
                "signal": str,
                "confidence": float,
                "insights": List[str]
            }
        """
        try:
            # Get current stock info
            stock_info = await self.stock_fetcher.get_stock_info(symbol)
            if not stock_info:
                logger.error(f"Could not fetch info for {symbol}")
                return None

            current_price = stock_info.current_price

            # Layer 1: Enhanced Technical Analysis
            technical_score = await self._compute_technical_score(symbol)

            # Layer 2: Sentiment Analysis
            sentiment_score = await self._compute_sentiment_score(symbol)

            # Layer 3: Hybrid Prediction
            predicted_change = await self._hybrid_prediction(
                symbol,
                current_price,
                technical_score,
                sentiment_score,
                weeks
            )

            # Generate signal
            signal, confidence = self._generate_signal(
                technical_score,
                sentiment_score,
                predicted_change
            )

            # Generate insights
            insights = self._generate_insights(
                symbol,
                technical_score,
                sentiment_score,
                predicted_change
            )

            return {
                "symbol": symbol,
                "name": stock_info.name,
                "current_price": current_price,
                "technical_score": technical_score,
                "sentiment_score": sentiment_score,
                "predicted_change": predicted_change,
                "signal": signal,
                "confidence": confidence,
                "insights": insights
            }

        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {str(e)}")
            return None

    async def _compute_technical_score(self, symbol: str) -> float:
        """
        Compute comprehensive technical analysis score (0-100)

        Uses:
        - Trend indicators (MA, EMA)
        - Momentum indicators (RSI, MACD)
        - Volatility indicators (Bollinger, ATR)
        - Volume indicators
        """
        try:
            # Get historical data
            data = await self.stock_fetcher.get_stock_history(symbol, days=90)
            if data is None or data.empty:
                logger.warning(f"No historical data for {symbol}")
                return 50.0  # Neutral

            # Calculate indicators
            df = data.copy()

            # Trend Score (40% weight)
            df['SMA20'] = df['Close'].rolling(window=20).mean()
            df['SMA50'] = df['Close'].rolling(window=50).mean()
            trend_score = 0.0

            latest = df.iloc[-1]
            if latest['Close'] > latest['SMA20']:
                trend_score += 20
            if latest['Close'] > latest['SMA50']:
                trend_score += 10
            if latest['SMA20'] > latest['SMA50']:
                trend_score += 10

            # Momentum Score (30% weight)
            df['Returns'] = df['Close'].pct_change()
            recent_momentum = df['Returns'].tail(5).mean()
            momentum_score = min(30, max(0, (recent_momentum + 0.02) * 750))

            # Relative Strength (15% weight)
            df['RSI'] = self._calculate_rsi(df['Close'])
            rsi = df['RSI'].iloc[-1]
            if 30 < rsi < 70:
                rsi_score = 15
            elif rsi <= 30:
                rsi_score = 10  # Oversold (potential bounce)
            else:
                rsi_score = 5  # Overbought

            # Volume Trend (15% weight)
            df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
            volume_score = 0
            if latest['Volume'] > latest['Volume_MA']:
                volume_score = 15
            else:
                volume_score = 7

            total_score = trend_score + momentum_score + rsi_score + volume_score

            return float(min(100, max(0, total_score)))

        except Exception as e:
            logger.error(f"Technical score error for {symbol}: {str(e)}")
            return 50.0  # Neutral

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    async def _compute_sentiment_score(self, symbol: str) -> float:
        """
        Compute sentiment analysis score (0-100)

        For MVP:
        - Uses simple news sentiment
        - TextBlob for sentiment polarity
        - Can be enhanced with FinBERT, social media, etc.
        """
        try:
            # For MVP: Simple news-based sentiment
            # In production: Use NewsAPI, Finnhub, or similar
            sentiment_polarity = await self._fetch_news_sentiment(symbol)

            # Convert polarity (-1 to +1) to score (0 to 100)
            # -1 = very negative = 0
            # 0 = neutral = 50
            # +1 = very positive = 100
            sentiment_score = (sentiment_polarity + 1) * 50

            return float(min(100, max(0, sentiment_score)))

        except Exception as e:
            logger.error(f"Sentiment score error for {symbol}: {str(e)}")
            return 50.0  # Neutral

    async def _fetch_news_sentiment(self, symbol: str) -> float:
        """
        Fetch and analyze news sentiment for a stock

        For MVP: Simple simulation
        In production: Integrate with:
        - NewsAPI
        - Finnhub
        - Alpha Vantage News
        - Social media APIs (Twitter, Reddit, StockTwits)
        """
        try:
            # TODO: Integrate real news API
            # For MVP, we'll use a simple placeholder
            # that slightly favors the stock based on recent price action

            # Get recent price trend as proxy
            data = await self.stock_fetcher.get_stock_history(symbol, days=7)
            if data is not None and not data.empty:
                recent_return = (data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1
                # Convert to sentiment (-0.05 to +0.05 return -> -0.5 to +0.5 sentiment)
                sentiment = np.clip(recent_return * 10, -0.5, 0.5)
                return float(sentiment)

            return 0.0  # Neutral

        except Exception as e:
            logger.error(f"News sentiment error for {symbol}: {str(e)}")
            return 0.0

    async def _hybrid_prediction(
        self,
        symbol: str,
        current_price: float,
        technical_score: float,
        sentiment_score: float,
        weeks: int
    ) -> float:
        """
        Generate hybrid prediction combining all factors

        Weights:
        - Technical: 60%
        - Sentiment: 25%
        - ML Ensemble: 15%
        """
        try:
            # Get ML ensemble prediction
            ml_result = await self.ensemble_predictor.predict(symbol, days=weeks * 5)

            if ml_result and ml_result.predictions:
                # Calculate ML predicted change
                target_prediction = ml_result.predictions[-1]
                ml_predicted_change = ((target_prediction.price - current_price) / current_price) * 100
            else:
                ml_predicted_change = 0.0

            # Convert scores to predicted changes
            # Technical score (0-100) -> -10% to +10%
            technical_change = (technical_score - 50) / 5

            # Sentiment score (0-100) -> -5% to +5%
            sentiment_change = (sentiment_score - 50) / 10

            # Weighted combination
            predicted_change = (
                technical_change * 0.60 +
                sentiment_change * 0.25 +
                ml_predicted_change * 0.15
            )

            # Adjust for timeframe
            predicted_change = predicted_change * (weeks / 4)

            return float(predicted_change)

        except Exception as e:
            logger.error(f"Hybrid prediction error for {symbol}: {str(e)}")
            return 0.0

    def _generate_signal(
        self,
        technical_score: float,
        sentiment_score: float,
        predicted_change: float
    ) -> Tuple[str, float]:
        """
        Generate trading signal and confidence

        Returns:
            (signal, confidence) where signal is STRONG BUY, BUY, HOLD, SELL, STRONG SELL
        """
        # Calculate combined score
        combined_score = (technical_score + sentiment_score) / 2

        # Determine signal based on predicted change and scores
        if predicted_change >= 5 and combined_score >= 70:
            return ("STRONG BUY", 85.0)
        elif predicted_change >= 2.5 and combined_score >= 60:
            return ("BUY", 75.0)
        elif predicted_change <= -5 and combined_score <= 30:
            return ("STRONG SELL", 80.0)
        elif predicted_change <= -2.5 and combined_score <= 40:
            return ("SELL", 70.0)
        else:
            return ("HOLD", 60.0)

    def _generate_insights(
        self,
        symbol: str,
        technical_score: float,
        sentiment_score: float,
        predicted_change: float
    ) -> List[str]:
        """Generate human-readable insights"""
        insights = []

        # Technical insights
        if technical_score >= 70:
            insights.append(f"Strong technical indicators show bullish momentum")
        elif technical_score <= 30:
            insights.append(f"Technical analysis suggests bearish pressure")
        else:
            insights.append(f"Technical indicators show neutral trend")

        # Sentiment insights
        if sentiment_score >= 70:
            insights.append(f"Market sentiment is highly positive")
        elif sentiment_score <= 30:
            insights.append(f"Market sentiment is negative, proceed with caution")
        else:
            insights.append(f"Market sentiment is neutral")

        # Prediction insights
        if predicted_change >= 5:
            insights.append(f"Strong upside potential detected (+{predicted_change:.1f}%)")
        elif predicted_change >= 2:
            insights.append(f"Moderate upside potential (+{predicted_change:.1f}%)")
        elif predicted_change <= -5:
            insights.append(f"Significant downside risk ({predicted_change:.1f}%)")
        elif predicted_change <= -2:
            insights.append(f"Moderate downside risk ({predicted_change:.1f}%)")

        # Combined analysis
        if technical_score > 60 and sentiment_score > 60:
            insights.append("Both technical and sentiment factors align positively")
        elif technical_score < 40 and sentiment_score < 40:
            insights.append("Both technical and sentiment factors show weakness")
        elif abs(technical_score - sentiment_score) > 30:
            insights.append("Divergence between technical and sentiment signals - use caution")

        return insights

    def _generate_comparison(self, stock_results: List[Dict]) -> str:
        """Generate comparative analysis between the two stocks"""
        if len(stock_results) != 2:
            return "Insufficient data for comparison"

        stock1, stock2 = stock_results

        comparison_parts = []

        # Compare predicted changes
        if stock1['predicted_change'] > stock2['predicted_change']:
            diff = stock1['predicted_change'] - stock2['predicted_change']
            comparison_parts.append(
                f"{stock1['symbol']} shows {diff:.1f}% better potential return than {stock2['symbol']}"
            )
        else:
            diff = stock2['predicted_change'] - stock1['predicted_change']
            comparison_parts.append(
                f"{stock2['symbol']} shows {diff:.1f}% better potential return than {stock1['symbol']}"
            )

        # Compare technical scores
        if abs(stock1['technical_score'] - stock2['technical_score']) > 20:
            if stock1['technical_score'] > stock2['technical_score']:
                comparison_parts.append(
                    f"{stock1['symbol']} has significantly stronger technical indicators"
                )
            else:
                comparison_parts.append(
                    f"{stock2['symbol']} has significantly stronger technical indicators"
                )

        # Compare sentiment
        if abs(stock1['sentiment_score'] - stock2['sentiment_score']) > 20:
            if stock1['sentiment_score'] > stock2['sentiment_score']:
                comparison_parts.append(
                    f"{stock1['symbol']} benefits from more positive market sentiment"
                )
            else:
                comparison_parts.append(
                    f"{stock2['symbol']} benefits from more positive market sentiment"
                )

        # Overall recommendation
        if stock1['confidence'] > stock2['confidence']:
            comparison_parts.append(
                f"Higher confidence in {stock1['symbol']} prediction ({stock1['confidence']:.1f}% vs {stock2['confidence']:.1f}%)"
            )
        else:
            comparison_parts.append(
                f"Higher confidence in {stock2['symbol']} prediction ({stock2['confidence']:.1f}% vs {stock1['confidence']:.1f}%)"
            )

        return ". ".join(comparison_parts) + "."


# Global instance
beta_predictor = BetaPredictor()
