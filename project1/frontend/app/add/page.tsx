'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { createNode, createRelationship, type CreateNodeRequest, type CreateRelationshipRequest } from '../../lib/api';
import { useToast } from '../../components/ToastProvider';
import { NODE_TYPE_OPTIONS, SECTOR_OPTIONS } from '../../lib/constants';

type TabType = 'node' | 'relationship';

export default function AddDataPage() {
  const router = useRouter();
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState<TabType>('node');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
  const [relationshipForm, setRelationshipForm] = useState<CreateRelationshipRequest>({
    id: '',
    source_id: '',
    target_id: '',
    strength: undefined,
  });

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
      const data: CreateRelationshipRequest = {
        id: relationshipForm.id.trim(),
        source_id: relationshipForm.source_id.trim(),
        target_id: relationshipForm.target_id.trim(),
        ...(relationshipForm.strength !== undefined && relationshipForm.strength !== null && { strength: relationshipForm.strength }),
      };

      await createRelationship(data);
      showToast(`Relationship "${data.id}" created successfully!`, 'success');
      
      // Mark graph as needing refresh
      sessionStorage.setItem('graphNeedsRefresh', 'true');
      
      // Reset form
      setRelationshipForm({
        id: '',
        source_id: '',
        target_id: '',
        strength: undefined,
      });

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

            <div className="form-group">
              <label htmlFor="node-id">
                Node ID <span className="required">*</span>
              </label>
              <input
                id="node-id"
                type="text"
                value={nodeForm.id}
                onChange={(e) => setNodeForm({ ...nodeForm, id: e.target.value.toUpperCase() })}
                placeholder={nodeForm.type === 'company' ? 'e.g., TSLA (NASDAQ)' : 'e.g., node-1'}
                required
                disabled={loading}
                style={{ textTransform: 'uppercase' }}
              />
              <small>
                {nodeForm.type === 'company' 
                  ? 'Unique identifier (e.g., NASDAQ stock symbol like TSLA)' 
                  : 'Unique identifier for the node'}
              </small>
            </div>

            <div className="form-group">
              <label htmlFor="node-label">
                Name <span className="required">*</span>
              </label>
              <input
                id="node-label"
                type="text"
                value={nodeForm.label}
                onChange={(e) => setNodeForm({ ...nodeForm, label: e.target.value })}
                placeholder={nodeForm.type === 'company' ? 'e.g., Tesla, Inc.' : 'e.g., Node Name'}
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="node-description">
                Description <span className="required">*</span>
              </label>
              <textarea
                id="node-description"
                value={nodeForm.description}
                onChange={(e) => setNodeForm({ ...nodeForm, description: e.target.value })}
                placeholder={`Describe the ${nodeForm.type}...`}
                rows={4}
                required
                disabled={loading}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="node-sector">Sector</label>
                <select
                  id="node-sector"
                  value={nodeForm.sector || ''}
                  onChange={(e) => {
                    const { value } = e.target;
                    setNodeForm({ ...nodeForm, sector: value || undefined });
                  }}
                  disabled={loading}
                >
                  <option value="">Select a sector</option>
                  {SECTOR_OPTIONS.map((option) => (
                    <option key={option.value} value={option.label}>
                      {option.label}
                    </option>
                  ))}
                </select>
                <small>Choose from predefined sectors</small>
              </div>

              <div className="form-group">
                <label htmlFor="node-color">Color (Hex)</label>
                <input
                  id="node-color"
                  type="text"
                  value={nodeForm.color}
                  onChange={(e) => setNodeForm({ ...nodeForm, color: e.target.value })}
                  placeholder="e.g., #667eea"
                  disabled={loading}
                />
              </div>
            </div>

            <button type="submit" className="submit-button" disabled={loading}>
              {loading ? 'Creating...' : `Create ${getNodeTypeLabel(nodeForm.type ?? defaultNodeType)}`}
            </button>
          </form>
        )}

        {activeTab === 'relationship' && (
          <form className="data-form" onSubmit={handleRelationshipSubmit}>
            <div className="form-group">
              <label htmlFor="relationship-id">
                Relationship ID <span className="required">*</span>
              </label>
              <input
                id="relationship-id"
                type="text"
                value={relationshipForm.id}
                onChange={(e) => setRelationshipForm({ ...relationshipForm, id: e.target.value })}
                placeholder="e.g., edge-company1-company2"
                required
                disabled={loading}
              />
              <small>Unique identifier for the relationship</small>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="source-id">
                  Source Node ID <span className="required">*</span>
                </label>
                <input
                  id="source-id"
                  type="text"
                  value={relationshipForm.source_id}
                  onChange={(e) => setRelationshipForm({ ...relationshipForm, source_id: e.target.value.toUpperCase() })}
                  placeholder="e.g., TSLA or node-1"
                  required
                  disabled={loading}
                  style={{ textTransform: 'uppercase' }}
                />
              </div>

              <div className="form-group">
                <label htmlFor="target-id">
                  Target Node ID <span className="required">*</span>
                </label>
                <input
                  id="target-id"
                  type="text"
                  value={relationshipForm.target_id}
                  onChange={(e) => setRelationshipForm({ ...relationshipForm, target_id: e.target.value.toUpperCase() })}
                  placeholder="e.g., AAPL or node-2"
                  required
                  disabled={loading}
                  style={{ textTransform: 'uppercase' }}
                />
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

            <button type="submit" className="submit-button" disabled={loading}>
              {loading ? 'Creating...' : 'Create Relationship'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

