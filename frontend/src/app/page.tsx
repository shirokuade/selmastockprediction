'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus, AlertCircle, RefreshCw, Target, CheckCircle, XCircle } from 'lucide-react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Loading from '@/components/ui/Loading';
import Alert from '@/components/ui/Alert';
import StockSelector from '@/components/StockSelector';
import PredictionChart from '@/components/PredictionChart';
import { stockApi, predictionApi, settingsApi } from '@/lib/api';
import { formatCurrency, formatPercentage, formatDateTime, getTrendColor } from '@/lib/utils';
import type { StockInfo, PredictionResult } from '@/types';

export default function HomePage() {
  const [selectedStock, setSelectedStock] = useState<string>('');
  const [stockInfo, setStockInfo] = useState<StockInfo | null>(null);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [predictionDays, setPredictionDays] = useState<number>(5);
  const [isLoadingStock, setIsLoadingStock] = useState(false);
  const [isLoadingPrediction, setIsLoadingPrediction] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load user settings on mount
  useEffect(() => {
    loadSettings();
  }, []);

  // Load stock info and prediction when stock changes
  useEffect(() => {
    if (selectedStock) {
      loadStockData();
    }
  }, [selectedStock]);

  const loadSettings = async () => {
    try {
      const settings = await settingsApi.getSettings();
      setSelectedStock(settings.default_stock);
      setPredictionDays(settings.prediction_days);
    } catch (error) {
      console.error('Failed to load settings:', error);
      setSelectedStock('BBCA'); // Default fallback
    }
  };

  const loadStockData = async () => {
    if (!selectedStock) return;

    setError(null);
    setIsLoadingStock(true);

    try {
      const info = await stockApi.getStockInfo(selectedStock);
      setStockInfo(info);
    } catch (error: any) {
      setError(error.message || 'Failed to load stock information');
      setStockInfo(null);
    } finally {
      setIsLoadingStock(false);
    }
  };

  const loadPrediction = async () => {
    if (!selectedStock) return;

    setError(null);
    setIsLoadingPrediction(true);

    try {
      const result = await predictionApi.predict(selectedStock, predictionDays);
      setPrediction(result);
    } catch (error: any) {
      const message = error.message || 'Failed to generate prediction';

      // Check if it's a "no model" error
      if (message.includes('train') || message.includes('model')) {
        setError(
          `Model not trained yet for ${selectedStock}. Please train the model first from the backend or wait for automatic training.`
        );
      } else {
        setError(message);
      }

      setPrediction(null);
    } finally {
      setIsLoadingPrediction(false);
    }
  };

  const handleStockChange = (symbol: string) => {
    setSelectedStock(symbol);
    setPrediction(null); // Reset prediction when stock changes
  };

  const getTrendIcon = () => {
    if (!prediction) return null;

    switch (prediction.trend) {
      case 'up':
        return <TrendingUp className="h-6 w-6 text-success" />;
      case 'down':
        return <TrendingDown className="h-6 w-6 text-danger" />;
      case 'stable':
        return <Minus className="h-6 w-6 text-gray-500" />;
    }
  };

  const getSignalConfig = (signal: string) => {
    switch (signal) {
      case 'STRONG_BUY':
        return {
          color: 'bg-green-600',
          textColor: 'text-white',
          borderColor: 'border-green-600',
          icon: <TrendingUp className="h-12 w-12" />,
          label: 'STRONG BUY',
          description: 'Highly recommended to buy this stock',
          bgGradient: 'from-green-500 to-green-700'
        };
      case 'BUY':
        return {
          color: 'bg-green-500',
          textColor: 'text-white',
          borderColor: 'border-green-500',
          icon: <CheckCircle className="h-12 w-12" />,
          label: 'BUY',
          description: 'Good opportunity to buy',
          bgGradient: 'from-green-400 to-green-600'
        };
      case 'HOLD':
        return {
          color: 'bg-blue-500',
          textColor: 'text-white',
          borderColor: 'border-blue-500',
          icon: <Target className="h-12 w-12" />,
          label: 'HOLD',
          description: 'Maintain current position',
          bgGradient: 'from-blue-400 to-blue-600'
        };
      case 'SELL':
        return {
          color: 'bg-orange-500',
          textColor: 'text-white',
          borderColor: 'border-orange-500',
          icon: <AlertCircle className="h-12 w-12" />,
          label: 'SELL',
          description: 'Consider selling',
          bgGradient: 'from-orange-400 to-orange-600'
        };
      case 'STRONG_SELL':
        return {
          color: 'bg-red-600',
          textColor: 'text-white',
          borderColor: 'border-red-600',
          icon: <XCircle className="h-12 w-12" />,
          label: 'STRONG SELL',
          description: 'Strongly recommended to sell',
          bgGradient: 'from-red-500 to-red-700'
        };
      default:
        return {
          color: 'bg-gray-500',
          textColor: 'text-white',
          borderColor: 'border-gray-500',
          icon: <Minus className="h-12 w-12" />,
          label: 'UNKNOWN',
          description: 'No clear signal',
          bgGradient: 'from-gray-400 to-gray-600'
        };
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Stock Prediction Dashboard</h2>
          <p className="text-gray-600 mt-1">
            Select an Indonesian stock to view predictions and analysis
          </p>
        </div>
      </div>

      {/* Stock Selector */}
      <Card>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Stock
            </label>
            <StockSelector value={selectedStock} onChange={handleStockChange} />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Prediction Days
            </label>
            <select
              value={predictionDays}
              onChange={(e) => setPredictionDays(Number(e.target.value))}
              className="w-full p-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value={3}>3 Days</option>
              <option value={5}>5 Days</option>
              <option value={7}>7 Days</option>
              <option value={10}>10 Days</option>
            </select>
          </div>
        </div>

        {selectedStock && (
          <div className="mt-4">
            <Button onClick={loadPrediction} isLoading={isLoadingPrediction} className="w-full">
              {isLoadingPrediction ? 'Generating Prediction...' : 'Get Prediction'}
            </Button>
          </div>
        )}
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert variant="error">
          <div className="flex items-start justify-between">
            <div>
              <p className="font-semibold">Error</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
            <button onClick={() => setError(null)} className="ml-4 text-red-600 hover:text-red-800">
              ×
            </button>
          </div>
        </Alert>
      )}

      {/* Trading Signal - Prominent Display */}
      {prediction && prediction.signal && (
        <div className={`bg-gradient-to-r ${getSignalConfig(prediction.signal).bgGradient} rounded-xl shadow-2xl overflow-hidden`}>
          <div className="p-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6">
                <div className={`${getSignalConfig(prediction.signal).textColor}`}>
                  {getSignalConfig(prediction.signal).icon}
                </div>
                <div>
                  <h3 className="text-4xl font-bold text-white mb-2">
                    {getSignalConfig(prediction.signal).label}
                  </h3>
                  <p className="text-white text-opacity-90 text-lg">
                    {getSignalConfig(prediction.signal).description}
                  </p>
                  <p className="text-white text-opacity-75 text-sm mt-2">
                    Confidence: {(prediction.confidence * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
              <div className="text-right text-white">
                <p className="text-sm text-white text-opacity-75">Current Price</p>
                <p className="text-3xl font-bold">{formatCurrency(prediction.current_price)}</p>
                <p className="text-sm text-white text-opacity-75 mt-2">
                  {predictionDays}-Day Forecast
                </p>
                <p className="text-2xl font-semibold">
                  {formatCurrency(prediction.predictions[prediction.predictions.length - 1].price)}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Current Stock Info */}
      {isLoadingStock ? (
        <Card>
          <Loading text="Loading stock information..." />
        </Card>
      ) : stockInfo ? (
        <Card title={`${stockInfo.symbol} - ${stockInfo.name || 'Indonesian Stock'}`}>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Current Price</p>
              <p className="text-2xl font-bold text-gray-900">
                {stockInfo.current_price ? formatCurrency(stockInfo.current_price) : 'N/A'}
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-600">Change</p>
              <p
                className={`text-2xl font-bold ${
                  stockInfo.change && stockInfo.change >= 0 ? 'text-success' : 'text-danger'
                }`}
              >
                {stockInfo.change_percent ? formatPercentage(stockInfo.change_percent) : 'N/A'}
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-600">Volume</p>
              <p className="text-2xl font-bold text-gray-900">
                {stockInfo.volume ? stockInfo.volume.toLocaleString() : 'N/A'}
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-600">Last Updated</p>
              <p className="text-sm text-gray-900">
                {stockInfo.last_updated ? formatDateTime(stockInfo.last_updated) : 'N/A'}
              </p>
            </div>
          </div>
        </Card>
      ) : null}

      {/* Prediction Results */}
      {isLoadingPrediction ? (
        <Card>
          <Loading text="Generating AI prediction..." size="lg" />
        </Card>
      ) : prediction ? (
        <>
          {/* Prediction Summary */}
          <Card title="Prediction Summary">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              <div className="flex items-center gap-3">
                {getTrendIcon()}
                <div>
                  <p className="text-sm text-gray-600">Trend</p>
                  <p className={`text-xl font-bold capitalize ${getTrendColor(prediction.trend)}`}>
                    {prediction.trend}
                  </p>
                </div>
              </div>

              <div>
                <p className="text-sm text-gray-600">Predicted Price ({predictionDays} days)</p>
                <p className="text-xl font-bold text-gray-900">
                  {formatCurrency(prediction.predictions[prediction.predictions.length - 1].price)}
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-600">Confidence</p>
                <p className="text-xl font-bold text-primary-600">
                  {(prediction.confidence * 100).toFixed(1)}%
                </p>
              </div>
            </div>

            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">
                Generated at: {formatDateTime(prediction.generated_at)}
              </p>
            </div>
          </Card>

          {/* Prediction Chart */}
          <Card title="Price Forecast">
            <PredictionChart
              predictions={prediction.predictions}
              currentPrice={prediction.current_price}
              symbol={prediction.symbol}
            />
          </Card>

          {/* Detailed Predictions */}
          <Card title="Daily Predictions">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                      Date
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                      Predicted Price
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                      Change from Current
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                      Confidence
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {prediction.predictions.map((pred, index) => {
                    const changePercent =
                      ((pred.price - prediction.current_price) / prediction.current_price) * 100;

                    return (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm text-gray-900">{pred.date}</td>
                        <td className="px-4 py-3 text-sm font-semibold text-gray-900">
                          {formatCurrency(pred.price)}
                        </td>
                        <td
                          className={`px-4 py-3 text-sm font-semibold ${
                            changePercent >= 0 ? 'text-success' : 'text-danger'
                          }`}
                        >
                          {formatPercentage(changePercent)}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {(pred.confidence * 100).toFixed(1)}%
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      ) : selectedStock ? (
        <Card>
          <div className="text-center py-12">
            <AlertCircle className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Prediction Yet</h3>
            <p className="text-gray-600 mb-4">
              Click "Get Prediction" to generate AI-powered forecast for {selectedStock}
            </p>
          </div>
        </Card>
      ) : null}

      {/* Info Section */}
      <Alert variant="info">
        <div>
          <p className="font-semibold mb-1">How it works</p>
          <p className="text-sm">
            Our AI model analyzes historical data, technical indicators, and market trends to
            predict future stock prices. The confidence score indicates how reliable the prediction
            is based on data quality and market stability.
          </p>
        </div>
      </Alert>
    </div>
  );
}
