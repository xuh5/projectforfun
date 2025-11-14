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
      throw new Error(error.detail || 'Failed to create company');
    }

    return (await response.json()) as CompanyDetail;
  } catch (error) {
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
      throw new Error(error.detail || 'Failed to create relationship');
    }

    return (await response.json()) as CreateRelationshipRequest;
  } catch (error) {
    throw error;
  }
};

