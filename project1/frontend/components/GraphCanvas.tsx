'use client';

import { useCallback, useEffect, useMemo, useRef } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { Line, OrbitControls, Text, Billboard } from '@react-three/drei';
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib';
import { Vector3 } from 'three';
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
  strength?: number;
}

interface GraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeClick?: (nodeId: string) => void;
  focusNodeId?: string | null;
}

function GraphNodeMesh({ node, onClick }: { node: GraphNode; onClick?: (nodeId: string) => void }) {
  const handleClick = useCallback(() => {
    onClick?.(node.id);
  }, [node.id, onClick]);

  return (
    <group position={node.position}>
      <mesh onClick={handleClick} castShadow>
        <sphereGeometry args={[0.4, 32, 32]} />
        <meshStandardMaterial
          color={node.color ?? '#667eea'}
          emissive={node.color ?? '#667eea'}
          emissiveIntensity={0.25}
          roughness={0.35}
          metalness={0.25}
        />
      </mesh>
      <Billboard position={[0, 0.75, 0]} follow>
        <Text
          fontSize={0.3}
          color="#f8fafc"
          anchorX="center"
          anchorY="bottom"
          outlineWidth={0.015}
          outlineColor="rgba(0, 0, 0, 0.75)"
          maxWidth={2.5}
          lineHeight={1.1}
          textAlign="center"
          depthOffset={-1}
        >
          {typeof node.data?.label === 'string' ? node.data.label : node.id}
        </Text>
      </Billboard>
    </group>
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

export default function GraphCanvas({ nodes, edges, onNodeClick, focusNodeId }: GraphCanvasProps) {
  const layoutBounds = useMemo(() => {
    if (!nodes.length) {
      return null;
    }

    let minX = Infinity;
    let minY = Infinity;
    let minZ = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;
    let maxZ = -Infinity;

    nodes.forEach((node) => {
      const [x, y, z] = node.position;
      if (x < minX) minX = x;
      if (y < minY) minY = y;
      if (z < minZ) minZ = z;
      if (x > maxX) maxX = x;
      if (y > maxY) maxY = y;
      if (z > maxZ) maxZ = z;
    });

    const center: [number, number, number] = [
      (minX + maxX) / 2,
      (minY + maxY) / 2,
      (minZ + maxZ) / 2,
    ];

    const spanX = maxX - minX;
    const spanY = maxY - minY;
    const spanZ = maxZ - minZ;
    const radius = Math.max(spanX, spanY, spanZ) / 2 || 1;

    return { center, radius };
  }, [nodes]);

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

  const controlsRef = useRef<OrbitControlsImpl | null>(null);

  const focusNode = useMemo(() => {
    if (!focusNodeId) return null;
    return nodes.find((node) => node.id === focusNodeId) ?? null;
  }, [focusNodeId, nodes]);

  function FitCamera({
    center,
    radius,
  }: {
    center: [number, number, number];
    radius: number;
  }) {
    const { camera } = useThree();

    useEffect(() => {
      if (!center || radius <= 0) return;

      const target = new Vector3(...center);
      const currentDirection = new Vector3()
        .subVectors(camera.position.clone(), target)
        .normalize();

      if (!Number.isFinite(currentDirection.length()) || currentDirection.length() === 0) {
        currentDirection.set(0, 0, 1);
      }

      const distance = Math.max(radius * 2.5, 6);
      const newPosition = new Vector3().copy(currentDirection).multiplyScalar(distance).add(target);

      camera.position.copy(newPosition);
      camera.near = Math.max(distance / 100, 0.1);
      camera.far = Math.max(distance * 10, 50);
      camera.updateProjectionMatrix();
      camera.lookAt(target);

      if (controlsRef.current) {
        controlsRef.current.target.copy(target);
        controlsRef.current.update();
      }
    }, [camera, center, radius]);

    return null;
  }

  function FocusOnNode({
    node,
    radiusHint,
  }: {
    node: GraphNode;
    radiusHint?: number;
  }) {
    const { camera } = useThree();

    useEffect(() => {
      if (!node) return;

      const target = new Vector3(...node.position);
      const currentPosition = camera.position.clone();
      let direction = currentPosition.clone().sub(target);

      if (!Number.isFinite(direction.length()) || direction.length() === 0) {
        direction = new Vector3(0, 0, 1);
      } else {
        direction.normalize();
      }

      const distance = Math.max((radiusHint ?? 3) * 0.3, 3);
      const newPosition = new Vector3()
        .copy(direction)
        .multiplyScalar(distance)
        .add(target);

      camera.position.copy(newPosition);
      camera.near = Math.max(distance / 50, 0.1);
      camera.far = Math.max(distance * 10, 50);
      camera.updateProjectionMatrix();
      camera.lookAt(target);

      if (controlsRef.current) {
        controlsRef.current.target.copy(target);
        controlsRef.current.update();
      }
    }, [camera, node, radiusHint]);

    return null;
  }

  return (
    <div className="graph-container">
      <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
        <color attach="background" args={['#05060d']} />
        <ambientLight intensity={0.6} />
        <directionalLight position={[5, 8, 5]} intensity={0.8} />
        <directionalLight position={[-6, -4, -5]} intensity={0.35} />
        <pointLight position={[0, 0, 0]} intensity={0.2} />

        {layoutBounds && <FitCamera center={layoutBounds.center} radius={layoutBounds.radius} />}
        {focusNode && (
          <FocusOnNode node={focusNode} radiusHint={layoutBounds?.radius} />
        )}

        {edgeLines}

        {nodes.map((node) => (
          <GraphNodeMesh key={node.id} node={node} onClick={onNodeClick} />
        ))}

        <OrbitControls
          ref={controlsRef}
          enableDamping
          dampingFactor={0.08}
          rotateSpeed={0.6}
        />
      </Canvas>
    </div>
  );
}

