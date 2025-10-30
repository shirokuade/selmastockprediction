// API service layer for backend communication

import axios, { AxiosError } from 'axios';
import type {
  StockInfo,
  PredictionResult,
  UserSettings,
  AvailableStock,
  ApiError,
} from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Error handler
const handleApiError = (error: unknown): never => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiError>;
    const message = axiosError.response?.data?.detail || axiosError.message;
    throw new Error(message);
  }
  throw error;
};

// Stock API
export const stockApi = {
  // Get available stocks
  getAvailableStocks: async (): Promise<AvailableStock[]> => {
    try {
      const response = await api.get<{ stocks: AvailableStock[]; total: number }>(
        '/api/stock/available'
      );
      return response.data.stocks;
    } catch (error) {
      handleApiError(error);
    }
  },

  // Get stock information
  getStockInfo: async (symbol: string): Promise<StockInfo> => {
    try {
      const response = await api.post<StockInfo>('/api/stock/info', { symbol });
      return response.data;
    } catch (error) {
      handleApiError(error);
    }
  },

  // Get stock history
  getStockHistory: async (symbol: string, days: number = 365) => {
    try {
      const response = await api.post(`/api/stock/history?days=${days}`, { symbol });
      return response.data;
    } catch (error) {
      handleApiError(error);
    }
  },

  // Validate stock symbol
  validateSymbol: async (symbol: string): Promise<boolean> => {
    try {
      const response = await api.get(`/api/stock/validate/${symbol}`);
      return response.data.is_valid;
    } catch (error) {
      return false;
    }
  },
};

// Prediction API
export const predictionApi = {
  // Get prediction
  predict: async (symbol: string, days: number = 5): Promise<PredictionResult> => {
    try {
      const response = await api.post<PredictionResult>('/api/prediction/predict', {
        symbol,
        days,
      });
      return response.data;
    } catch (error) {
      handleApiError(error);
    }
  },

  // Train model
  trainModel: async (symbol: string): Promise<void> => {
    try {
      await api.post(`/api/prediction/train?symbol=${symbol}`);
    } catch (error) {
      handleApiError(error);
    }
  },

  // Get model status
  getModelStatus: async (symbol: string) => {
    try {
      const response = await api.get(`/api/prediction/model-status/${symbol}`);
      return response.data;
    } catch (error) {
      handleApiError(error);
    }
  },
};

// Settings API
export const settingsApi = {
  // Save settings
  saveSettings: async (settings: UserSettings): Promise<void> => {
    try {
      await api.post('/api/settings/save', settings);
    } catch (error) {
      handleApiError(error);
    }
  },

  // Get settings
  getSettings: async (): Promise<UserSettings> => {
    try {
      const response = await api.get<{ settings: UserSettings }>('/api/settings/get');
      return response.data.settings;
    } catch (error) {
      // Return default settings if not found
      return {
        default_stock: process.env.NEXT_PUBLIC_DEFAULT_STOCK || 'BBCA',
        prediction_days: 5,
        notification_enabled: false,
      };
    }
  },

  // Update settings
  updateSettings: async (settings: UserSettings): Promise<void> => {
    try {
      await api.put('/api/settings/update', settings);
    } catch (error) {
      handleApiError(error);
    }
  },
};

// Health check
export const healthCheck = async (): Promise<boolean> => {
  try {
    const response = await api.get('/health');
    return response.data.status === 'healthy';
  } catch (error) {
    return false;
  }
};

export default api;
