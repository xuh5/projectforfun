'use client';

import { useEffect, useRef } from 'react';
import { createChart, IChartApi, ISeriesApi, LineSeries } from 'lightweight-charts';

interface ChartDataPoint {
  time: string; // Format: 'YYYY-MM-DD'
  value: number;
}

interface StockChartProps {
  data: ChartDataPoint[];
  height?: number;
}

export function StockChart({ data, height = 400 }: StockChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<'Line'> | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current || !data || data.length === 0) return;

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: height,
      layout: {
        background: { color: 'transparent' },
        textColor: '#64748b',
      },
      grid: {
        vertLines: { color: '#f1f5f9' },
        horzLines: { color: '#f1f5f9' },
      },
      crosshair: {
        mode: 1, // Normal crosshair mode (shows crosshair on hover)
      },
      rightPriceScale: {
        borderColor: '#e2e8f0',
      },
      timeScale: {
        borderColor: '#e2e8f0',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    // Add line series
    const lineSeries = chart.addSeries(LineSeries, {
      color: '#6366f1',
      lineWidth: 2,
      priceLineVisible: false,
      lastValueVisible: true,
    });

    // Set data
    lineSeries.setData(data);

    // Set visible range to show all data from start to end
    if (data.length > 0) {
      chart.timeScale().setVisibleRange({
        from: data[0].time as any,
        to: data[data.length - 1].time as any,
      });
    }

    // Store references
    chartRef.current = chart;
    seriesRef.current = lineSeries;

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
        seriesRef.current = null;
      }
    };
  }, [data, height]);

  if (!data || data.length === 0) {
    return (
      <div className="stock-chart-empty">
        <p>No chart data available.</p>
      </div>
    );
  }

  return <div ref={chartContainerRef} style={{ width: '100%', height: `${height}px` }} />;
}

