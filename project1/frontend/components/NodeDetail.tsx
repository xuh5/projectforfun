'use client';

import { useEffect } from 'react';
import './NodeDetail.css';

interface NodeDetailProps {
  node: {
    id: string;
    data: {
      label: string;
      description?: string;
      [key: string]: any;
    };
  } | null;
  onClose: () => void;
}

export default function NodeDetail({ node, onClose }: NodeDetailProps) {
  useEffect(() => {
    if (node) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [node]);

  if (!node) return null;

  return (
    <div className="node-detail-overlay" onClick={onClose}>
      <div className="node-detail-content" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>×</button>
        <div className="node-detail-header">
          <h2>{node.data.label}</h2>
          <span className="node-id">ID: {node.id}</span>
        </div>
        <div className="node-detail-body">
          {node.data.description && (
            <p className="description">{node.data.description}</p>
          )}
          <div className="node-detail-info">
            <h3>Node Information</h3>
            <ul>
              {Object.entries(node.data).map(([key, value]) => {
                if (key === 'label' || key === 'description') return null;
                return (
                  <li key={key}>
                    <strong>{key}:</strong> {String(value)}
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}


