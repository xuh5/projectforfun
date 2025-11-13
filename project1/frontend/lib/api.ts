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

