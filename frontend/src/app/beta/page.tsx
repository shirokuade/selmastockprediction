'use client';

import { useState } from 'react';
import { TrendingUp, Brain, Newspaper, BarChart3, AlertCircle, Sparkles } from 'lucide-react';
import axios from 'axios';

const API_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

// Popular Indonesian stocks for quick selection
const POPULAR_STOCKS = [
  { symbol: 'BBCA', name: 'Bank Central Asia' },
  { symbol: 'BMRI', name: 'Bank Mandiri' },
  { symbol: 'BBRI', name: 'Bank Rakyat Indonesia' },
  { symbol: 'TLKM', name: 'Telkom Indonesia' },
  { symbol: 'ASII', name: 'Astra International' },
  { symbol: 'UNVR', name: 'Unilever Indonesia' },
  { symbol: 'ICBP', name: 'Indofood CBP' },
  { symbol: 'GGRM', name: 'Gudang Garam' },
];

export default function BetaPage() {
  const [stock1, setStock1] = useState('BBCA');
  const [stock2, setStock2] = useState('BMRI');
  const [weeks, setWeeks] = useState(4);
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    try {
      setAnalyzing(true);
      setError(null);
      setResults(null);

      const response = await axios.post(`${API_URL}/api/beta/analyze`, {
        stocks: [stock1, stock2],
        weeks: weeks
      });

      setResults(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Sparkles className="h-8 w-8 text-purple-600" />
            <h1 className="text-3xl font-bold text-gray-900">Beta AI Engine</h1>
            <span className="px-3 py-1 bg-purple-100 text-purple-700 text-xs font-semibold rounded-full">
              EXPERIMENTAL
            </span>
          </div>
          <p className="text-gray-600">
            Advanced prediction system combining technical analysis + sentiment analysis from news & social media
          </p>
        </div>

        {/* Architecture Info Banner */}
        <div className="mb-8 p-6 bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-purple-200 rounded-xl">
          <h3 className="text-lg font-bold text-purple-900 mb-3">🚀 Next-Generation Prediction Architecture</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-start gap-2">
              <BarChart3 className="h-5 w-5 text-purple-600 mt-1" />
              <div>
                <p className="font-semibold text-purple-900 text-sm">Technical Analysis</p>
                <p className="text-xs text-purple-700">30+ indicators, multi-timeframe analysis</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <Newspaper className="h-5 w-5 text-blue-600 mt-1" />
              <div>
                <p className="font-semibold text-blue-900 text-sm">Sentiment Analysis</p>
                <p className="text-xs text-blue-700">News, social media, market sentiment</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <Brain className="h-5 w-5 text-indigo-600 mt-1" />
              <div>
                <p className="font-semibold text-indigo-900 text-sm">Hybrid AI Models</p>
                <p className="text-xs text-indigo-700">TFT + Ensemble + Deep Learning</p>
              </div>
            </div>
          </div>
        </div>

        {/* Input Form */}
        <div className="bg-white rounded-xl shadow-lg border-2 border-gray-200 p-8 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Select 2 Stocks for Deep Analysis</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Stock 1 */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Stock 1
              </label>
              <select
                value={stock1}
                onChange={(e) => setStock1(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 font-mono"
              >
                {POPULAR_STOCKS.map((stock) => (
                  <option key={stock.symbol} value={stock.symbol}>
                    {stock.symbol} - {stock.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Stock 2 */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Stock 2
              </label>
              <select
                value={stock2}
                onChange={(e) => setStock2(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 font-mono"
              >
                {POPULAR_STOCKS.map((stock) => (
                  <option key={stock.symbol} value={stock.symbol}>
                    {stock.symbol} - {stock.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Weeks */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Analysis Period (Weeks)
              </label>
              <input
                type="number"
                min="1"
                max="12"
                value={weeks}
                onChange={(e) => setWeeks(parseInt(e.target.value) || 1)}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              />
            </div>
          </div>

          {/* Analyze Button */}
          <div className="mt-6">
            <button
              onClick={handleAnalyze}
              disabled={analyzing || stock1 === stock2}
              className="w-full px-6 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all flex items-center justify-center gap-3 font-semibold text-lg shadow-lg disabled:opacity-50"
            >
              {analyzing ? (
                <>
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                  Analyzing with AI...
                </>
              ) : (
                <>
                  <Brain className="h-6 w-6" />
                  Run Advanced Analysis
                </>
              )}
            </button>
            {stock1 === stock2 && (
              <p className="text-red-600 text-sm mt-2 text-center">
                Please select two different stocks
              </p>
            )}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-8 p-4 bg-red-50 border-2 border-red-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
            <div>
              <p className="font-semibold text-red-900">Analysis Error</p>
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="space-y-6">
            {results.stocks?.map((stockResult: any, idx: number) => (
              <div key={idx} className="bg-white rounded-xl shadow-lg border-2 border-gray-200 p-8">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">{stockResult.symbol}</h3>
                    <p className="text-gray-600">{stockResult.name}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Current Price</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {new Intl.NumberFormat('id-ID', {
                        style: 'currency',
                        currency: 'IDR',
                        minimumFractionDigits: 0
                      }).format(stockResult.current_price)}
                    </p>
                  </div>
                </div>

                {/* Prediction */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <p className="text-sm text-blue-600 font-semibold mb-1">Technical Score</p>
                    <p className="text-2xl font-bold text-blue-900">
                      {stockResult.technical_score?.toFixed(1)}%
                    </p>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-lg">
                    <p className="text-sm text-purple-600 font-semibold mb-1">Sentiment Score</p>
                    <p className="text-2xl font-bold text-purple-900">
                      {stockResult.sentiment_score?.toFixed(1)}%
                    </p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg">
                    <p className="text-sm text-green-600 font-semibold mb-1">Combined Prediction</p>
                    <p className="text-2xl font-bold text-green-900">
                      {stockResult.predicted_change >= 0 ? '+' : ''}
                      {stockResult.predicted_change?.toFixed(2)}%
                    </p>
                  </div>
                </div>

                {/* Signal */}
                <div className="mb-6">
                  <div className={`inline-flex items-center gap-2 px-6 py-3 rounded-full font-bold text-lg ${
                    stockResult.signal === 'STRONG BUY' ? 'bg-green-100 text-green-800' :
                    stockResult.signal === 'BUY' ? 'bg-blue-100 text-blue-800' :
                    stockResult.signal === 'HOLD' ? 'bg-yellow-100 text-yellow-800' :
                    stockResult.signal === 'SELL' ? 'bg-orange-100 text-orange-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    <TrendingUp className="h-5 w-5" />
                    {stockResult.signal}
                  </div>
                  <p className="text-gray-600 mt-2">
                    Confidence: {stockResult.confidence?.toFixed(1)}%
                  </p>
                </div>

                {/* Key Insights */}
                {stockResult.insights && stockResult.insights.length > 0 && (
                  <div>
                    <h4 className="font-bold text-gray-900 mb-3">🔍 Key Insights</h4>
                    <ul className="space-y-2">
                      {stockResult.insights.map((insight: string, i: number) => (
                        <li key={i} className="text-gray-700 text-sm flex items-start gap-2">
                          <span className="text-purple-600 mt-1">•</span>
                          <span>{insight}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}

            {/* Comparative Analysis */}
            {results.comparison && (
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl shadow-lg border-2 border-purple-200 p-8">
                <h3 className="text-xl font-bold text-purple-900 mb-4">📊 Comparative Analysis</h3>
                <p className="text-gray-700">{results.comparison}</p>
              </div>
            )}
          </div>
        )}

        {/* Feature Explanation */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200">
            <h3 className="font-bold text-gray-900 mb-3">🎯 What Makes Beta Different?</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>• <strong>Deep focus</strong>: Analyzes only 2 stocks for maximum depth</li>
              <li>• <strong>Sentiment integration</strong>: News, social media, market mood</li>
              <li>• <strong>Temporal Fusion</strong>: Advanced time-series transformer</li>
              <li>• <strong>Multi-factor</strong>: Technical + Fundamental + Sentiment</li>
              <li>• <strong>Explainable AI</strong>: Shows which factors drove the prediction</li>
            </ul>
          </div>

          <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200">
            <h3 className="font-bold text-gray-900 mb-3">⚠️ Beta Disclaimer</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>• This is an <strong>experimental</strong> research engine</li>
              <li>• Predictions are <strong>not financial advice</strong></li>
              <li>• Always do your own due diligence</li>
              <li>• Past performance ≠ future results</li>
              <li>• Use for research and learning purposes</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
