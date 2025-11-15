import { buildApiUrl, API_ROUTES } from './config';
import type { CompanyDetail, RawGraphResponse } from './types';

const withDefaultInit = (init?: RequestInit): RequestInit => ({
  cache: 'no-store',
  ...init,
});

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

export const fetchCompanyDetail = async (
  nodeId: string,
  init?: RequestInit
): Promise<CompanyDetail | null> => {
  try {
    const response = await fetch(buildApiUrl(API_ROUTES.nodeDetail(nodeId)), withDefaultInit(init));
    if (!response.ok) {
      return null;
    }

    return (await response.json()) as CompanyDetail;
  } catch {
    return null;
  }
};

export interface CreateCompanyRequest {
  id: string;
  label: string;
  description: string;
  sector?: string;
  color?: string;
  metadata?: Record<string, unknown>;
}

export interface CreateRelationshipRequest {
  id: string;
  source_id: string;
  target_id: string;
  strength?: number;
}

export const createCompany = async (data: CreateCompanyRequest): Promise<CompanyDetail | null> => {
  try {
    const response = await fetch(buildApiUrl(API_ROUTES.createCompany), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create company' }));
      throw new Error(error.detail || 'Failed to create company. Please check your connection and try again.');
    }

    return (await response.json()) as CompanyDetail;
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Unable to connect to the server. Please check your internet connection.');
    }
    throw error;
  }
};

export const createRelationship = async (data: CreateRelationshipRequest): Promise<CreateRelationshipRequest | null> => {
  try {
    const response = await fetch(buildApiUrl(API_ROUTES.createRelationship), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create relationship' }));
      throw new Error(error.detail || 'Failed to create relationship. Please check your connection and try again.');
    }

    return (await response.json()) as CreateRelationshipRequest;
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Unable to connect to the server. Please check your internet connection.');
    }
    throw error;
  }
};

export interface UpdateCompanyRequest {
  label?: string;
  description?: string;
  sector?: string;
  color?: string;
  metadata?: Record<string, unknown>;
}

export interface UpdateRelationshipRequest {
  source_id?: string;
  target_id?: string;
  strength?: number;
}

export const updateCompany = async (companyId: string, data: UpdateCompanyRequest): Promise<CompanyDetail | null> => {
  try {
    const response = await fetch(buildApiUrl(API_ROUTES.updateCompany(companyId)), {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to update company' }));
      if (response.status === 404) {
        throw new Error('Company not found. It may have been deleted.');
      }
      throw new Error(error.detail || 'Failed to update company. Please try again.');
    }

    return (await response.json()) as CompanyDetail;
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Unable to connect to the server. Please check your internet connection.');
    }
    throw error;
  }
};

export const deleteCompany = async (companyId: string): Promise<void> => {
  try {
    const response = await fetch(buildApiUrl(API_ROUTES.deleteCompany(companyId)), {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to delete company' }));
      if (response.status === 404) {
        throw new Error('Company not found. It may have already been deleted.');
      }
      throw new Error(error.detail || 'Failed to delete company. Please try again.');
    }
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Unable to connect to the server. Please check your internet connection.');
    }
    throw error;
  }
};

export const updateRelationship = async (relationshipId: string, data: UpdateRelationshipRequest): Promise<{ id: string; source_id: string; target_id: string; strength?: number } | null> => {
  try {
    const response = await fetch(buildApiUrl(API_ROUTES.updateRelationship(relationshipId)), {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to update relationship' }));
      if (response.status === 404) {
        throw new Error('Relationship not found. It may have been deleted.');
      }
      throw new Error(error.detail || 'Failed to update relationship. Please try again.');
    }

    return (await response.json()) as { id: string; source_id: string; target_id: string; strength?: number };
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Unable to connect to the server. Please check your internet connection.');
    }
    throw error;
  }
};

export const deleteRelationship = async (relationshipId: string): Promise<void> => {
  try {
    const response = await fetch(buildApiUrl(API_ROUTES.deleteRelationship(relationshipId)), {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to delete relationship' }));
      if (response.status === 404) {
        throw new Error('Relationship not found. It may have already been deleted.');
      }
      throw new Error(error.detail || 'Failed to delete relationship. Please try again.');
    }
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Unable to connect to the server. Please check your internet connection.');
    }
    throw error;
  }
};

export interface SearchHit {
  id: string;
  label: string;
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

