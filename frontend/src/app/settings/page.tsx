'use client';

import { useState, useEffect } from 'react';
import { Save, CheckCircle } from 'lucide-react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Alert from '@/components/ui/Alert';
import StockSelector from '@/components/StockSelector';
import { settingsApi } from '@/lib/api';
import type { UserSettings } from '@/types';

export default function SettingsPage() {
  const [settings, setSettings] = useState<UserSettings>({
    default_stock: 'BBCA',
    prediction_days: 5,
    notification_enabled: false,
  });

  const [isSaving, setIsSaving] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const data = await settingsApi.getSettings();
      setSettings(data);
    } catch (error: any) {
      setError(error.message || 'Failed to load settings');
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
