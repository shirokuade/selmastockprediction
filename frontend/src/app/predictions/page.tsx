'use client';

import { useState, useEffect } from 'react';
import { RefreshCw, TrendingUp, CheckCircle, XCircle, AlertTriangle, Zap, Database } from 'lucide-react';
import axios from 'axios';

const API_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export default function PredictionEnginePage() {
  const [predictions, setPredictions] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'active' | 'historical'>('active');
  const [predicting, setPredicting] = useState(false);
  const [fetchingHistory, setFetchingHistory] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      const endpoint = activeTab === 'active'
        ? `${API_URL}/api/prediction-engine/predictions/active`
        : `${API_URL}/api/prediction-engine/predictions/historical`;

      const [predResponse, statsResponse] = await Promise.all([
        axios.get(endpoint),
        axios.get(`${API_URL}/api/prediction-engine/stats`)
      ]);

      setPredictions(predResponse.data.predictions || []);
      setStats(statsResponse.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load predictions');
    } finally {
      setLoading(false);
    }
  };

  const triggerPredictions = async () => {
    try {
      setPredicting(true);
      setError(null);
      setSuccess(null);

      const response = await axios.post(`${API_URL}/api/prediction-engine/trigger/monday-predictions`);

      setSuccess(response.data.message || 'Predictions generated successfully! Refreshing data...');

      // Wait a moment then reload data
      setTimeout(() => {
        loadData();
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate predictions');
    } finally {
      setPredicting(false);
    }
  };

  const fetchHistoricalData = async () => {
    try {
      setFetchingHistory(true);
      setError(null);
      setSuccess(null);

      const response = await axios.post(`${API_URL}/api/prediction-engine/trigger/fetch-history?days=365`);

      setSuccess(response.data.message + ' - ' + response.data.note);

      // Reload data after a delay
      setTimeout(() => {
        loadData();
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch historical data');
    } finally {
      setFetchingHistory(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const getStatusBadge = (prediction: any) => {
    if (prediction.is_correct === null || prediction.is_correct === undefined) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          <AlertTriangle className="h-3 w-3 mr-1" />
          Pending
        </span>
      );
    }

    if (prediction.is_correct) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          <CheckCircle className="h-3 w-3 mr-1" />
          Correct
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
          <XCircle className="h-3 w-3 mr-1" />
          Incorrect
        </span>
      );
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Prediction Engine</h1>
            <p className="text-gray-600 mt-2">
              Weekly trading signals for top 100 Indonesian stocks
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={loadData}
              disabled={loading || predicting || fetchingHistory}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <button
              onClick={fetchHistoricalData}
              disabled={loading || predicting || fetchingHistory}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              <Database className={`h-4 w-4 ${fetchingHistory ? 'animate-pulse' : ''}`} />
              {fetchingHistory ? 'Fetching...' : 'Fetch History'}
            </button>
            <button
              onClick={triggerPredictions}
              disabled={loading || predicting || fetchingHistory}
              className="px-6 py-2 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-lg hover:from-green-700 hover:to-blue-700 transition-colors flex items-center gap-2 font-semibold disabled:opacity-50 shadow-lg"
            >
              <Zap className={`h-5 w-5 ${predicting ? 'animate-pulse' : ''}`} />
              {predicting ? 'Generating...' : 'Predict!'}
            </button>
          </div>
        </div>

        {/* Success Message */}
        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
            {success}
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Fetching History Status */}
        {fetchingHistory && (
          <div className="mb-6 p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-purple-600"></div>
              <div>
                <p className="text-purple-900 font-semibold">Fetching historical data...</p>
                <p className="text-purple-700 text-sm">This will take 10-15 minutes for 1 year of data for 100 stocks. Please wait.</p>
              </div>
            </div>
          </div>
        )}

        {/* Predicting Status */}
        {predicting && (
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
              <div>
                <p className="text-blue-900 font-semibold">Generating predictions...</p>
                <p className="text-blue-700 text-sm">This will take 5-10 minutes for 100 stocks. Please wait.</p>
              </div>
            </div>
          </div>
        )}

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200">
              <div className="text-sm text-gray-600 mb-1">Active Predictions</div>
              <div className="text-2xl font-bold text-gray-900">{stats.active_predictions}</div>
            </div>

            <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200">
              <div className="text-sm text-gray-600 mb-1">Historical Accuracy</div>
              <div className="text-2xl font-bold text-green-600">{stats.accuracy_percent.toFixed(1)}%</div>
            </div>

            <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200">
              <div className="text-sm text-gray-600 mb-1">Avg Predicted Gain</div>
              <div className="text-2xl font-bold text-blue-600">{formatPercent(stats.average_predicted_gain)}</div>
            </div>

            <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200">
              <div className="text-sm text-gray-600 mb-1">Avg Actual Gain</div>
              <div className={`text-2xl font-bold ${stats.average_actual_gain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatPercent(stats.average_actual_gain)}
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="mb-6 border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('active')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'active'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Active Predictions
            </button>
            <button
              onClick={() => setActiveTab('historical')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'historical'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Historical Results
            </button>
          </nav>
        </div>

        {/* Info Banner */}
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="text-sm font-semibold text-blue-900 mb-1">Trading Strategy</h3>
          <p className="text-sm text-blue-700">
            Buy on <strong>Monday</strong> at opening price. Sell on <strong>Friday</strong> at closing price.
            Only stocks with predicted gain ≥ 2.5% are shown.
          </p>
        </div>

        {/* Predictions Table */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading predictions...</p>
            </div>
          ) : predictions.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <TrendingUp className="h-16 w-16 mx-auto mb-4 text-gray-400" />
              <p className="text-lg font-medium">No predictions available</p>
              <p className="text-sm mt-2">
                {activeTab === 'active'
                  ? 'First, click "Fetch History" to download historical data, then click "Predict!" to generate predictions.'
                  : 'No historical data yet. Predictions will appear here after first week completes.'}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Symbol
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Monday Price
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      LightGBM
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      XGBoost
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Avg Prediction
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Predicted Gain
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actual Price
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actual Gain
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {predictions.map((pred: any, index: number) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="font-mono text-sm font-semibold text-gray-900">{pred.symbol}</div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(pred.monday_price)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(pred.prediction_1)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(pred.prediction_2)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                        {formatCurrency(pred.avg_prediction)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-semibold text-green-600">
                        {formatPercent(pred.predicted_gain_percent)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {pred.actual_friday_price ? formatCurrency(pred.actual_friday_price) : '-'}
                      </td>
                      <td className={`px-4 py-4 whitespace-nowrap text-sm font-semibold ${
                        pred.actual_gain_percent
                          ? pred.actual_gain_percent >= 0
                            ? 'text-green-600'
                            : 'text-red-600'
                          : 'text-gray-400'
                      }`}>
                        {pred.actual_gain_percent !== null ? formatPercent(pred.actual_gain_percent) : '-'}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        {getStatusBadge(pred)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {predictions.length > 0 && (
          <div className="mt-4 text-sm text-gray-500 text-right">
            Showing {predictions.length} predictions sorted by highest gain
          </div>
        )}

        {/* Strategy Info */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-6 bg-gradient-to-r from-green-50 to-green-100 rounded-lg border border-green-200">
            <h3 className="font-semibold text-green-900 mb-2">🤖 Setup & Process</h3>
            <ul className="text-sm text-green-800 space-y-1">
              <li>• <strong>First time:</strong> Click "Fetch History" (10-15 min)</li>
              <li>• <strong>Daily:</strong> Update prices (8 AM WIB)</li>
              <li>• <strong>Monday:</strong> Generate predictions (9 AM WIB)</li>
              <li>• <strong>Daily:</strong> Track actual prices (5 PM WIB)</li>
            </ul>
          </div>

          <div className="p-6 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg border border-blue-200">
            <h3 className="font-semibold text-blue-900 mb-2">📊 Top 2 Algorithms</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• LightGBM (Best performer)</li>
              <li>• XGBoost (2nd best performer)</li>
              <li>• Average of both for final prediction</li>
            </ul>
          </div>

          <div className="p-6 bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg border border-purple-200">
            <h3 className="font-semibold text-purple-900 mb-2">💰 Trading Rules</h3>
            <ul className="text-sm text-purple-800 space-y-1">
              <li>• Min gain threshold: 2.5%</li>
              <li>• Buy Monday open, sell Friday close</li>
              <li>• 100 stocks analyzed weekly</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
