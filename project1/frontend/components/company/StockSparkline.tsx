import type { StockPoint } from '../../lib/types';

interface StockSparklineProps {
  series: StockPoint[];
}

export function StockSparkline({ series }: StockSparklineProps) {
  if (!series.length) {
    return (
      <div className="stock-chart-empty">
        <p>No price data available.</p>
      </div>
    );
  }

  const width = 360;
  const height = 140;
  const prices = series.map((point) => point.price);
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const span = max - min || 1;

  const points = series
    .map((point, index) => {
      const x = (index / (series.length - 1 || 1)) * width;
      const y = height - ((point.price - min) / span) * height;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(' ');

  const areaPoints = `0,${height} ${points} ${width},${height}`;

  return (
    <svg className="stock-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-hidden="true">
      <defs>
        <linearGradient id="stockGradient" x1="0%" x2="0%" y1="0%" y2="100%">
          <stop offset="0%" stopColor="rgba(99, 102, 241, 0.45)" />
          <stop offset="100%" stopColor="rgba(129, 140, 248, 0.05)" />
        </linearGradient>
      </defs>
      <polygon points={areaPoints} fill="url(#stockGradient)" opacity={0.65} />
      <polyline
        points={points}
        fill="none"
        stroke="rgba(99, 102, 241, 0.95)"
        strokeWidth={3}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

