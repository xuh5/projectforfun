'use client';

import { ChangeEvent, FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';

import GraphCanvas from '../components/GraphCanvas';
import { useGraphData } from '../hooks/useGraphData';
import type { GraphNode } from '../lib/types';

const SEARCH_RESULT_LIMIT = 8;

const getNodeLabel = (node: GraphNode): string => {
  const rawLabel = typeof node.data?.label === 'string' ? node.data.label.trim() : '';
  return rawLabel.length > 0 ? rawLabel : node.id;
};

export default function Home() {
  const { nodes, edges, loading, error } = useGraphData();
  const [searchQuery, setSearchQuery] = useState('');
  const [focusNodeId, setFocusNodeId] = useState<string | null>(null);
  const router = useRouter();

  const matchingNodes = useMemo<GraphNode[]>(() => {
    const term = searchQuery.trim().toLowerCase();
    if (!term) return [];

    return nodes
      .filter((node) => {
        const label = typeof node.data?.label === 'string' ? node.data.label : '';
        return label.toLowerCase().includes(term) || node.id.toLowerCase().includes(term);
      })
      .slice(0, SEARCH_RESULT_LIMIT);
  }, [nodes, searchQuery]);

  const resolveNodeLabel = useCallback(
    (nodeId: string): string | null => {
      const node = nodes.find((candidate) => candidate.id === nodeId);
      if (!node) return null;
      return getNodeLabel(node);
    },
    [nodes]
  );

  const navigateToNode = useCallback(
    (nodeId: string): string | null => {
      const label = resolveNodeLabel(nodeId);
      if (!label) {
        return null;
      }

      const params = new URLSearchParams();
      if (label !== nodeId) {
        params.set('label', label);
      }
      const query = params.toString();
      router.push(`/company/${encodeURIComponent(nodeId)}${query ? `?${query}` : ''}`);
      return label;
    },
    [resolveNodeLabel, router]
  );

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
        const resolvedLabel = getNodeLabel(firstMatch);
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

  const handleNodeClick = useCallback(
    (nodeId: string) => {
      const label = navigateToNode(nodeId);
      if (label) {
        setSearchQuery(label);
      }
      setFocusNodeId(nodeId);
    },
    [navigateToNode]
  );

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

        {error ? <div className="search-hint" role="status">{error}</div> : null}

        {searchQuery.trim().length > 0 ? (
          matchingNodes.length > 0 ? (
            <ul className="search-results" role="listbox">
              {matchingNodes.map((node) => {
                const resolvedLabel = getNodeLabel(node);
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
        <GraphCanvas nodes={nodes} edges={edges} focusNodeId={focusNodeId} onNodeClick={handleNodeClick} />
      </div>
    </div>
  );
}
