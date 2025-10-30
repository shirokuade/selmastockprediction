// API service layer for backend communication

import axios, { AxiosError } from 'axios';
import type {
  StockInfo,
  PredictionResult,
  UserSettings,
  AvailableStock,
  ApiError,
  PortfolioStock,
  PortfolioResponse,
  ActivityLogResponse,
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
const handleApiError = (error: unknown): Error => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiError>;
    const message = axiosError.response?.data?.detail || axiosError.message;
    return new Error(message);
  }
  return error instanceof Error ? error : new Error(String(error));
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
      throw handleApiError(error);
    }
  },

  // Get stock information
  getStockInfo: async (symbol: string): Promise<StockInfo> => {
    try {
      const response = await api.post<StockInfo>('/api/stock/info', { symbol });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Get stock history
  getStockHistory: async (symbol: string, days: number = 365) => {
    try {
      const response = await api.post(`/api/stock/history?days=${days}`, { symbol });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
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
      throw handleApiError(error);
    }
  },

  // Train model
  trainModel: async (symbol: string): Promise<void> => {
    try {
      await api.post(`/api/prediction/train?symbol=${symbol}`);
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Get model status
  getModelStatus: async (symbol: string) => {
    try {
      const response = await api.get(`/api/prediction/model-status/${symbol}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
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
      throw handleApiError(error);
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
      throw handleApiError(error);
    }
  },
};

// Portfolio API
export const portfolioApi = {
  // Add stock to portfolio
  addStock: async (stock: {
    symbol: string;
    shares: number;
    purchase_price: number;
    purchase_date?: string;
  }): Promise<void> => {
    try {
      await api.post('/api/portfolio/add', stock);
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Get portfolio
  getPortfolio: async (): Promise<PortfolioResponse> => {
    try {
      const response = await api.get<PortfolioResponse>('/api/portfolio');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Remove stock from portfolio
  removeStock: async (symbol: string): Promise<void> => {
    try {
      await api.delete(`/api/portfolio/${symbol}`);
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Get portfolio stocks list
  getStocksList: async (): Promise<string[]> => {
    try {
      const response = await api.get<{ symbols: string[]; count: number }>(
        '/api/portfolio/stocks/list'
      );
      return response.data.symbols;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

// Activity API
export const activityApi = {
  // Get activity logs
  getLogs: async (params?: {
    limit?: number;
    activity_type?: string;
    symbol?: string;
  }): Promise<ActivityLogResponse> => {
    try {
      const queryParams = new URLSearchParams();
      if (params?.limit) queryParams.append('limit', params.limit.toString());
      if (params?.activity_type) queryParams.append('activity_type', params.activity_type);
      if (params?.symbol) queryParams.append('symbol', params.symbol);

      const response = await api.get<ActivityLogResponse>(
        `/api/activity/logs?${queryParams.toString()}`
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Get activity types
  getTypes: async (): Promise<any[]> => {
    try {
      const response = await api.get('/api/activity/logs/types');
      return response.data.types;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Get activity summary
  getSummary: async (): Promise<any> => {
    try {
      const response = await api.get('/api/activity/logs/summary');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
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
