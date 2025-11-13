'use client';

import { ChangeEvent, FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import GraphCanvas, { GraphEdge, GraphNode } from '../components/GraphCanvas';
import {
  forceCenter,
  forceCollide,
  forceLink,
  forceManyBody,
  forceSimulation,
  forceX,
  forceY,
  forceZ
} from 'd3-force-3d';

const DEFAULT_COMPANY_NAMES = [
  'NVIDIA',
  'Tesla',
  'Apple',
  'Microsoft',
  'Amazon',
  'Google',
  'Meta',
  'AMD',
  'Intel',
  'Netflix',
  'Adobe',
  'Salesforce',
  'Samsung',
  'Qualcomm',
  'Spotify',
  'Uber',
  'Airbnb',
  'IBM',
  'Oracle',
  'Stripe',
  'Shopify',
  'ByteDance',
  'Tencent',
  'Alibaba',
  'TSMC',
  'Unity',
  'Roblox',
  'Zoom'
];

const normalizeCartesianPosition = (position: Record<string, unknown>): [number, number, number] | null => {
  if (!position) return null;

  const maybeNumber = (value: unknown): number | null =>
    typeof value === 'number' && Number.isFinite(value) ? value : null;

  const x = maybeNumber((position as { x?: number }).x ?? (position as { left?: number }).left);
  const y = maybeNumber((position as { y?: number }).y ?? (position as { top?: number }).top);
  const z = maybeNumber((position as { z?: number }).z);

  if (x === null && y === null && z === null) {
    return null;
  }

  const scale = 120;
  return [
    (x ?? 0) / scale,
    (y ?? 0) / scale,
    (z ?? 0) / scale,
  ];
};

const createInitialPosition = (fallbackScale: number): [number, number, number] => {
  const range = Math.max(2, fallbackScale);
  return [
    (Math.random() - 0.5) * range,
    (Math.random() - 0.5) * range,
    (Math.random() - 0.5) * range,
  ];
};

type SimulationNode = GraphNode & {
  x?: number;
  y?: number;
  z?: number;
  vx?: number;
  vy?: number;
  vz?: number;
  fx?: number;
  fy?: number;
  fz?: number;
  index?: number;
};

type SimulationLink = {
  source: string;
  target: string;
  strength?: number;
};

const DEFAULT_LINK_STRENGTH = 0.15;

const runForceDirectedLayout = (
  nodes: GraphNode[],
  edges: GraphEdge[],
  iterations = 300
): GraphNode[] => {
  if (!nodes.length || edges.length === 0) {
    return nodes;
  }

  const scale = Math.cbrt(nodes.length) * 6;

  const simulationNodes: SimulationNode[] = nodes.map((node) => {
    const initial = node.position ?? createInitialPosition(scale);
    return {
      ...node,
      x: initial[0],
      y: initial[1],
      z: initial[2],
    };
  });

  const simulationLinks: SimulationLink[] = edges.map((edge) => ({
    source: edge.source,
    target: edge.target,
    strength: typeof edge.strength === 'number' && Number.isFinite(edge.strength)
      ? Math.min(Math.max(edge.strength, 0), 1)
      : undefined,
  }));

  const linkForce = forceLink<SimulationNode, SimulationLink>(simulationLinks)
    .id((node: SimulationNode) => node.id)
    .strength((link: SimulationLink) => link.strength ?? DEFAULT_LINK_STRENGTH)
    .distance(() => 1.8);

  const baseCharge = -12 * Math.cbrt(nodes.length);

  const simulation = forceSimulation<SimulationNode>(simulationNodes)
    .force('link', linkForce)
    .force('charge', forceManyBody().strength(baseCharge))
    .force('center', forceCenter(0, 0, 0))
    .force('collision', forceCollide<SimulationNode>(0.85).strength(0.95))
    .force('x', forceX<SimulationNode>(0).strength(0.02))
    .force('y', forceY<SimulationNode>(0).strength(0.02))
    .force('z', forceZ<SimulationNode>(0).strength(0.02));

  simulation.alpha(1).alphaMin(0.001);
  simulation.stop();

  for (let i = 0; i < iterations; i += 1) {
    simulation.tick();
  }

  return simulationNodes.map((node) => {
    const {
      x = 0,
      y = 0,
      z = 0,
      vx,
      vy,
      vz,
      fx,
      fy,
      fz,
      index,
      position: _position,
      ...rest
    } = node;

    return {
      ...rest,
      position: [x, y, z] as [number, number, number],
    };
  });
};

const createGraphNode = (node: any, index: number, total: number): GraphNode => {
  const positionFromNode = normalizeCartesianPosition(node?.position ?? {});
  const rawData = { ...(node?.data ?? {}) };
  const fallbackName = DEFAULT_COMPANY_NAMES[index % DEFAULT_COMPANY_NAMES.length];

  const labelCandidates = [
    node?.label,
    rawData.label,
    rawData.name,
    node?.name,
  ];

  const resolvedLabel =
    labelCandidates.find((value) => typeof value === 'string' && value.trim().length > 0)?.toString() ??
    fallbackName;

  const description =
    typeof node?.description === 'string'
      ? node.description
      : typeof rawData.description === 'string'
        ? rawData.description
        : `${resolvedLabel} is a key company within the network.`;

  return {
    id: String(node?.id ?? `node-${index}`),
    position: positionFromNode ?? createInitialPosition(total),
    color: typeof node?.color === 'string' ? node.color : (typeof rawData.color === 'string' ? rawData.color : undefined),
    data: {
      ...rawData,
      label: resolvedLabel,
      description,
    },
  };
};

const createGraphEdge = (edge: any, index: number): GraphEdge | null => {
  const source = edge?.source;
  const target = edge?.target;

  if (!source || !target) {
    return null;
  }

  return {
    id: String(edge?.id ?? `edge-${index}`),
    source: String(source),
    target: String(target),
    strength:
      typeof edge?.strength === 'number' && Number.isFinite(edge.strength)
        ? edge.strength
        : undefined,
  };
};

export default function Home() {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [focusNodeId, setFocusNodeId] = useState<string | null>(null);

  useEffect(() => {
    fetchGraphData();
  }, []);

  const fetchGraphData = async () => {
    try {
      const response = await fetch('/api/nodes');
      const data = await response.json();

      const rawNodes: any[] = Array.isArray(data?.nodes) ? data.nodes : [];
      const rawEdges: any[] = Array.isArray(data?.edges) ? data.edges : [];

      if (!rawNodes.length || !rawEdges.length) {
        generateSampleData();
        return;
      }

      const apiNodes: GraphNode[] = rawNodes.map((node, index) => createGraphNode(node, index, rawNodes.length));
      const apiEdges: GraphEdge[] = rawEdges
        .map((edge, index) => createGraphEdge(edge, index))
        .filter((edge): edge is GraphEdge => edge !== null);

      if (!apiNodes.length || !apiEdges.length) {
        generateSampleData();
        return;
      }

      const positionedNodes = runForceDirectedLayout(apiNodes, apiEdges);
      setNodes(positionedNodes);
      setEdges(apiEdges);
    } catch (error) {
      console.error('Error fetching graph data:', error);
      // Fallback to sample data
      generateSampleData();
    } finally {
      setLoading(false);
    }
  };

  const generateSampleData = () => {
    // Generate sample nodes in a circular pattern
    const nodeCount = 18;
    const palette = ['#667eea', '#764ba2', '#f093fb', '#4f46e5', '#22d3ee', '#f472b6'];
    const sectors = ['AI', 'Automotive', 'Consumer', 'Enterprise', 'Cloud', 'Semiconductors'];

    const sampleNodes: GraphNode[] = Array.from({ length: nodeCount }, (_, index) => {
      const color = palette[index % palette.length];
      const companyName = DEFAULT_COMPANY_NAMES[index % DEFAULT_COMPANY_NAMES.length];
      const sector = sectors[index % sectors.length];

      return {
        id: `node-${index + 1}`,
        position: createInitialPosition(nodeCount),
        color,
        data: {
          label: companyName,
          description: `${companyName} is a leading ${sector.toLowerCase()} company in our sample network.`,
          sector,
          marketCap: `${(Math.random() * 900 + 100).toFixed(1)}B`,
          color,
        },
      };
    });

    const sampleEdges: GraphEdge[] = [];

    for (let i = 0; i < nodeCount; i++) {
      const nextIndex = (i + 1) % nodeCount;
      const longIndex = (i + Math.floor(nodeCount / 3)) % nodeCount;

      sampleEdges.push({
        id: `edge-${i}-${nextIndex}`,
        source: sampleNodes[i].id,
        target: sampleNodes[nextIndex].id,
        strength: 0.25,
      });

      if (longIndex !== nextIndex) {
        sampleEdges.push({
          id: `edge-${i}-${longIndex}`,
          source: sampleNodes[i].id,
          target: sampleNodes[longIndex].id,
          strength: 0.1,
        });
      }
    }

    const positionedNodes = runForceDirectedLayout(sampleNodes, sampleEdges, 400);
    setNodes(positionedNodes);
    setEdges(sampleEdges);
  };

  const matchingNodes = useMemo(() => {
    const term = searchQuery.trim().toLowerCase();
    if (!term) return [];

    return nodes
      .filter((node) => {
        const label = typeof node.data?.label === 'string' ? node.data.label : '';
        return label.toLowerCase().includes(term) || node.id.toLowerCase().includes(term);
      })
      .slice(0, 8);
  }, [nodes, searchQuery]);

  const handleSearchChange = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setSearchQuery(value);
    if (value.trim().length === 0) {
      setFocusNodeId(null);
    }
  }, []);

  const handleSearchSubmit = useCallback(
    (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      const trimmed = searchQuery.trim();
      if (!trimmed) return;
      const firstMatch = matchingNodes[0];
      if (firstMatch) {
        const resolvedLabel =
          typeof firstMatch.data?.label === 'string' && firstMatch.data.label.trim().length > 0
            ? firstMatch.data.label
            : firstMatch.id;
        setSearchQuery(resolvedLabel);
        setFocusNodeId(firstMatch.id);
      }
    },
    [matchingNodes, searchQuery]
  );

  useEffect(() => {
    if (focusNodeId && !nodes.some((node) => node.id === focusNodeId)) {
      setFocusNodeId(null);
    }
  }, [focusNodeId, nodes]);

  if (loading) {
    return (
      <div className="page-wrapper">
        <div className="canvas-window">
          <span className="canvas-status">Loading graph…</span>
        </div>
      </div>
    );
  }

  return (
    <div className="page-wrapper">
      <div className="search-container">
        <form className="search-form" onSubmit={handleSearchSubmit}>
          <input
            type="search"
            value={searchQuery}
            onChange={handleSearchChange}
            placeholder="Search companies by name or node ID…"
            aria-label="Search companies"
            autoComplete="off"
          />
          <button type="submit">Search</button>
        </form>

        {searchQuery.trim().length > 0 ? (
          matchingNodes.length > 0 ? (
            <ul className="search-results" role="listbox">
              {matchingNodes.map((node) => {
                const resolvedLabel =
                  typeof node.data?.label === 'string' && node.data.label.trim().length > 0
                    ? node.data.label
                    : node.id;
                return (
                  <li key={node.id}>
                    <button
                      type="button"
                      onClick={() => {
                        setSearchQuery(resolvedLabel);
                        setFocusNodeId(node.id);
                      }}
                      aria-label={`Copy ${resolvedLabel} into search`}
                    >
                      <span className="result-label">{resolvedLabel}</span>
                      <span className="result-meta">{node.id}</span>
                    </button>
                  </li>
                );
              })}
            </ul>
          ) : (
            <div className="search-empty">No companies match that search.</div>
          )
        ) : null}
      </div>
      <div className="canvas-window">
        <GraphCanvas nodes={nodes} edges={edges} focusNodeId={focusNodeId} />
      </div>
    </div>
  );
}
