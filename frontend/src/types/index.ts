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
  signal: string; // STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL
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

export interface PortfolioStock {
  symbol: string;
  shares: number;
  purchase_price: number;
  purchase_date?: string;
  current_price?: number;
  current_value?: number;
  gain_loss?: number;
  gain_loss_percent?: number;
}

export interface PortfolioResponse {
  stocks: PortfolioStock[];
  total_investment: number;
  current_value: number;
  total_gain_loss: number;
  total_gain_loss_percent: number;
  last_updated: string;
}

export interface ActivityLog {
  timestamp: string;
  activity_type: string;
  symbol?: string;
  message: string;
  details?: any;
}

export interface ActivityLogResponse {
  logs: ActivityLog[];
  total: number;
}
