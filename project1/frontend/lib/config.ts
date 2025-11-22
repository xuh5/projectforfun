export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? process.env.API_BASE_URL ?? 'http://localhost:8000';

export const API_ROUTES = {
  graph: '/api/nodes',
  nodeDetail: (nodeId: string) => `/api/nodes/${encodeURIComponent(nodeId)}`,
  search: '/api/search',
  createNode: '/api/nodes',
  updateNode: (nodeId: string) => `/api/nodes/${encodeURIComponent(nodeId)}`,
  deleteNode: (nodeId: string) => `/api/nodes/${encodeURIComponent(nodeId)}`,
  createRelationship: '/api/relationships',
  updateRelationship: (relationshipId: string) => `/api/relationships/${encodeURIComponent(relationshipId)}`,
  deleteRelationship: (relationshipId: string) => `/api/relationships/${encodeURIComponent(relationshipId)}`,
  currentUser: '/api/users/me',
} as const;

export const buildApiUrl = (path: string): string => {
  if (!path.startsWith('/')) {
    throw new Error(`API paths must start with "/". Received: ${path}`);
  }

  return `${API_BASE_URL}${path}`;
};

