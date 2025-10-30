// Utility functions

import clsx, { ClassValue } from 'clsx';

// Combine class names
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

// Format currency (Indonesian Rupiah)
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

// Format number with commas
export function formatNumber(value: number): string {
  return new Intl.NumberFormat('id-ID').format(value);
}

// Format percentage
export function formatPercentage(value: number): string {
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
}

// Format date
export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return new Intl.DateTimeFormat('id-ID', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(d);
}

// Format date and time
export function formatDateTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return new Intl.DateTimeFormat('id-ID', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(d);
}

// Get trend color
export function getTrendColor(trend: 'up' | 'down' | 'stable'): string {
  switch (trend) {
    case 'up':
      return 'text-success';
    case 'down':
      return 'text-danger';
    case 'stable':
      return 'text-gray-500';
    default:
      return 'text-gray-500';
  }
}

// Get confidence color based on value
export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return 'text-success';
  if (confidence >= 0.6) return 'text-warning';
  return 'text-danger';
}

// Sleep utility for delays
export const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

// Debounce function
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}
