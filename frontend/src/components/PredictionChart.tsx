'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { formatCurrency, formatDate } from '@/lib/utils';
import type { PredictionData } from '@/types';

interface PredictionChartProps {
  predictions: PredictionData[];
  currentPrice: number;
  symbol: string;
}

export default function PredictionChart({
  predictions,
  currentPrice,
  symbol,
}: PredictionChartProps) {
  // Prepare chart data with current price as starting point
  const chartData = [
    {
      date: 'Now',
      price: currentPrice,
      confidence: 1,
      isActual: true,
    },
    ...predictions.map((p) => ({
      date: formatDate(p.date),
      price: p.price,
      confidence: p.confidence,
      isActual: false,
    })),
  ];

  const customTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="font-semibold">{data.date}</p>
          <p className="text-primary-600">
            Price: {formatCurrency(data.price)}
          </p>
          {!data.isActual && (
            <p className="text-sm text-gray-600">
              Confidence: {(data.confidence * 100).toFixed(1)}%
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-[400px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="date"
            stroke="#888"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            stroke="#888"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => `Rp ${(value / 1000).toFixed(0)}k`}
          />
          <Tooltip content={customTooltip} />
          <Legend />
          <ReferenceLine
            y={currentPrice}
            stroke="#888"
            strokeDasharray="3 3"
            label={{ value: 'Current', position: 'insideTopRight' }}
          />
          <Line
            type="monotone"
            dataKey="price"
            stroke="#0ea5e9"
            strokeWidth={3}
            dot={{ fill: '#0ea5e9', r: 5 }}
            activeDot={{ r: 7 }}
            name={`${symbol} Price`}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
