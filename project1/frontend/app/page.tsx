'use client';

import { useEffect, useState } from 'react';
import GraphCanvas, { GraphEdge, GraphNode } from '../components/GraphCanvas';

const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));

const computeSphericalPosition = (index: number, total: number, radius = 5): [number, number, number] => {
  if (total <= 1) {
    return [0, 0, 0];
  }

  const normalizedIndex = index + 0.5;
  const y = 1 - (normalizedIndex / total) * 2;
  const distance = Math.sqrt(Math.max(0, 1 - y * y));
  const theta = GOLDEN_ANGLE * normalizedIndex;
  const x = Math.cos(theta) * distance;
  const z = Math.sin(theta) * distance;

  return [x * radius, y * radius, z * radius];
};

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

const createGraphNode = (node: any, index: number, total: number): GraphNode => {
  const positionFromNode = normalizeCartesianPosition(node?.position ?? {});
  const fallbackPosition = computeSphericalPosition(index, total);

  const rawData = { ...(node?.data ?? {}) };
  const label =
    typeof node?.label === 'string'
      ? node.label
      : typeof rawData.label === 'string'
        ? rawData.label
        : String(node?.id ?? `node-${index}`);
  const description =
    typeof node?.description === 'string'
      ? node.description
      : typeof rawData.description === 'string'
        ? rawData.description
        : undefined;

  return {
    id: String(node?.id ?? `node-${index}`),
    position: positionFromNode ?? fallbackPosition,
    color: typeof node?.color === 'string' ? node.color : (typeof rawData.color === 'string' ? rawData.color : undefined),
    data: {
      ...rawData,
      label,
      ...(description ? { description } : {}),
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
  };
};

export default function Home() {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [loading, setLoading] = useState(true);

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

      setNodes(apiNodes);
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
    const categories = ['A', 'B', 'C'];

    const sampleNodes: GraphNode[] = Array.from({ length: nodeCount }, (_, index) => {
      const position = computeSphericalPosition(index, nodeCount, 5);
      const color = palette[index % palette.length];

      return {
        id: `node-${index + 1}`,
        position,
        color,
        data: {
          label: `Node ${index + 1}`,
          description: `This is node number ${index + 1} in the 3D graph.`,
          category: categories[index % categories.length],
          value: Math.floor(Math.random() * 100),
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
      });

      if (longIndex !== nextIndex) {
        sampleEdges.push({
          id: `edge-${i}-${longIndex}`,
          source: sampleNodes[i].id,
          target: sampleNodes[longIndex].id,
        });
      }
    }

    setNodes(sampleNodes);
    setEdges(sampleEdges);
  };

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
      <div className="canvas-window">
        <GraphCanvas nodes={nodes} edges={edges} />
      </div>
    </div>
  );
}
