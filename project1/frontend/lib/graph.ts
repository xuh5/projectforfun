import {
  forceCenter,
  forceCollide,
  forceLink,
  forceManyBody,
  forceSimulation,
  forceX,
  forceY,
  forceZ,
} from 'd3-force-3d';

import type { GraphEdge, GraphNode, RawGraphResponse } from './types';
import { FORCE_LAYOUT, POSITION_CONFIG } from './graphConfig';

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
  'Zoom',
] as const;

const SAMPLE_PALETTE = ['#667eea', '#764ba2', '#f093fb', '#4f46e5', '#22d3ee', '#f472b6'] as const;
const SAMPLE_SECTORS = ['AI', 'Automotive', 'Consumer', 'Enterprise', 'Cloud', 'Semiconductors'] as const;

type RawNode = {
  id?: unknown;
  position?: Record<string, unknown>;
  data?: Record<string, unknown>;
  label?: unknown;
  name?: unknown;
  description?: unknown;
  color?: unknown;
};

type RawEdge = {
  id?: unknown;
  source?: unknown;
  target?: unknown;
  strength?: unknown;
};

const maybeNumber = (value: unknown): number | null =>
  typeof value === 'number' && Number.isFinite(value) ? value : null;

export const normalizeCartesianPosition = (
  position: Record<string, unknown> | undefined | null
): [number, number, number] | null => {
  if (!position) return null;

  const x = maybeNumber((position as { x?: number }).x ?? (position as { left?: number }).left);
  const y = maybeNumber((position as { y?: number }).y ?? (position as { top?: number }).top);
  const z = maybeNumber((position as { z?: number }).z);

  if (x === null && y === null && z === null) {
    return null;
  }

  return [(x ?? 0) / POSITION_CONFIG.positionScale, (y ?? 0) / POSITION_CONFIG.positionScale, (z ?? 0) / POSITION_CONFIG.positionScale];
};

export const createInitialPosition = (fallbackScale: number): [number, number, number] => {
  const range = Math.max(2, fallbackScale);
  return [(Math.random() - 0.5) * range, (Math.random() - 0.5) * range, (Math.random() - 0.5) * range];
};

export const createGraphNode = (node: RawNode, index: number, total: number): GraphNode => {
  const positionFromNode = normalizeCartesianPosition(node?.position);
  const rawData = { ...(node?.data ?? {}) };

  const labelCandidates = [node?.label, rawData.label, rawData.name, node?.name];

  const resolvedLabel =
    labelCandidates.find((value) => typeof value === 'string' && value.trim().length > 0)?.toString() ??
    DEFAULT_COMPANY_NAMES[index % DEFAULT_COMPANY_NAMES.length];

  const description =
    typeof node?.description === 'string'
      ? node.description
      : typeof rawData.description === 'string'
        ? rawData.description
        : `${resolvedLabel} is a key company within the network.`;

  const colorCandidate =
    typeof node?.color === 'string'
      ? node.color
      : typeof rawData.color === 'string'
        ? rawData.color
        : undefined;

  return {
    id: String(node?.id ?? `node-${index}`),
    position: positionFromNode ?? createInitialPosition(total),
    color: colorCandidate,
    data: {
      ...rawData,
      label: resolvedLabel,
      description,
    },
  };
};

export const createGraphEdge = (edge: RawEdge, index: number): GraphEdge | null => {
  const source = edge?.source;
  const target = edge?.target;

  if (!source || !target) {
    return null;
  }

  const strength =
    typeof edge?.strength === 'number' && Number.isFinite(edge.strength)
      ? Math.min(Math.max(edge.strength, 0), 1)
      : undefined;

  return {
    id: String(edge?.id ?? `edge-${index}`),
    source: String(source),
    target: String(target),
    strength,
  };
};

// Default link strength is now defined in graphConfig.ts as FORCE_LAYOUT.defaultLinkStrength

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

export const runForceDirectedLayout = (
  nodes: GraphNode[],
  edges: GraphEdge[],
  iterations: number = FORCE_LAYOUT.defaultIterations
): GraphNode[] => {
  if (!nodes.length || edges.length === 0) {
    return nodes;
  }

  const scale = Math.cbrt(nodes.length) * FORCE_LAYOUT.scaleMultiplier;

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
    strength: edge.strength,
  }));

  const linkForce = forceLink<SimulationNode, SimulationLink>(simulationLinks)
    .id((node: SimulationNode) => node.id)
    .strength((link: SimulationLink) => link.strength ?? FORCE_LAYOUT.defaultLinkStrength)
    .distance(() => FORCE_LAYOUT.linkDistance);

  const baseCharge = FORCE_LAYOUT.chargeStrengthBase * Math.cbrt(nodes.length);

  const simulation = forceSimulation<SimulationNode>(simulationNodes)
    .force('link', linkForce)
    .force('charge', forceManyBody().strength(baseCharge))
    .force('center', forceCenter(0, 0, 0))
    .force('collision', forceCollide<SimulationNode>(FORCE_LAYOUT.collisionRadius).strength(FORCE_LAYOUT.collisionStrength))
    .force('x', forceX<SimulationNode>(0).strength(FORCE_LAYOUT.axisForceStrength))
    .force('y', forceY<SimulationNode>(0).strength(FORCE_LAYOUT.axisForceStrength))
    .force('z', forceZ<SimulationNode>(0).strength(FORCE_LAYOUT.axisForceStrength));

  simulation.alpha(1).alphaMin(0.001);
  simulation.stop();

  for (let i = 0; i < iterations; i += 1) {
    simulation.tick();
  }

  return simulationNodes.map((node) => {
    const { x = 0, y = 0, z = 0, position: _position, ...rest } = node;
    return {
      ...rest,
      position: [x, y, z],
    };
  });
};

export const hydrateGraphResponse = (raw: RawGraphResponse): { nodes: GraphNode[]; edges: GraphEdge[] } => {
  const rawNodes: RawNode[] = Array.isArray(raw?.nodes) ? (raw.nodes as RawNode[]) : [];
  const rawEdges: RawEdge[] = Array.isArray(raw?.edges) ? (raw.edges as RawEdge[]) : [];

  const nodes = rawNodes.map((node, index) => createGraphNode(node, index, rawNodes.length));
  const edges = rawEdges
    .map((edge, index) => createGraphEdge(edge, index))
    .filter((edge): edge is GraphEdge => edge !== null);

  return { nodes, edges };
};

export const generateSampleGraphData = (nodeCount = 18): { nodes: GraphNode[]; edges: GraphEdge[] } => {
  const sampleNodes: GraphNode[] = Array.from({ length: nodeCount }, (_, index) => {
    const color = SAMPLE_PALETTE[index % SAMPLE_PALETTE.length];
    const companyName = DEFAULT_COMPANY_NAMES[index % DEFAULT_COMPANY_NAMES.length];
    const sector = SAMPLE_SECTORS[index % SAMPLE_SECTORS.length];

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

  for (let i = 0; i < nodeCount; i += 1) {
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

  const positionedNodes = runForceDirectedLayout(sampleNodes, sampleEdges, FORCE_LAYOUT.defaultIterations);

  return { nodes: positionedNodes, edges: sampleEdges };
};

