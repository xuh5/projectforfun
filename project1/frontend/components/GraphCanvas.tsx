'use client';

import { useCallback, useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { Line, OrbitControls } from '@react-three/drei';
import './GraphCanvas.css';

export interface GraphNode {
  id: string;
  position: [number, number, number];
  color?: string;
  data?: {
    label: string;
    description?: string;
    [key: string]: unknown;
  };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
}

interface GraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeClick?: (nodeId: string) => void;
}

function GraphNodeMesh({ node, onClick }: { node: GraphNode; onClick?: (nodeId: string) => void }) {
  const handleClick = useCallback(() => {
    onClick?.(node.id);
  }, [node.id, onClick]);

  return (
    <mesh position={node.position} onClick={handleClick} castShadow>
      <sphereGeometry args={[0.25, 32, 32]} />
      <meshStandardMaterial
        color={node.color ?? '#667eea'}
        emissive={node.color ?? '#667eea'}
        emissiveIntensity={0.25}
        roughness={0.35}
        metalness={0.25}
      />
    </mesh>
  );
}

function GraphEdgeLine({
  start,
  end,
}: {
  start: [number, number, number];
  end: [number, number, number];
}) {
  return (
    <Line
      points={[start, end]}
      color="#9ca3af"
      lineWidth={1.5}
      transparent
      opacity={0.35}
      depthWrite={false}
    />
  );
}

export default function GraphCanvas({ nodes, edges, onNodeClick }: GraphCanvasProps) {
  const nodePositionMap = useMemo(() => {
    const map = new Map<string, [number, number, number]>();
    nodes.forEach((node) => {
      map.set(node.id, node.position);
    });
    return map;
  }, [nodes]);

  const edgeLines = useMemo(
    () =>
      edges.reduce<JSX.Element[]>((acc, edge) => {
        const start = nodePositionMap.get(edge.source);
        const end = nodePositionMap.get(edge.target);
        if (!start || !end) return acc;
        acc.push(<GraphEdgeLine key={edge.id} start={start} end={end} />);
        return acc;
      }, []),
    [edges, nodePositionMap]
  );

  return (
    <div className="graph-container">
      <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
        <color attach="background" args={['#05060d']} />
        <ambientLight intensity={0.6} />
        <directionalLight position={[5, 8, 5]} intensity={0.8} />
        <directionalLight position={[-6, -4, -5]} intensity={0.35} />
        <pointLight position={[0, 0, 0]} intensity={0.2} />

        {edgeLines}

        {nodes.map((node) => (
          <GraphNodeMesh key={node.id} node={node} onClick={onNodeClick} />
        ))}

        <OrbitControls enableDamping dampingFactor={0.08} rotateSpeed={0.6} />
      </Canvas>
    </div>
  );
}

