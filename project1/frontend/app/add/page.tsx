'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { createCompany, createRelationship, type CreateCompanyRequest, type CreateRelationshipRequest } from '../../lib/api';

type TabType = 'company' | 'relationship';

export default function AddDataPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<TabType>('company');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Company form state
  const [companyForm, setCompanyForm] = useState<CreateCompanyRequest>({
    id: '',
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

  const handleCompanySubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // Clean up empty fields
      const data: CreateCompanyRequest = {
        id: companyForm.id.trim(),
        label: companyForm.label.trim(),
        description: companyForm.description.trim(),
        ...(companyForm.sector?.trim() && { sector: companyForm.sector.trim() }),
        ...(companyForm.color?.trim() && { color: companyForm.color.trim() }),
        ...(Object.keys(companyForm.metadata || {}).length > 0 && { metadata: companyForm.metadata }),
      };

      await createCompany(data);
      setSuccess(`Company "${data.label}" created successfully!`);
      
      // Mark graph as needing refresh
      sessionStorage.setItem('graphNeedsRefresh', 'true');
      
      // Reset form
      setCompanyForm({
        id: '',
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
      setError(err instanceof Error ? err.message : 'Failed to create company');
    } finally {
      setLoading(false);
    }
  };

  const handleRelationshipSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const data: CreateRelationshipRequest = {
        id: relationshipForm.id.trim(),
        source_id: relationshipForm.source_id.trim(),
        target_id: relationshipForm.target_id.trim(),
        ...(relationshipForm.strength !== undefined && relationshipForm.strength !== null && { strength: relationshipForm.strength }),
      };

      await createRelationship(data);
      setSuccess(`Relationship "${data.id}" created successfully!`);
      
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
      setError(err instanceof Error ? err.message : 'Failed to create relationship');
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
            className={`tab ${activeTab === 'company' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('company');
              setError(null);
              setSuccess(null);
            }}
            type="button"
          >
            Add Company
          </button>
          <button
            className={`tab ${activeTab === 'relationship' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('relationship');
              setError(null);
              setSuccess(null);
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

        {success && (
          <div className="success-message" role="status">
            {success}
          </div>
        )}

        {activeTab === 'company' && (
          <form className="data-form" onSubmit={handleCompanySubmit}>
            <div className="form-group">
              <label htmlFor="company-id">
                Company ID <span className="required">*</span>
              </label>
              <input
                id="company-id"
                type="text"
                value={companyForm.id}
                onChange={(e) => setCompanyForm({ ...companyForm, id: e.target.value })}
                placeholder="e.g., company-1"
                required
                disabled={loading}
              />
              <small>Unique identifier for the company</small>
            </div>

            <div className="form-group">
              <label htmlFor="company-label">
                Company Name <span className="required">*</span>
              </label>
              <input
                id="company-label"
                type="text"
                value={companyForm.label}
                onChange={(e) => setCompanyForm({ ...companyForm, label: e.target.value })}
                placeholder="e.g., Acme Corporation"
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="company-description">
                Description <span className="required">*</span>
              </label>
              <textarea
                id="company-description"
                value={companyForm.description}
                onChange={(e) => setCompanyForm({ ...companyForm, description: e.target.value })}
                placeholder="Describe the company..."
                rows={4}
                required
                disabled={loading}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="company-sector">Sector</label>
                <input
                  id="company-sector"
                  type="text"
                  value={companyForm.sector}
                  onChange={(e) => setCompanyForm({ ...companyForm, sector: e.target.value })}
                  placeholder="e.g., Technology"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="company-color">Color (Hex)</label>
                <input
                  id="company-color"
                  type="text"
                  value={companyForm.color}
                  onChange={(e) => setCompanyForm({ ...companyForm, color: e.target.value })}
                  placeholder="e.g., #667eea"
                  disabled={loading}
                />
              </div>
            </div>

            <button type="submit" className="submit-button" disabled={loading}>
              {loading ? 'Creating...' : 'Create Company'}
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
                  Source Company ID <span className="required">*</span>
                </label>
                <input
                  id="source-id"
                  type="text"
                  value={relationshipForm.source_id}
                  onChange={(e) => setRelationshipForm({ ...relationshipForm, source_id: e.target.value })}
                  placeholder="e.g., company-1"
                  required
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="target-id">
                  Target Company ID <span className="required">*</span>
                </label>
                <input
                  id="target-id"
                  type="text"
                  value={relationshipForm.target_id}
                  onChange={(e) => setRelationshipForm({ ...relationshipForm, target_id: e.target.value })}
                  placeholder="e.g., company-2"
                  required
                  disabled={loading}
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

