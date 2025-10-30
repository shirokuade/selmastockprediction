'use client';

import { useState, useEffect } from 'react';
import { Search } from 'lucide-react';
import { stockApi } from '@/lib/api';
import type { AvailableStock } from '@/types';
import { cn } from '@/lib/utils';

interface StockSelectorProps {
  value: string;
  onChange: (symbol: string) => void;
  className?: string;
}

export default function StockSelector({ value, onChange, className }: StockSelectorProps) {
  const [stocks, setStocks] = useState<AvailableStock[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadStocks();
  }, []);

  const loadStocks = async () => {
    try {
      const data = await stockApi.getAvailableStocks();
      setStocks(data);
    } catch (error) {
      console.error('Failed to load stocks:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredStocks = stocks.filter(
    (stock) =>
      stock.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      stock.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const selectedStock = stocks.find((s) => s.symbol === value);

  return (
    <div className={cn('relative', className)}>
      <div
        className="flex items-center gap-2 p-3 border-2 border-gray-300 rounded-lg cursor-pointer hover:border-primary-500 transition-colors"
        onClick={() => setIsOpen(!isOpen)}
      >
        <Search className="h-5 w-5 text-gray-400" />
        <div className="flex-1">
          {selectedStock ? (
            <div>
              <p className="font-semibold">{selectedStock.symbol}</p>
              <p className="text-sm text-gray-600">{selectedStock.name}</p>
            </div>
          ) : (
            <p className="text-gray-500">Select a stock...</p>
          )}
        </div>
      </div>

      {isOpen && (
        <div className="absolute z-10 w-full mt-2 bg-white border border-gray-300 rounded-lg shadow-lg max-h-96 overflow-hidden">
          <div className="p-3 border-b">
            <input
              type="text"
              placeholder="Search stocks..."
              className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onClick={(e) => e.stopPropagation()}
            />
          </div>

          <div className="overflow-y-auto max-h-80">
            {isLoading ? (
              <div className="p-4 text-center text-gray-500">Loading stocks...</div>
            ) : filteredStocks.length === 0 ? (
              <div className="p-4 text-center text-gray-500">No stocks found</div>
            ) : (
              filteredStocks.map((stock) => (
                <div
                  key={stock.symbol}
                  className={cn(
                    'p-3 cursor-pointer hover:bg-primary-50 border-b last:border-b-0 transition-colors',
                    stock.symbol === value && 'bg-primary-100'
                  )}
                  onClick={() => {
                    onChange(stock.symbol);
                    setIsOpen(false);
                    setSearchTerm('');
                  }}
                >
                  <p className="font-semibold">{stock.symbol}</p>
                  <p className="text-sm text-gray-600">{stock.name}</p>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {isOpen && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
}
