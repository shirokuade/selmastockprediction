'use client';

import { useState, useEffect } from 'react';
import { portfolioApi, stockApi } from '@/lib/api';
import type { PortfolioResponse, AvailableStock } from '@/types';

export default function PortfolioPage() {
  const [portfolio, setPortfolio] = useState<PortfolioResponse | null>(null);
  const [availableStocks, setAvailableStocks] = useState<AvailableStock[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [addingStock, setAddingStock] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    symbol: '',
    shares: '',
    purchase_price: '',
    purchase_date: new Date().toISOString().split('T')[0]
  });

  // Load portfolio and available stocks
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [portfolioData, stocks] = await Promise.all([
        portfolioApi.getPortfolio().catch(() => ({
          stocks: [],
          total_investment: 0,
          current_value: 0,
          total_gain_loss: 0,
          total_gain_loss_percent: 0,
          last_updated: new Date().toISOString()
        })),
        stockApi.getAvailableStocks()
      ]);

      setPortfolio(portfolioData);
      setAvailableStocks(stocks);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleAddStock = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      await portfolioApi.addStock({
        symbol: formData.symbol,
        shares: parseInt(formData.shares),
        purchase_price: parseFloat(formData.purchase_price),
        purchase_date: formData.purchase_date
      });

      // Reset form
      setFormData({
        symbol: '',
        shares: '',
        purchase_price: '',
        purchase_date: new Date().toISOString().split('T')[0]
      });

      setAddingStock(false);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add stock');
    }
  };

  const handleRemoveStock = async (symbol: string) => {
    if (!confirm(`Are you sure you want to remove ${symbol} from your portfolio?`)) {
      return;
    }

    try {
      setError(null);
      await portfolioApi.removeStock(symbol);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove stock');
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

  if (loading) {
    return (
      <div className="p-8">
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Portfolio Tracker</h1>
            <p className="text-gray-600 mt-2">
              Track your stock investments with real-time market values
            </p>
          </div>
          <button
            onClick={() => setAddingStock(!addingStock)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            {addingStock ? 'Cancel' : '+ Add Stock'}
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Add Stock Form */}
        {addingStock && (
          <div className="mb-8 p-6 bg-white rounded-lg shadow-md border border-gray-200">
            <h2 className="text-xl font-semibold mb-4">Add Stock to Portfolio</h2>
            <form onSubmit={handleAddStock} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stock Symbol
                </label>
                <select
                  value={formData.symbol}
                  onChange={(e) => setFormData({ ...formData, symbol: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="">Select stock...</option>
                  {availableStocks.map((stock) => (
                    <option key={stock.symbol} value={stock.symbol}>
                      {stock.symbol} - {stock.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Shares
                </label>
                <input
                  type="number"
                  value={formData.shares}
                  onChange={(e) => setFormData({ ...formData, shares: e.target.value })}
                  min="1"
                  step="1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="100"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Purchase Price (IDR)
                </label>
                <input
                  type="number"
                  value={formData.purchase_price}
                  onChange={(e) => setFormData({ ...formData, purchase_price: e.target.value })}
                  min="0"
                  step="0.01"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="10000"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Purchase Date
                </label>
                <input
                  type="date"
                  value={formData.purchase_date}
                  onChange={(e) => setFormData({ ...formData, purchase_date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              <div className="md:col-span-2 lg:col-span-4">
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Add to Portfolio
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Portfolio Summary */}
        {portfolio && portfolio.stocks.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200">
              <div className="text-sm text-gray-600 mb-1">Total Investment</div>
              <div className="text-2xl font-bold text-gray-900">
                {formatCurrency(portfolio.total_investment)}
              </div>
            </div>

            <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200">
              <div className="text-sm text-gray-600 mb-1">Current Value</div>
              <div className="text-2xl font-bold text-gray-900">
                {formatCurrency(portfolio.current_value)}
              </div>
            </div>

            <div className={`p-6 bg-white rounded-lg shadow-md border border-gray-200`}>
              <div className="text-sm text-gray-600 mb-1">Total Gain/Loss</div>
              <div className={`text-2xl font-bold ${portfolio.total_gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(portfolio.total_gain_loss)}
              </div>
            </div>

            <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200">
              <div className="text-sm text-gray-600 mb-1">Return</div>
              <div className={`text-2xl font-bold ${portfolio.total_gain_loss_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatPercent(portfolio.total_gain_loss_percent)}
              </div>
            </div>
          </div>
        )}

        {/* Portfolio Holdings */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold">Your Holdings</h2>
          </div>

          {!portfolio || portfolio.stocks.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <svg className="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-lg font-medium">No stocks in portfolio</p>
              <p className="text-sm mt-2">Add your first stock to start tracking your investments</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Shares</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Purchase Price</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current Price</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current Value</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Gain/Loss</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Return</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {portfolio.stocks.map((stock: any) => (
                    <tr key={stock.symbol} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="font-medium text-gray-900">{stock.symbol}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {stock.shares}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(stock.purchase_price)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(stock.current_price || 0)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {formatCurrency(stock.current_value || 0)}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${(stock.gain_loss || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(stock.gain_loss || 0)}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${(stock.gain_loss_percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatPercent(stock.gain_loss_percent || 0)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <button
                          onClick={() => handleRemoveStock(stock.symbol)}
                          className="text-red-600 hover:text-red-800 font-medium"
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {portfolio && portfolio.stocks.length > 0 && (
          <div className="mt-4 text-sm text-gray-500 text-right">
            Last updated: {new Date(portfolio.last_updated).toLocaleString('id-ID')}
          </div>
        )}
      </div>
    </div>
  );
}
