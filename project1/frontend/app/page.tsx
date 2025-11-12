'use client';

import { useEffect, useState } from 'react';
import { Edge, Node } from 'reactflow';
import GraphCanvas from '../components/GraphCanvas';

export default function Home() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGraphData();
  }, []);

  const fetchGraphData = async () => {
    try {
      const response = await fetch('/api/nodes');
      const data = await response.json();

      const apiNodes: Node[] = (data?.nodes || []).map((node: any) => ({
        id: node.id,
        type: 'default',
        position: {
          x: node.x ?? Math.random() * 800,
          y: node.y ?? Math.random() * 600,
        },
        data: {
          label: node.label || node.id,
          description: node.description,
          ...node.data,
        },
        style: {
          background: node.color || '#667eea',
          color: '#fff',
          border: '2px solid #fff',
          borderRadius: '50%',
          width: 80,
          height: 80,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '14px',
          fontWeight: 'bold',
        },
      }));

      const apiEdges: Edge[] = (data?.edges || []).map((edge: any) => ({
        id: edge.id || `${edge.source}-${edge.target}`,
        source: edge.source,
        target: edge.target,
        type: 'smoothstep',
        animated: true,
      }));

      if (!apiNodes.length || !apiEdges.length) {
        generateSampleData();
        return;
      }

      setNodes(apiNodes);
      setEdges(apiEdges);
    } catch (error) {
      console.error('Error fetching graph data:', error);
      // Fallback to sample data
      generateSampleData();
    } finally {
      setLoading(false);
    }
  };

  const generateSampleData = () => {
    // Generate sample nodes in a circular pattern
    const sampleNodes: Node[] = [];
    const sampleEdges: Edge[] = [];
    const nodeCount = 12;
    const radius = 300;
    const centerX = 400;
    const centerY = 300;

    for (let i = 0; i < nodeCount; i++) {
      const angle = (2 * Math.PI * i) / nodeCount;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);

      sampleNodes.push({
        id: `node-${i}`,
        type: 'default',
        position: { x, y },
        data: {
          label: `Node ${i + 1}`,
          description: `This is node number ${i + 1} in the graph network.`,
          value: Math.floor(Math.random() * 100),
          category: ['A', 'B', 'C'][i % 3],
        },
        style: {
          background: ['#667eea', '#764ba2', '#f093fb'][i % 3],
          color: '#fff',
          border: '2px solid #fff',
          borderRadius: '50%',
          width: 80,
          height: 80,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '14px',
          fontWeight: 'bold',
        },
      });

      // Create edges connecting to next node
      if (i < nodeCount - 1) {
        sampleEdges.push({
          id: `edge-${i}-${i + 1}`,
          source: `node-${i}`,
          target: `node-${i + 1}`,
          type: 'smoothstep',
          animated: true,
        });
      }
    }

    // Connect last node to first
    sampleEdges.push({
      id: `edge-${nodeCount - 1}-0`,
      source: `node-${nodeCount - 1}`,
      target: 'node-0',
      type: 'smoothstep',
      animated: true,
    });

    setNodes(sampleNodes);
    setEdges(sampleEdges);
  };

  if (loading) {
    return (
      <div className="page-wrapper">
        <div className="canvas-window">
          <span className="canvas-status">Loading graph…</span>
        </div>
      </div>
    );
  }

  return (
    <div className="page-wrapper">
      <div className="canvas-window">
        <GraphCanvas nodes={nodes} edges={edges} />
      </div>
    </div>
  );
}
