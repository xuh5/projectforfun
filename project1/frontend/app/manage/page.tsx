'use client';

import { useState, useEffect, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  fetchGraphData,
  updateCompany,
  deleteCompany,
  updateRelationship,
  deleteRelationship,
  getCurrentUserInfo,
  type UpdateCompanyRequest,
  type UpdateRelationshipRequest,
} from '../../lib/api';
import { hydrateGraphResponse } from '../../lib/graph';
import { useToast } from '../../components/ToastProvider';
import { useAuth } from '../../contexts/AuthContext';
import type { GraphEdge, GraphNode } from '../../lib/types';

type TabType = 'company' | 'relationship';

interface EditCompanyState {
  id: string;
  label: string;
  description?: string;
  sector?: string;
  color?: string;
}

interface EditRelationshipState {
  id: string;
  source_id: string;
  target_id: string;
  strength?: number;
}

export default function ManagePage() {
  const router = useRouter();
  const { showToast } = useToast();
  const { user, loading: authLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('company');
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [editingCompany, setEditingCompany] = useState<EditCompanyState | null>(null);
  const [editingRelationship, setEditingRelationship] = useState<EditRelationshipState | null>(null);
  const [deletingCompanyId, setDeletingCompanyId] = useState<string | null>(null);
  const [deletingRelationshipId, setDeletingRelationshipId] = useState<string | null>(null);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    checkAuthAndLoad();
  }, [user, authLoading]);

  const checkAuthAndLoad = async () => {
    // Wait for auth to finish loading
    if (authLoading) {
      setCheckingAuth(true);
      return;
    }

    setCheckingAuth(true);

    // Check if user is logged in
    if (!user) {
      setCheckingAuth(false);
      router.push('/');
      return;
    }

    // Check if user is admin
    try {
      const userInfo = await getCurrentUserInfo();
      if (!userInfo || userInfo.role !== 'admin') {
        setCheckingAuth(false);
        router.push('/');
        return;
      }

      setIsAdmin(true);
      await loadData();
    } catch (err) {
      setCheckingAuth(false);
      router.push('/');
    } finally {
      setCheckingAuth(false);
    }
  };

  const loadData = async () => {
    setFetching(true);
    try {
      const rawGraph = await fetchGraphData();
      if (rawGraph) {
        const graphData = hydrateGraphResponse(rawGraph);
        setNodes(graphData?.nodes ?? []);
        setEdges(graphData?.edges ?? []);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load data';
      setError(message);
      showToast(message, 'error');
    } finally {
      setFetching(false);
    }
  };

  const handleUpdateCompany = async (e: FormEvent) => {
    e.preventDefault();
    if (!editingCompany) return;

    setLoading(true);
    setError(null);

    try {
      const data: UpdateCompanyRequest = {
        label: editingCompany.label?.trim(),
        description: editingCompany.description?.trim() || undefined,
        sector: editingCompany.sector?.trim() || undefined,
        color: editingCompany.color?.trim() || undefined,
      };

      await updateCompany(editingCompany.id, data);
      showToast(`Company "${data.label}" updated successfully!`, 'success');
      setEditingCompany(null);
      sessionStorage.setItem('graphNeedsRefresh', 'true');
      await loadData();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update company';
      setError(message);
      showToast(message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteCompany = async () => {
    if (!deletingCompanyId) return;

    setLoading(true);
    setError(null);

    try {
      await deleteCompany(deletingCompanyId);
      showToast('Company deleted successfully!', 'success');
      setDeletingCompanyId(null);
      sessionStorage.setItem('graphNeedsRefresh', 'true');
      await loadData();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete company';
      setError(message);
      showToast(message, 'error');
      setDeletingCompanyId(null);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateRelationship = async (e: FormEvent) => {
    e.preventDefault();
    if (!editingRelationship) return;

    setLoading(true);
    setError(null);

    try {
      const data: UpdateRelationshipRequest = {
        source_id: editingRelationship.source_id?.trim() || undefined,
        target_id: editingRelationship.target_id?.trim() || undefined,
        strength:
          editingRelationship.strength !== undefined && editingRelationship.strength !== null
            ? Number(editingRelationship.strength)
            : undefined,
      };

      await updateRelationship(editingRelationship.id, data);
      showToast('Relationship updated successfully!', 'success');
      setEditingRelationship(null);
      sessionStorage.setItem('graphNeedsRefresh', 'true');
      await loadData();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update relationship';
      setError(message);
      showToast(message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteRelationship = async () => {
    if (!deletingRelationshipId) return;

    setLoading(true);
    setError(null);

    try {
      await deleteRelationship(deletingRelationshipId);
      showToast('Relationship deleted successfully!', 'success');
      setDeletingRelationshipId(null);
      sessionStorage.setItem('graphNeedsRefresh', 'true');
      await loadData();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete relationship';
      setError(message);
      showToast(message, 'error');
      setDeletingRelationshipId(null);
    } finally {
      setLoading(false);
    }
  };

  const getNodeLabel = (nodeId: string): string => {
    const node = nodes.find((n) => n.id === nodeId);
    return node?.data?.label || nodeId;
  };

  // Hide page content while checking auth or if not admin
  if (checkingAuth || authLoading || !isAdmin) {
    return null;
  }

  return (
    <div className="page-wrapper">
      <div className="add-data-container">
        <div className="add-data-header">
          <h1>Manage Data</h1>
          <button className="back-button" onClick={() => router.push('/')} type="button">
            ← Back to Graph
          </button>
        </div>

        <div className="tabs">
          <button
            className={`tab ${activeTab === 'company' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('company');
              setError(null);
              setEditingCompany(null);
              setDeletingCompanyId(null);
            }}
            type="button"
          >
            Manage Companies
          </button>
          <button
            className={`tab ${activeTab === 'relationship' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('relationship');
              setError(null);
              setEditingRelationship(null);
              setDeletingRelationshipId(null);
            }}
            type="button"
          >
            Manage Relationships
          </button>
        </div>

        {error && (
          <div className="error-message" role="alert">
            {error}
          </div>
        )}

        {fetching ? (
          <div className="loading-message">Loading data...</div>
        ) : (
          <>
            {activeTab === 'company' && (
              <div className="manage-content">
                {nodes.length === 0 ? (
                  <div className="empty-state">No companies found.</div>
                ) : (
                  <div className="items-list">
                    {nodes.map((node) => (
                      <div key={node.id} className="item-card">
                        <div className="item-info">
                          <h3>{getNodeLabel(node.id)}</h3>
                          <p className="item-id">ID: {node.id}</p>
                          {typeof node.data?.description === 'string' && node.data.description && (
                            <p className="item-description">{node.data.description}</p>
                          )}
                          {typeof node.data?.sector === 'string' && node.data.sector && (
                            <p className="item-meta">Sector: {node.data.sector}</p>
                          )}
                        </div>
                        <div className="item-actions">
                          <button
                            className="action-button edit-button"
                            onClick={() => {
                              setEditingCompany({
                                id: node.id,
                                label: getNodeLabel(node.id),
                                description:
                                  typeof node.data?.description === 'string' ? node.data.description : undefined,
                                sector: typeof node.data?.sector === 'string' ? node.data.sector : undefined,
                                color:
                                  node.color ||
                                  (typeof node.data?.color === 'string' ? node.data.color : undefined),
                              });
                            }}
                            type="button"
                            disabled={loading}
                          >
                            Edit
                          </button>
                          <button
                            className="action-button delete-button"
                            onClick={() => setDeletingCompanyId(node.id)}
                            type="button"
                            disabled={loading}
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'relationship' && (
              <div className="manage-content">
                {edges.length === 0 ? (
                  <div className="empty-state">No relationships found.</div>
                ) : (
                  <div className="items-list">
                    {edges.map((edge) => (
                      <div key={edge.id} className="item-card">
                        <div className="item-info">
                          <h3>Relationship: {edge.id}</h3>
                          <p className="item-meta">
                            Source: <strong>{getNodeLabel(edge.source)}</strong> ({edge.source})
                          </p>
                          <p className="item-meta">
                            Target: <strong>{getNodeLabel(edge.target)}</strong> ({edge.target})
                          </p>
                          {edge.strength !== undefined && (
                            <p className="item-meta">Strength: {edge.strength.toFixed(2)}</p>
                          )}
                        </div>
                        <div className="item-actions">
                          <button
                            className="action-button edit-button"
                            onClick={() => {
                              setEditingRelationship({
                                id: edge.id,
                                source_id: edge.source,
                                target_id: edge.target,
                                strength: edge.strength,
                              });
                            }}
                            type="button"
                            disabled={loading}
                          >
                            Edit
                          </button>
                          <button
                            className="action-button delete-button"
                            onClick={() => setDeletingRelationshipId(edge.id)}
                            type="button"
                            disabled={loading}
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* Edit Company Modal */}
        {editingCompany && (
          <div className="modal-overlay" onClick={() => setEditingCompany(null)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Edit Company</h2>
                <button
                  className="modal-close"
                  onClick={() => setEditingCompany(null)}
                  type="button"
                  disabled={loading}
                >
                  ×
                </button>
              </div>
              <form className="modal-form" onSubmit={handleUpdateCompany}>
                <div className="form-group">
                  <label htmlFor="edit-company-label">
                    Company Name <span className="required">*</span>
                  </label>
                  <input
                    id="edit-company-label"
                    type="text"
                    value={editingCompany.label || ''}
                    onChange={(e) =>
                      setEditingCompany({ ...editingCompany, label: e.target.value })
                    }
                    required
                    disabled={loading}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="edit-company-description">Description</label>
                  <textarea
                    id="edit-company-description"
                    value={editingCompany.description || ''}
                    onChange={(e) =>
                      setEditingCompany({ ...editingCompany, description: e.target.value })
                    }
                    rows={4}
                    disabled={loading}
                  />
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="edit-company-sector">Sector</label>
                    <input
                      id="edit-company-sector"
                      type="text"
                      value={editingCompany.sector || ''}
                      onChange={(e) =>
                        setEditingCompany({ ...editingCompany, sector: e.target.value })
                      }
                      disabled={loading}
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="edit-company-color">Color (Hex)</label>
                    <input
                      id="edit-company-color"
                      type="text"
                      value={editingCompany.color || ''}
                      onChange={(e) =>
                        setEditingCompany({ ...editingCompany, color: e.target.value })
                      }
                      disabled={loading}
                    />
                  </div>
                </div>
                <div className="modal-actions">
                  <button
                    type="button"
                    className="modal-button modal-button-cancel"
                    onClick={() => setEditingCompany(null)}
                    disabled={loading}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="modal-button modal-button-submit"
                    disabled={loading}
                  >
                    {loading ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Edit Relationship Modal */}
        {editingRelationship && (
          <div className="modal-overlay" onClick={() => setEditingRelationship(null)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Edit Relationship</h2>
                <button
                  className="modal-close"
                  onClick={() => setEditingRelationship(null)}
                  type="button"
                  disabled={loading}
                >
                  ×
                </button>
              </div>
              <form className="modal-form" onSubmit={handleUpdateRelationship}>
                <div className="form-group">
                  <label htmlFor="edit-relationship-source">
                    Source Company ID <span className="required">*</span>
                  </label>
                  <select
                    id="edit-relationship-source"
                    value={editingRelationship.source_id || ''}
                    onChange={(e) =>
                      setEditingRelationship({ ...editingRelationship, source_id: e.target.value })
                    }
                    required
                    disabled={loading}
                  >
                    <option value="">Select source company...</option>
                    {nodes.map((node) => (
                      <option key={node.id} value={node.id}>
                        {getNodeLabel(node.id)} ({node.id})
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="edit-relationship-target">
                    Target Company ID <span className="required">*</span>
                  </label>
                  <select
                    id="edit-relationship-target"
                    value={editingRelationship.target_id || ''}
                    onChange={(e) =>
                      setEditingRelationship({ ...editingRelationship, target_id: e.target.value })
                    }
                    required
                    disabled={loading}
                  >
                    <option value="">Select target company...</option>
                    {nodes.map((node) => (
                      <option key={node.id} value={node.id}>
                        {getNodeLabel(node.id)} ({node.id})
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="edit-relationship-strength">Strength (0-1)</label>
                  <input
                    id="edit-relationship-strength"
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={editingRelationship.strength ?? ''}
                    onChange={(e) =>
                      setEditingRelationship({
                        ...editingRelationship,
                        strength: e.target.value ? parseFloat(e.target.value) : undefined,
                      })
                    }
                    disabled={loading}
                  />
                </div>
                <div className="modal-actions">
                  <button
                    type="button"
                    className="modal-button modal-button-cancel"
                    onClick={() => setEditingRelationship(null)}
                    disabled={loading}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="modal-button modal-button-submit"
                    disabled={loading}
                  >
                    {loading ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Delete Confirmations */}
        {deletingCompanyId && (
          <div className="modal-overlay" onClick={() => setDeletingCompanyId(null)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Delete Company</h2>
              </div>
              <div className="modal-body">
                <p>
                  Are you sure you want to delete "{getNodeLabel(deletingCompanyId)}"? This action
                  cannot be undone.
                </p>
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  className="modal-button modal-button-cancel"
                  onClick={() => setDeletingCompanyId(null)}
                  disabled={loading}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="modal-button modal-button-delete"
                  onClick={handleDeleteCompany}
                  disabled={loading}
                >
                  {loading ? 'Deleting...' : 'Delete'}
                </button>
              </div>
            </div>
          </div>
        )}

        {deletingRelationshipId && (
          <div className="modal-overlay" onClick={() => setDeletingRelationshipId(null)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Delete Relationship</h2>
              </div>
              <div className="modal-body">
                <p>Are you sure you want to delete this relationship? This action cannot be undone.</p>
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  className="modal-button modal-button-cancel"
                  onClick={() => setDeletingRelationshipId(null)}
                  disabled={loading}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="modal-button modal-button-delete"
                  onClick={handleDeleteRelationship}
                  disabled={loading}
                >
                  {loading ? 'Deleting...' : 'Delete'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

