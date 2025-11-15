'use client';

import { ChangeEvent, FormEvent, useCallback, useEffect, useMemo, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';

import GraphCanvas from '../components/GraphCanvas';
import { useGraphData } from '../hooks/useGraphData';
import { searchCompanies, type SearchHit } from '../lib/api';
import type { GraphNode } from '../lib/types';

const SEARCH_RESULT_LIMIT = 8;
const SEARCH_DEBOUNCE_MS = 300;

const getNodeLabel = (node: GraphNode): string => {
  const rawLabel = typeof node.data?.label === 'string' ? node.data.label.trim() : '';
  return rawLabel.length > 0 ? rawLabel : node.id;
};

export default function Home() {
  const { nodes, edges, loading, error, refresh } = useGraphData();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchHit[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [focusNodeId, setFocusNodeId] = useState<string | null>(null);
  const router = useRouter();
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Auto-refresh on mount if data was mutated (stored in sessionStorage)
  useEffect(() => {
    const shouldRefresh = sessionStorage.getItem('graphNeedsRefresh');
    if (shouldRefresh === 'true') {
      sessionStorage.removeItem('graphNeedsRefresh');
      refresh();
    }
  }, [refresh]);

  // Debounced backend search
  useEffect(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    const trimmedQuery = searchQuery.trim();
    if (!trimmedQuery) {
      setSearchResults([]);
      setSearchLoading(false);
      return;
    }

    setSearchLoading(true);
    debounceTimerRef.current = setTimeout(async () => {
      try {
        const response = await searchCompanies(trimmedQuery, SEARCH_RESULT_LIMIT);
        setSearchResults(response?.results || []);
      } catch (err) {
        setSearchResults([]);
      } finally {
        setSearchLoading(false);
      }
    }, SEARCH_DEBOUNCE_MS);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [searchQuery]);

  // Convert search hits to matching nodes for compatibility
  const matchingNodes = useMemo<GraphNode[]>(() => {
    if (!searchQuery.trim() || searchResults.length === 0) return [];

    return searchResults
      .map((hit) => {
        const node = nodes.find((n) => n.id === hit.id);
        return node || null;
      })
      .filter((node): node is GraphNode => node !== null);
  }, [nodes, searchResults, searchQuery]);

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
          searchLoading ? (
            <div className="search-empty">Searching...</div>
          ) : searchResults.length > 0 ? (
            <ul className="search-results" role="listbox">
              {searchResults.map((hit) => {
                const node = nodes.find((n) => n.id === hit.id);
                const resolvedLabel = node ? getNodeLabel(node) : hit.label;
                return (
                  <li key={hit.id}>
                    <button
                      type="button"
                      onClick={() => {
                        setSearchQuery(hit.label);
                        if (node) {
                          setFocusNodeId(hit.id);
                        } else {
                          // Navigate to company page even if not in graph yet
                          navigateToNode(hit.id);
                        }
                      }}
                      aria-label={`Select ${resolvedLabel}`}
                    >
                      <span className="result-label">{hit.label}</span>
                      <span className="result-meta">{hit.id}</span>
                      {hit.sector && <span className="result-meta"> • {hit.sector}</span>}
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
