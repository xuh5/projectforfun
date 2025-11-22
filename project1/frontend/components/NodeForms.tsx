'use client';

import { useState } from 'react';
import { SketchPicker, ColorResult } from 'react-color';
import type { CreateNodeRequest } from '../lib/api';
import { SECTOR_OPTIONS } from '../lib/constants';

interface NodeFormProps {
  formData: CreateNodeRequest;
  onChange: (data: CreateNodeRequest) => void;
  loading: boolean;
  getNodeTypeLabel: (type: string) => string;
}

// Simple color picker component
function ColorPicker({ color, onChange, disabled }: { color?: string; onChange: (color: string) => void; disabled: boolean }) {
  const [show, setShow] = useState(false);
  return (
    <div style={{ position: 'relative' }}>
      <button
        type="button"
        onClick={() => setShow(!show)}
        disabled={disabled}
        style={{
          width: '100%',
          height: '40px',
          border: '1px solid rgba(226, 232, 240, 0.8)',
          borderRadius: '8px',
          backgroundColor: color || '#667eea',
          cursor: disabled ? 'not-allowed' : 'pointer',
        }}
      />
      {show && (
        <>
          <div style={{ position: 'fixed', inset: 0, zIndex: 999 }} onClick={() => setShow(false)} />
          <div style={{ position: 'absolute', zIndex: 1000, marginTop: '8px' }}>
            <SketchPicker color={color || '#667eea'} onChange={(c: ColorResult) => onChange(c.hex)} disableAlpha />
          </div>
        </>
      )}
    </div>
  );
}

export function CompanyNodeForm({ formData, onChange, loading, getNodeTypeLabel }: NodeFormProps) {

  return (
    <>
      <div className="form-group">
        <label htmlFor="node-id">
          Stock Symbol <span className="required">*</span>
        </label>
        <input
          id="node-id"
          type="text"
          value={formData.id}
          onChange={(e) => onChange({ ...formData, id: e.target.value.toUpperCase() })}
          placeholder="e.g., TSLA (NASDAQ)"
          required
          disabled={loading}
          style={{ textTransform: 'uppercase' }}
        />
        <small>Unique identifier (e.g., NASDAQ stock symbol like TSLA)</small>
      </div>

      <div className="form-group">
        <label htmlFor="node-description">
          Description <span className="required">*</span>
        </label>
        <textarea
          id="node-description"
          value={formData.description}
          onChange={(e) => onChange({ ...formData, description: e.target.value })}
          placeholder="Describe the company..."
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
            value={formData.sector || ''}
            onChange={(e) => {
              const { value } = e.target;
              onChange({ ...formData, sector: value || undefined });
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
          <label htmlFor="node-color">Color</label>
          <ColorPicker
            color={formData.color}
            onChange={(color) => onChange({ ...formData, color })}
            disabled={loading}
          />
          <small>Click to open color picker</small>
        </div>
      </div>
    </>
  );
}

export function GenericNodeForm({ formData, onChange, loading, getNodeTypeLabel }: NodeFormProps) {

  return (
    <>
      <div className="form-group">
        <label htmlFor="node-id">
          Node ID <span className="required">*</span>
        </label>
        <input
          id="node-id"
          type="text"
          value={formData.id}
          onChange={(e) => onChange({ ...formData, id: e.target.value })}
          placeholder="e.g., node-1"
          required
          disabled={loading}
        />
        <small>Unique identifier for the node</small>
      </div>

      <div className="form-group">
        <label htmlFor="node-label">
          Name <span className="required">*</span>
        </label>
        <input
          id="node-label"
          type="text"
          value={formData.label}
          onChange={(e) => onChange({ ...formData, label: e.target.value })}
          placeholder="e.g., Node Name"
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
          value={formData.description}
          onChange={(e) => onChange({ ...formData, description: e.target.value })}
          placeholder={`Describe the ${formData.type}...`}
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
            value={formData.sector || ''}
            onChange={(e) => {
              const { value } = e.target;
              onChange({ ...formData, sector: value || undefined });
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
          <label htmlFor="node-color">Color</label>
          <ColorPicker
            color={formData.color}
            onChange={(color) => onChange({ ...formData, color })}
            disabled={loading}
          />
          <small>Click to open color picker</small>
        </div>
      </div>
    </>
  );
}

