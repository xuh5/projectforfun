'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useThree, useFrame } from '@react-three/fiber';
import { Line, OrbitControls, Text, Billboard } from '@react-three/drei';
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib';
import { Vector3, type Mesh } from 'three';
import './GraphCanvas.css';

import type { GraphNode, GraphEdge } from '../lib/types';
import {
  NODE_CONFIG,
  NODE_MATERIAL,
  NODE_HOVER,
  NODE_LABEL,
  EDGE_CONFIG,
  CAMERA_CONFIG,
  FOCUS_CAMERA,
  LIGHTING_CONFIG,
  ORBIT_CONTROLS,
} from '../lib/graphConfig';

export type { GraphNode, GraphEdge } from '../lib/types';

interface GraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeClick?: (nodeId: string) => void;
  focusNodeId?: string | null;
}

function GraphNodeMesh({ node, onClick }: { node: GraphNode; onClick?: (nodeId: string) => void }) {
  const [hovered, setHovered] = useState(false);
  const meshRef = useRef<Mesh>(null);
  const targetScaleRef = useRef(1.0);

  // Update target scale when hover state changes
  useEffect(() => {
    targetScaleRef.current = hovered ? NODE_HOVER.scaleMultiplier : 1.0;
  }, [hovered]);

  // Animate scale on hover
  useFrame(() => {
    if (meshRef.current) {
      const currentScale = meshRef.current.scale.x;
      const targetScale = targetScaleRef.current;
      const newScale = currentScale + (targetScale - currentScale) * NODE_HOVER.animationSpeed;
      meshRef.current.scale.set(newScale, newScale, newScale);
    }
  });

  const handleClick = useCallback(() => {
    onClick?.(node.id);
  }, [node.id, onClick]);

  const handlePointerEnter = useCallback(() => {
    setHovered(true);
  }, []);

  const handlePointerLeave = useCallback(() => {
    setHovered(false);
  }, []);

  return (
    <group position={node.position}>
      <mesh
        ref={meshRef}
        onClick={handleClick}
        onPointerEnter={handlePointerEnter}
        onPointerLeave={handlePointerLeave}
        castShadow
      >
        <sphereGeometry args={[NODE_CONFIG.radius, ...NODE_CONFIG.geometrySegments]} />
        <meshStandardMaterial
          color={node.color ?? NODE_CONFIG.defaultColor}
          emissive={node.color ?? NODE_CONFIG.defaultColor}
          emissiveIntensity={hovered ? NODE_MATERIAL.emissiveIntensity.hovered : NODE_MATERIAL.emissiveIntensity.default}
          roughness={NODE_MATERIAL.roughness}
          metalness={NODE_MATERIAL.metalness}
        />
      </mesh>
      <Billboard position={NODE_LABEL.positionOffset} follow>
        <Text
          fontSize={NODE_LABEL.fontSize}
          color={NODE_LABEL.color}
          anchorX={NODE_LABEL.textAlign}
          anchorY="bottom"
          outlineWidth={NODE_LABEL.outlineWidth}
          outlineColor={NODE_LABEL.outlineColor}
          maxWidth={NODE_LABEL.maxWidth}
          lineHeight={NODE_LABEL.lineHeight}
          textAlign={NODE_LABEL.textAlign}
          depthOffset={NODE_LABEL.depthOffset}
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
      color={EDGE_CONFIG.color}
      lineWidth={EDGE_CONFIG.lineWidth}
      transparent
      opacity={EDGE_CONFIG.opacity}
      depthWrite={EDGE_CONFIG.depthWrite}
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

      const distance = Math.max(radius * CAMERA_CONFIG.fitDistanceMultiplier, CAMERA_CONFIG.minDistance);
      const newPosition = new Vector3().copy(currentDirection).multiplyScalar(distance).add(target);

      camera.position.copy(newPosition);
      camera.near = Math.max(distance / CAMERA_CONFIG.nearPlaneRatio, CAMERA_CONFIG.minNearPlane);
      camera.far = Math.max(distance * CAMERA_CONFIG.farPlaneRatio, CAMERA_CONFIG.minFarPlane);
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

      const distance = Math.max((radiusHint ?? FOCUS_CAMERA.minDistance) * FOCUS_CAMERA.distanceMultiplier, FOCUS_CAMERA.minDistance);
      const newPosition = new Vector3()
        .copy(direction)
        .multiplyScalar(distance)
        .add(target);

      camera.position.copy(newPosition);
      camera.near = Math.max(distance / FOCUS_CAMERA.nearPlaneRatio, CAMERA_CONFIG.minNearPlane);
      camera.far = Math.max(distance * CAMERA_CONFIG.farPlaneRatio, CAMERA_CONFIG.minFarPlane);
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
      <Canvas camera={{ position: CAMERA_CONFIG.initialPosition, fov: CAMERA_CONFIG.fov }}>
        <color attach="background" args={[LIGHTING_CONFIG.backgroundColor]} />
        <ambientLight intensity={LIGHTING_CONFIG.ambientIntensity} />
        <directionalLight position={LIGHTING_CONFIG.primaryDirectionalLight.position} intensity={LIGHTING_CONFIG.primaryDirectionalLight.intensity} />
        <directionalLight position={LIGHTING_CONFIG.secondaryDirectionalLight.position} intensity={LIGHTING_CONFIG.secondaryDirectionalLight.intensity} />
        <pointLight position={LIGHTING_CONFIG.pointLight.position} intensity={LIGHTING_CONFIG.pointLight.intensity} />

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
          enableDamping={ORBIT_CONTROLS.enableDamping}
          dampingFactor={ORBIT_CONTROLS.dampingFactor}
          rotateSpeed={ORBIT_CONTROLS.rotateSpeed}
        />
      </Canvas>
    </div>
  );
}

