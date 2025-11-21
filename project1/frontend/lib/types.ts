export type ScalarRecord = Record<string, unknown>;

export interface NodeDetail {
  id: string;
  data: {
    label: string;
    description?: string;
    type?: string; // e.g., "company", "person", "project", etc.
    sector?: string;
    category?: string;
    value?: number;
    [key: string]: unknown;
  };
}

// Backward compatibility alias
export type CompanyDetail = NodeDetail;

export interface GraphNodeData {
  label: string;
  description?: string;
  type?: string; // e.g., "company", "person", "project", etc.
  [key: string]: unknown;
}

export interface GraphNode {
  id: string;
  position: [number, number, number];
  color?: string;
  data?: GraphNodeData;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type?: string;  // e.g., "owns", "partners_with", "competes_with"
  strength?: number;
  created_datetime?: string;  // ISO format string
}

export interface StockPoint {
  dateLabel: string;
  price: number;
}

export interface RawGraphResponse {
  nodes: unknown[];
  edges: unknown[];
}

