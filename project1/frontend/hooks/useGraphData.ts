import { useCallback, useEffect, useState } from 'react';

import { fetchGraphData } from '../lib/api';
import { generateSampleGraphData, hydrateGraphResponse, runForceDirectedLayout } from '../lib/graph';
import type { GraphEdge, GraphNode } from '../lib/types';

interface UseGraphDataResult {
  nodes: GraphNode[];
  edges: GraphEdge[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

const buildErrorMessage = (raw?: unknown): string =>
  raw instanceof Error ? raw.message : 'Unable to load graph data.';

export const useGraphData = (): UseGraphDataResult => {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fallbackToSample = useCallback(() => {
    const sample = generateSampleGraphData();
    setNodes(sample.nodes);
    setEdges(sample.edges);
  }, []);

  const loadGraph = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const raw = await fetchGraphData();
      if (!raw) {
        fallbackToSample();
        setError('API did not return graph data. Showing sample dataset.');
        return;
      }

      const { nodes: hydratedNodes, edges: hydratedEdges } = hydrateGraphResponse(raw);

      if (!hydratedNodes.length || !hydratedEdges.length) {
        fallbackToSample();
        setError('Graph data was empty. Showing sample dataset.');
        return;
      }

      const positionedNodes = runForceDirectedLayout(hydratedNodes, hydratedEdges);
      setNodes(positionedNodes);
      setEdges(hydratedEdges);
    } catch (err) {
      setError(buildErrorMessage(err));
      fallbackToSample();
    } finally {
      setLoading(false);
    }
  }, [fallbackToSample]);

  useEffect(() => {
    void loadGraph();
  }, [loadGraph]);

  return {
    nodes,
    edges,
    loading,
    error,
    refresh: loadGraph,
  };
};

