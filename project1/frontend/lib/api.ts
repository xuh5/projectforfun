import { buildApiUrl, API_ROUTES } from './config';
import type { NodeDetail, RawGraphResponse } from './types';

const withDefaultInit = (init?: RequestInit): RequestInit => ({
  cache: 'no-store',
  ...init,
});

const handleApiError = (error: unknown, defaultMessage: string): Error => {
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return new Error('Unable to connect to the server. Please check your internet connection.');
  }
  if (error instanceof Error) {
    return error;
  }
  return new Error(defaultMessage);
};

const fetchWithErrorHandling = async <T>(
  url: string,
  options: RequestInit = {},
  errorMessage: string
): Promise<T> => {
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: errorMessage }));
      const statusMessage = response.status === 404 
        ? error.detail || 'Resource not found. It may have been deleted.'
        : error.detail || errorMessage;
      throw new Error(statusMessage);
    }
    return (await response.json()) as T;
  } catch (error) {
    throw handleApiError(error, errorMessage);
  }
};

export const fetchGraphData = async (init?: RequestInit): Promise<RawGraphResponse | null> => {
  try {
    const response = await fetch(buildApiUrl(API_ROUTES.graph), withDefaultInit(init));
    if (!response.ok) {
      return null;
    }

    return (await response.json()) as RawGraphResponse;
  } catch {
    return null;
  }
};

export const fetchNodeDetail = async (
  nodeId: string,
  init?: RequestInit
): Promise<NodeDetail | null> => {
  try {
    const response = await fetch(buildApiUrl(API_ROUTES.nodeDetail(nodeId)), withDefaultInit(init));
    if (!response.ok) {
      return null;
    }

    return (await response.json()) as NodeDetail;
  } catch {
    return null;
  }
};

// Backward compatibility alias
export const fetchCompanyDetail = fetchNodeDetail;

export interface CreateNodeRequest {
  id: string;
  type?: string; // e.g., "company", "person", "project", etc. Defaults to "company"
  label: string;
  description: string;
  sector?: string;
  color?: string;
  metadata?: Record<string, unknown>;
}

// Backward compatibility alias
export type CreateCompanyRequest = CreateNodeRequest;

export interface CreateRelationshipRequest {
  id: string;
  source_id: string;
  target_id: string;
  strength?: number;
}

export const createNode = async (data: CreateNodeRequest): Promise<NodeDetail | null> => {
  // Default type to "company" if not provided for backward compatibility
  const requestData = {
    ...data,
    type: data.type || 'company',
  };

  return fetchWithErrorHandling<NodeDetail>(
    buildApiUrl(API_ROUTES.createNode),
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    },
    'Failed to create node. Please check your connection and try again.'
  );
};

// Backward compatibility alias
export const createCompany = createNode;

export const createRelationship = async (data: CreateRelationshipRequest): Promise<CreateRelationshipRequest | null> => {
  return fetchWithErrorHandling<CreateRelationshipRequest>(
    buildApiUrl(API_ROUTES.createRelationship),
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    },
    'Failed to create relationship. Please check your connection and try again.'
  );
};

export interface UpdateNodeRequest {
  type?: string;
  label?: string;
  description?: string;
  sector?: string;
  color?: string;
  metadata?: Record<string, unknown>;
}

// Backward compatibility alias
export type UpdateCompanyRequest = UpdateNodeRequest;

export interface UpdateRelationshipRequest {
  source_id?: string;
  target_id?: string;
  strength?: number;
}

export const updateNode = async (nodeId: string, data: UpdateNodeRequest): Promise<NodeDetail | null> => {
  return fetchWithErrorHandling<NodeDetail>(
    buildApiUrl(API_ROUTES.updateNode(nodeId)),
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    },
    'Failed to update node. Please try again.'
  );
};

// Backward compatibility alias
export const updateCompany = updateNode;

export const deleteNode = async (nodeId: string): Promise<void> => {
  await fetchWithErrorHandling<void>(
    buildApiUrl(API_ROUTES.deleteNode(nodeId)),
    { method: 'DELETE' },
    'Failed to delete node. Please try again.'
  );
};

// Backward compatibility alias
export const deleteCompany = deleteNode;

export const updateRelationship = async (relationshipId: string, data: UpdateRelationshipRequest): Promise<{ id: string; source_id: string; target_id: string; strength?: number } | null> => {
  return fetchWithErrorHandling<{ id: string; source_id: string; target_id: string; strength?: number }>(
    buildApiUrl(API_ROUTES.updateRelationship(relationshipId)),
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    },
    'Failed to update relationship. Please try again.'
  );
};

export const deleteRelationship = async (relationshipId: string): Promise<void> => {
  await fetchWithErrorHandling<void>(
    buildApiUrl(API_ROUTES.deleteRelationship(relationshipId)),
    { method: 'DELETE' },
    'Failed to delete relationship. Please try again.'
  );
};

export interface SearchHit {
  id: string;
  label: string;
  type?: string;
  sector?: string;
  score?: number;
}

export interface SearchResponse {
  query: string;
  results: SearchHit[];
}

export const searchCompanies = async (query: string, limit: number = 8): Promise<SearchResponse | null> => {
  if (!query.trim()) {
    return null;
  }

  try {
    const params = new URLSearchParams({
      query: query.trim(),
      limit: limit.toString(),
    });
    const response = await fetch(buildApiUrl(`${API_ROUTES.search}?${params.toString()}`), withDefaultInit());

    if (!response.ok) {
      return null;
    }

    return (await response.json()) as SearchResponse;
  } catch {
    return null;
  }
};

