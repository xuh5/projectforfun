import type { StockPoint } from './types';

export const formatNumber = (value: number | undefined, options?: Intl.NumberFormatOptions): string => {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return '—';
  }

  return new Intl.NumberFormat('en-US', options).format(value);
};

export const generateMockSeries = (seed: string, points = 16): StockPoint[] => {
  const normalizeSeed = Array.from(seed).reduce((acc, char, index) => {
    return acc + char.charCodeAt(0) * (index + 1);
  }, 0);

  let value = 100 + (normalizeSeed % 45);
  const series: StockPoint[] = [];

  for (let i = 0; i < points; i += 1) {
    const drift = Math.sin((normalizeSeed / 13 + i) * 0.45) * 2.6;
    const volatility = ((normalizeSeed % (i + 3)) / (points + 4)) * 4.2;
    value = Math.max(12, value + drift + volatility - 2.1);
    const formatted = new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
    }).format(new Date(Date.now() - (points - i) * 1000 * 60 * 60 * 24));
    series.push({ dateLabel: formatted, price: Number(value.toFixed(2)) });
  }

  return series;
};

