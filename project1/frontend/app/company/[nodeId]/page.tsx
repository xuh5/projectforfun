import Link from 'next/link';
import '../company.css';

import { StockSparkline } from '../../../components/company/StockSparkline';
import { fetchNodeDetail, fetchGraphData } from '../../../lib/api';
import { hydrateGraphResponse } from '../../../lib/graph';
import { formatNumber, generateMockSeries } from '../../../lib/stocks';
import type { GraphEdge, GraphNode } from '../../../lib/types';

interface CompanyPageProps {
  params: { nodeId: string };
  searchParams?: { [key: string]: string | string[] | undefined };
}

export default async function CompanyPage({ params, searchParams }: CompanyPageProps) {
  const decodedId = decodeURIComponent(params.nodeId);
  const [companyDetail, rawGraph] = await Promise.all([
    fetchNodeDetail(decodedId),
    fetchGraphData(),
  ]);

  const graphData = rawGraph ? hydrateGraphResponse(rawGraph) : null;
  const graphNodes: GraphNode[] = graphData?.nodes ?? [];
  const graphEdges: GraphEdge[] = graphData?.edges ?? [];
  const graphLoaded = Boolean(graphData);

  const rawLabel = searchParams?.label;
  const labelFromSearch =
    typeof rawLabel === 'string' && rawLabel.trim().length > 0 ? rawLabel.trim() : null;

  const resolvedLabel =
    labelFromSearch ??
    companyDetail?.data?.label ??
    (typeof companyDetail?.data?.name === 'string' ? companyDetail.data.name : null) ??
    decodedId;

  const companyDescription =
    companyDetail?.data?.description && companyDetail.data.description.trim().length > 0
      ? companyDetail.data.description.trim()
      : `Detailed information for ${resolvedLabel} will be expanded as the knowledge graph evolves.`;

  const series = generateMockSeries(resolvedLabel);
  const latestPrice = series.at(-1)?.price ?? 0;
  const startingPrice = series[0]?.price ?? latestPrice;
  const change = latestPrice - startingPrice;
  const changePercent = startingPrice ? (change / startingPrice) * 100 : 0;
  const seriesHigh = Math.max(...series.map((point) => point.price));
  const seriesLow = Math.min(...series.map((point) => point.price));

  const neighborIds = new Set<string>();

  graphEdges.forEach((edge) => {
    if (edge.source === decodedId) {
      neighborIds.add(edge.target);
    }
    if (edge.target === decodedId) {
      neighborIds.add(edge.source);
    }
  });

  const connectedNodes =
    graphNodes
      ?.filter((node) => neighborIds.has(node.id))
      .map((node) => ({
        id: node.id,
        label:
          typeof node.data?.label === 'string' && node.data.label.trim().length > 0
            ? node.data.label
            : node.id,
        description:
          typeof node.data?.description === 'string' && node.data.description.trim().length > 0
            ? node.data.description
            : 'Connected company within the knowledge graph.',
        color: node.color ?? (typeof node.data?.color === 'string' ? node.data.color : '#6366f1'),
      })) ?? [];

  const metadataItems = [
    { label: 'Node ID', value: decodedId },
    { label: 'Sector', value: companyDetail?.data?.sector },
    { label: 'Category', value: companyDetail?.data?.category },
    {
      label: 'In-Network Links',
      value: neighborIds.size ? `${neighborIds.size}` : undefined,
    },
    {
      label: 'Graph Value',
      value:
        typeof companyDetail?.data?.value === 'number'
          ? formatNumber(companyDetail.data.value, { style: 'decimal' })
          : undefined,
    },
  ].filter((item) => item.value && String(item.value).trim().length > 0);

  return (
    <main className="company-page">
      <div className="company-shell">
        <section className="company-hero">
          <div>
            <span className="company-badge">Company profile</span>
            <h1 className="company-title">{resolvedLabel}</h1>
            <p className="company-description">{companyDescription}</p>
          </div>
          <dl className="company-metrics">
            <div>
              <dt>Latest price</dt>
              <dd>${formatNumber(latestPrice, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</dd>
            </div>
            <div>
              <dt>Day change</dt>
              <dd className={change >= 0 ? 'metric-up' : 'metric-down'}>
                {change >= 0 ? '+' : ''}
                {formatNumber(change, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} (
                {change >= 0 ? '+' : ''}
                {formatNumber(changePercent, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%)
              </dd>
            </div>
            <div>
              <dt>52-week range*</dt>
              <dd>
                ${formatNumber(seriesLow, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} – $
                {formatNumber(seriesHigh, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </dd>
            </div>
            <div>
              <dt>Connections</dt>
              <dd>{neighborIds.size || '—'}</dd>
            </div>
          </dl>
        </section>

        <section className="company-content-grid">
          <article className="company-overview">
            <header>
              <h2>Network overview</h2>
              <p>Key attributes captured for this company within the graph.</p>
            </header>
            <dl>
              {metadataItems.length ? (
                metadataItems.map((item) => (
                  <div key={item.label}>
                    <dt>{item.label}</dt>
                    <dd>{item.value}</dd>
                  </div>
                ))
              ) : (
                <div>
                  <dt>Insight</dt>
                  <dd>Metadata for this node will appear as new data is ingested.</dd>
                </div>
              )}
            </dl>
          </article>

          <article className="company-stock">
            <header>
              <div>
                <h2>Stock performance</h2>
                <p>Sparkline generated from recent activity for a quick momentum glimpse.</p>
              </div>
              <span className="stock-label">Simulated data</span>
            </header>
            <StockSparkline series={series} />
            <ul className="stock-metrics">
              <li>
                <span>Open</span>
                <strong>
                  ${formatNumber(startingPrice, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </strong>
              </li>
              <li>
                <span>High</span>
                <strong>
                  ${formatNumber(seriesHigh, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </strong>
              </li>
              <li>
                <span>Low</span>
                <strong>
                  ${formatNumber(seriesLow, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </strong>
              </li>
              <li>
                <span>Volume</span>
                <strong>{formatNumber(Math.round(latestPrice * 120_000))}</strong>
              </li>
            </ul>
          </article>
        </section>

        <section className="company-connections">
          <header>
            <div>
              <h2>Connected companies</h2>
              <p>
                Explore related nodes to understand how {resolvedLabel} is positioned within the knowledge
                graph.
              </p>
            </div>
            <span className="connection-count">
              {neighborIds.size} connection{neighborIds.size === 1 ? '' : 's'}
            </span>
          </header>
          {connectedNodes.length > 0 ? (
            <div className="connected-grid">
              {connectedNodes.map((node) => (
                <Link
                  key={node.id}
                  href={`/company/${encodeURIComponent(node.id)}?label=${encodeURIComponent(node.label)}`}
                  className="connected-card"
                  style={{ borderColor: node.color }}
                >
                  <span className="connected-color" style={{ backgroundColor: node.color }} />
                  <div>
                    <h3>{node.label}</h3>
                    <p>{node.description}</p>
                  </div>
                  <span className="connected-link">View profile →</span>
                </Link>
              ))}
            </div>
          ) : (
            <div className="connections-empty">
              <p>
                {graphLoaded
                  ? `${resolvedLabel} currently has no direct connections recorded.`
                  : 'Connections will appear once the graph data is available.'}
              </p>
            </div>
          )}
        </section>

        <footer className="company-footer">
          <Link href="/" className="company-back-link">
            ← Back to graph
          </Link>
        </footer>
      </div>
    </main>
  );
}

