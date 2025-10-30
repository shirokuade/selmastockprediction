'use client';

import { useState, useEffect } from 'react';
import { Save, CheckCircle, Activity, Clock, AlertCircle, TrendingUp } from 'lucide-react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Alert from '@/components/ui/Alert';
import StockSelector from '@/components/StockSelector';
import { settingsApi, activityApi } from '@/lib/api';
import type { UserSettings, ActivityLog } from '@/types';

export default function SettingsPage() {
  const [settings, setSettings] = useState<UserSettings>({
    default_stock: 'BBCA',
    prediction_days: 5,
    notification_enabled: false,
  });

  const [isSaving, setIsSaving] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([]);
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [activityFilter, setActivityFilter] = useState<string>('all');

  useEffect(() => {
    loadSettings();
    loadActivityLogs();
  }, []);

  useEffect(() => {
    loadActivityLogs();
  }, [activityFilter]);

  const loadSettings = async () => {
    try {
      const data = await settingsApi.getSettings();
      setSettings(data);
    } catch (error: any) {
      setError(error.message || 'Failed to load settings');
    }
  };

  const loadActivityLogs = async () => {
    try {
      setLoadingLogs(true);
      const params = activityFilter !== 'all' ? { activity_type: activityFilter, limit: 50 } : { limit: 50 };
      const response = await activityApi.getLogs(params);
      setActivityLogs(response.logs);
    } catch (error: any) {
      console.error('Failed to load activity logs:', error);
    } finally {
      setLoadingLogs(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setShowSuccess(false);

    try {
      await settingsApi.saveSettings(settings);
      setShowSuccess(true);

      // Hide success message after 3 seconds
      setTimeout(() => {
        setShowSuccess(false);
      }, 3000);
    } catch (error: any) {
      setError(error.message || 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Settings</h2>
        <p className="text-gray-600 mt-1">Customize your stock prediction preferences</p>
      </div>

      {/* Success Alert */}
      {showSuccess && (
        <Alert variant="success">
          <div className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            <p className="font-semibold">Settings saved successfully!</p>
          </div>
        </Alert>
      )}

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

      {/* Stock Preferences */}
      <Card title="Stock Preferences">
        <div className="space-y-6">
          {/* Default Stock */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Default Stock
              <span className="text-gray-500 font-normal ml-2">
                (This stock will be selected by default on the dashboard)
              </span>
            </label>
            <StockSelector
              value={settings.default_stock}
              onChange={(symbol) => setSettings({ ...settings, default_stock: symbol })}
            />
          </div>

          {/* Prediction Days */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Default Prediction Days
            </label>
            <select
              value={settings.prediction_days}
              onChange={(e) =>
                setSettings({ ...settings, prediction_days: Number(e.target.value) })
              }
              className="w-full p-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value={3}>3 Days</option>
              <option value={5}>5 Days</option>
              <option value={7}>7 Days</option>
              <option value={10}>10 Days</option>
              <option value={14}>14 Days</option>
              <option value={30}>30 Days</option>
            </select>
            <p className="text-sm text-gray-600 mt-2">
              Number of days to predict into the future
            </p>
          </div>
        </div>
      </Card>

      {/* Notification Preferences */}
      <Card title="Notification Preferences">
        <div className="space-y-4">
          <div className="flex items-start gap-3">
            <input
              type="checkbox"
              id="notifications"
              checked={settings.notification_enabled}
              onChange={(e) =>
                setSettings({ ...settings, notification_enabled: e.target.checked })
              }
              className="mt-1 h-5 w-5 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <div className="flex-1">
              <label htmlFor="notifications" className="font-medium text-gray-900 cursor-pointer">
                Enable Notifications
              </label>
              <p className="text-sm text-gray-600 mt-1">
                Receive notifications about significant price changes and prediction updates
                (Feature coming soon)
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Activity Logs */}
      <Card title="Activity Logs">
        <div className="space-y-4">
          {/* Filter */}
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              View system activities, predictions, and training logs
            </p>
            <select
              value={activityFilter}
              onChange={(e) => setActivityFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 text-sm"
            >
              <option value="all">All Activities</option>
              <option value="prediction">Predictions</option>
              <option value="training">Training</option>
              <option value="daily_update">Daily Updates</option>
              <option value="weekly_retrain">Weekly Retraining</option>
              <option value="portfolio_update">Portfolio Changes</option>
              <option value="error">Errors</option>
            </select>
          </div>

          {/* Logs List */}
          <div className="border border-gray-200 rounded-lg divide-y divide-gray-200 max-h-96 overflow-y-auto">
            {loadingLogs ? (
              <div className="p-8 text-center text-gray-500">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
                <p className="mt-2">Loading logs...</p>
              </div>
            ) : activityLogs.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <Activity className="h-12 w-12 mx-auto mb-2 text-gray-400" />
                <p>No activity logs found</p>
              </div>
            ) : (
              activityLogs.map((log, index) => (
                <div key={index} className="p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      {/* Icon based on activity type */}
                      {log.activity_type === 'prediction' && (
                        <TrendingUp className="h-5 w-5 text-blue-500 mt-0.5" />
                      )}
                      {log.activity_type === 'training' && (
                        <Activity className="h-5 w-5 text-purple-500 mt-0.5" />
                      )}
                      {(log.activity_type === 'daily_update' || log.activity_type === 'weekly_retrain') && (
                        <Clock className="h-5 w-5 text-green-500 mt-0.5" />
                      )}
                      {log.activity_type === 'error' && (
                        <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
                      )}
                      {!['prediction', 'training', 'daily_update', 'weekly_retrain', 'error'].includes(log.activity_type) && (
                        <Activity className="h-5 w-5 text-gray-400 mt-0.5" />
                      )}

                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          {log.symbol && (
                            <span className="font-mono text-sm font-semibold text-gray-900">
                              {log.symbol}
                            </span>
                          )}
                          <span className="text-sm text-gray-600">{log.message}</span>
                        </div>
                        {log.details && (
                          <div className="mt-1 text-xs text-gray-500 font-mono bg-gray-50 p-2 rounded">
                            {JSON.stringify(log.details, null, 2).slice(0, 200)}
                            {JSON.stringify(log.details, null, 2).length > 200 && '...'}
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="text-xs text-gray-500 whitespace-nowrap ml-4">
                      {new Date(log.timestamp).toLocaleString('id-ID', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="flex justify-end">
            <Button variant="outline" onClick={loadActivityLogs} size="sm">
              Refresh Logs
            </Button>
          </div>
        </div>
      </Card>

      {/* About */}
      <Card title="About">
        <div className="space-y-3 text-sm text-gray-600">
          <p>
            <strong className="text-gray-900">Selma Stock Prediction</strong> is an AI-powered
            platform for predicting Indonesian stock prices using machine learning and technical
            analysis.
          </p>
          <p>
            Our models analyze historical price data, technical indicators (RSI, MACD, Bollinger
            Bands, Moving Averages), and market trends to generate accurate forecasts.
          </p>
          <p className="text-xs text-gray-500 mt-4">
            <strong>Disclaimer:</strong> This tool is for informational purposes only. Always do
            your own research before making investment decisions.
          </p>
        </div>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end gap-3">
        <Button variant="outline" onClick={loadSettings} disabled={isSaving}>
          Reset
        </Button>
        <Button onClick={handleSave} isLoading={isSaving}>
          <Save className="h-5 w-5 mr-2" />
          Save Settings
        </Button>
      </div>
    </div>
  );
}
