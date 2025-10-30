// Type definitions for the application

export interface StockInfo {
  symbol: string;
  name?: string;
  current_price?: number;
  change?: number;
  change_percent?: number;
  volume?: number;
  market_cap?: number;
  last_updated?: string;
}

export interface PredictionData {
  date: string;
  price: number;
  confidence: number;
}

export interface PredictionResult {
  symbol: string;
  current_price: number;
  predictions: PredictionData[];
  trend: 'up' | 'down' | 'stable';
  confidence: number;
  generated_at: string;
}

export interface UserSettings {
  default_stock: string;
  prediction_days: number;
  notification_enabled: boolean;
}

export interface AvailableStock {
  symbol: string;
  name: string;
}

export interface ApiError {
  detail: string;
  message?: string;
}
