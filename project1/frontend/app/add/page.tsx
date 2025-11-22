'use client';

import { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { createNode, createRelationship, fetchGraphData, type CreateNodeRequest, type CreateRelationshipRequest } from '../../lib/api';
import { useToast } from '../../components/ToastProvider';
import { NODE_TYPE_OPTIONS, RELATION_TYPE_OPTIONS } from '../../lib/constants';
import { CompanyNodeForm, GenericNodeForm } from '../../components/NodeForms';
import type { GraphNode } from '../../lib/types';

type TabType = 'node' | 'relationship';

export default function AddDataPage() {
  const router = useRouter();
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState<TabType>('node');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [availableNodes, setAvailableNodes] = useState<GraphNode[]>([]);
  const [loadingNodes, setLoadingNodes] = useState(false);

  // Node form state
  const defaultNodeType = NODE_TYPE_OPTIONS[0]?.value ?? 'company';
  const [nodeForm, setNodeForm] = useState<CreateNodeRequest>({
    id: '',
    type: defaultNodeType,
    label: '',
    description: '',
    sector: '',
    color: '',
    metadata: {},
  });

  // Relationship form state
  const defaultRelationType = RELATION_TYPE_OPTIONS[0]?.value ?? 'works_with';
  const [relationshipForm, setRelationshipForm] = useState<CreateRelationshipRequest>({
    source_id: '',
    target_id: '',
    type: defaultRelationType,
    strength: undefined,
  });

  // Fetch available nodes when relationship tab is active
  useEffect(() => {
    if (activeTab === 'relationship') {
      loadAvailableNodes();
    }
  }, [activeTab]);

  const loadAvailableNodes = async () => {
    setLoadingNodes(true);
    try {
      const graphData = await fetchGraphData();
      if (graphData?.nodes) {
        setAvailableNodes(graphData.nodes);
      }
    } catch (err) {
      console.error('Failed to load nodes:', err);
      showToast('Failed to load available nodes', 'error');
    } finally {
      setLoadingNodes(false);
    }
  };

  const getNodeLabel = (node: GraphNode): string => {
    return node.data?.label || node.id;
  };

  const getNodeTypeLabel = (type: string) => {
    return NODE_TYPE_OPTIONS.find((t) => t.value === type)?.label || type.charAt(0).toUpperCase() + type.slice(1);
  };

  const handleNodeSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Clean up empty fields
      const data: CreateNodeRequest = {
        id: nodeForm.id.trim().toUpperCase(), // Convert to uppercase for stock symbols
        type: nodeForm.type || 'company',
        label: nodeForm.label.trim(),
        description: nodeForm.description.trim(),
        ...(nodeForm.sector?.trim() && { sector: nodeForm.sector.trim() }),
        ...(nodeForm.color?.trim() && { color: nodeForm.color.trim() }),
        ...(Object.keys(nodeForm.metadata || {}).length > 0 && { metadata: nodeForm.metadata }),
      };

      await createNode(data);
      const typeLabel = getNodeTypeLabel(data.type || 'company');
      showToast(`${typeLabel} "${data.label}" created successfully!`, 'success');
      
      // Mark graph as needing refresh
      sessionStorage.setItem('graphNeedsRefresh', 'true');
      
      // Reset form
      setNodeForm({
        id: '',
        type: defaultNodeType,
        label: '',
        description: '',
        sector: '',
        color: '',
        metadata: {},
      });

      // Optionally redirect after a delay
      setTimeout(() => {
        router.push('/');
      }, 2000);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create node';
      setError(message);
      showToast(message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleRelationshipSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (!relationshipForm.source_id || !relationshipForm.target_id) {
        throw new Error('Please select both source and target nodes');
      }

      if (relationshipForm.source_id === relationshipForm.target_id) {
        throw new Error('Source and target nodes must be different');
      }

      if (!relationshipForm.type) {
        throw new Error('Please select a relationship type');
      }

      const data: CreateRelationshipRequest = {
        source_id: relationshipForm.source_id,
        target_id: relationshipForm.target_id,
        type: relationshipForm.type,
        ...(relationshipForm.strength !== undefined && relationshipForm.strength !== null && { strength: relationshipForm.strength }),
      };

      await createRelationship(data);
      const sourceLabel = getNodeLabel(availableNodes.find(n => n.id === data.source_id) || { id: data.source_id, position: [0, 0, 0] } as GraphNode);
      const targetLabel = getNodeLabel(availableNodes.find(n => n.id === data.target_id) || { id: data.target_id, position: [0, 0, 0] } as GraphNode);
      const typeLabel = RELATION_TYPE_OPTIONS.find(t => t.value === data.type)?.label || data.type;
      showToast(`Relationship "${typeLabel}" between "${sourceLabel}" and "${targetLabel}" created successfully!`, 'success');
      
      // Mark graph as needing refresh
      sessionStorage.setItem('graphNeedsRefresh', 'true');
      
      // Reset form
      setRelationshipForm({
        source_id: '',
        target_id: '',
        type: defaultRelationType,
        strength: undefined,
      });

      // Reload nodes to get updated list
      await loadAvailableNodes();

      // Optionally redirect after a delay
      setTimeout(() => {
        router.push('/');
      }, 2000);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create relationship';
      setError(message);
      showToast(message, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-wrapper">
      <div className="add-data-container">
        <div className="add-data-header">
          <h1>Add Data</h1>
          <button 
            className="back-button"
            onClick={() => router.push('/')}
            type="button"
          >
            ← Back to Graph
          </button>
        </div>

        <div className="tabs">
          <button
            className={`tab ${activeTab === 'node' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('node');
              setError(null);
            }}
            type="button"
          >
            Add Node
          </button>
          <button
            className={`tab ${activeTab === 'relationship' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('relationship');
              setError(null);
            }}
            type="button"
          >
            Add Relationship
          </button>
        </div>

        {error && (
          <div className="error-message" role="alert">
            {error}
          </div>
        )}

        {activeTab === 'node' && (
          <form className="data-form" onSubmit={handleNodeSubmit}>
            <div className="form-group">
              <label htmlFor="node-type">
                Type <span className="required">*</span>
              </label>
              <select
                id="node-type"
                value={nodeForm.type}
                onChange={(e) => setNodeForm({ ...nodeForm, type: e.target.value })}
                required
                disabled={loading}
              >
                {NODE_TYPE_OPTIONS.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
              <small>Select the type of node to create</small>
            </div>

            {nodeForm.type === 'company' ? (
              <CompanyNodeForm
                formData={nodeForm}
                onChange={setNodeForm}
                loading={loading}
                getNodeTypeLabel={getNodeTypeLabel}
              />
            ) : (
              <GenericNodeForm
                formData={nodeForm}
                onChange={setNodeForm}
                loading={loading}
                getNodeTypeLabel={getNodeTypeLabel}
              />
            )}

            <button type="submit" className="submit-button" disabled={loading}>
              {loading ? 'Creating...' : `Create ${getNodeTypeLabel(nodeForm.type ?? defaultNodeType)}`}
            </button>
          </form>
        )}

        {activeTab === 'relationship' && (
          <form className="data-form" onSubmit={handleRelationshipSubmit}>
            {loadingNodes && (
              <div className="form-group">
                <p>Loading available nodes...</p>
              </div>
            )}

            {!loadingNodes && availableNodes.length === 0 && (
              <div className="form-group">
                <p style={{ color: '#ff6b6b' }}>No nodes available. Please create nodes first.</p>
              </div>
            )}

            {!loadingNodes && availableNodes.length > 0 && (
              <>
                <div className="form-group">
                  <label htmlFor="relationship-type">
                    Relationship Type <span className="required">*</span>
                  </label>
                  <select
                    id="relationship-type"
                    value={relationshipForm.type}
                    onChange={(e) => setRelationshipForm({ ...relationshipForm, type: e.target.value })}
                    required
                    disabled={loading}
                  >
                    {RELATION_TYPE_OPTIONS.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                  <small>Select the type of relationship</small>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="source-id">
                      Source Node <span className="required">*</span>
                    </label>
                    <select
                      id="source-id"
                      value={relationshipForm.source_id}
                      onChange={(e) => setRelationshipForm({ ...relationshipForm, source_id: e.target.value })}
                      required
                      disabled={loading}
                    >
                      <option value="">Select source node</option>
                      {availableNodes.map((node) => (
                        <option key={node.id} value={node.id}>
                          {getNodeLabel(node)} ({node.id})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label htmlFor="target-id">
                      Target Node <span className="required">*</span>
                    </label>
                    <select
                      id="target-id"
                      value={relationshipForm.target_id}
                      onChange={(e) => setRelationshipForm({ ...relationshipForm, target_id: e.target.value })}
                      required
                      disabled={loading}
                    >
                      <option value="">Select target node</option>
                      {availableNodes
                        .filter((node) => node.id !== relationshipForm.source_id)
                        .map((node) => (
                          <option key={node.id} value={node.id}>
                            {getNodeLabel(node)} ({node.id})
                          </option>
                        ))}
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="relationship-strength">Strength (0-1)</label>
                  <input
                    id="relationship-strength"
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={relationshipForm.strength ?? ''}
                    onChange={(e) => setRelationshipForm({ ...relationshipForm, strength: e.target.value ? parseFloat(e.target.value) : undefined })}
                    placeholder="e.g., 0.5"
                    disabled={loading}
                  />
                  <small>Optional: Relationship strength between 0 and 1</small>
                </div>

                <button type="submit" className="submit-button" disabled={loading || loadingNodes}>
                  {loading ? 'Creating...' : 'Create Relationship'}
                </button>
              </>
            )}
          </form>
        )}
      </div>
    </div>
  );
}

