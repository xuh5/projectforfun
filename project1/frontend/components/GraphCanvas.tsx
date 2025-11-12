'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  Edge,
  Node,
  ReactFlowInstance,
  useEdgesState,
  useNodesState
} from 'reactflow';
import 'reactflow/dist/style.css';
import './GraphCanvas.css';

interface GraphCanvasProps {
  nodes: Node[];
  edges: Edge[];
  onNodeClick?: (nodeId: string) => void;
}

export default function GraphCanvas({ nodes: initialNodes, edges: initialEdges, onNodeClick }: GraphCanvasProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);
  const [isZooming, setIsZooming] = useState(false);
  const zoomTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastMousePosition = useRef<{ x: number; y: number } | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Update nodes and edges when props change
  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  const onInit = useCallback((instance: ReactFlowInstance) => {
    setReactFlowInstance(instance);
  }, []);

  const onNodeClickHandler = useCallback((event: React.MouseEvent, node: Node) => {
    if (!reactFlowInstance) return;

    // Get node position
    const nodePosition = node.position;
    const nodeWidth = node.width || 50;
    const nodeHeight = node.height || 50;

    // Calculate center of node in viewport coordinates
    const viewport = reactFlowInstance.getViewport();
    const nodeCenterX = (nodePosition.x + nodeWidth / 2) * viewport.zoom + viewport.x;
    const nodeCenterY = (nodePosition.y + nodeHeight / 2) * viewport.zoom + viewport.y;

    // Animate zoom to node with fast zoom-in animation
    setIsZooming(true);
    reactFlowInstance.setCenter(nodePosition.x + nodeWidth / 2, nodePosition.y + nodeHeight / 2, {
      zoom: 2.5,
      duration: 400,
    });

    // After animation, trigger detail view (if provided)
    setTimeout(() => {
      onNodeClick?.(node.id);
      setIsZooming(false);
    }, 400);
  }, [reactFlowInstance, onNodeClick]);

  const onMouseMove = useCallback((event: React.MouseEvent) => {
    if (!reactFlowInstance || isZooming) return;

    const reactFlowBounds = (event.currentTarget as HTMLElement).getBoundingClientRect();
    const mouseX = event.clientX - reactFlowBounds.left;
    const mouseY = event.clientY - reactFlowBounds.top;

    lastMousePosition.current = { x: mouseX, y: mouseY };

    // Cancel any pending animation frame
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }

    // Use requestAnimationFrame for smooth zoom
    animationFrameRef.current = requestAnimationFrame(() => {
      if (!reactFlowInstance || isZooming) return;

      const viewport = reactFlowInstance.getViewport();
      const currentZoom = viewport.zoom;

      // Only zoom if not already at max zoom
      if (currentZoom < 2.5) {
        // Convert mouse position to flow coordinates
        const flowPosition = reactFlowInstance.screenToFlowPosition({
          x: mouseX,
          y: mouseY,
        });

        // Calculate new zoom (smooth zoom in)
        const newZoom = Math.min(currentZoom + 0.005, 2.5);

        // Set zoom centered on mouse position
        reactFlowInstance.setCenter(flowPosition.x, flowPosition.y, {
          zoom: newZoom,
          duration: 50,
        });
      }
    });
  }, [reactFlowInstance, isZooming]);

  const onMouseLeave = useCallback(() => {
    if (zoomTimeoutRef.current) {
      clearTimeout(zoomTimeoutRef.current);
    }
    lastMousePosition.current = null;
  }, []);

  useEffect(() => {
    return () => {
      if (zoomTimeoutRef.current) {
        clearTimeout(zoomTimeoutRef.current);
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  return (
    <div className="graph-container" onMouseMove={onMouseMove} onMouseLeave={onMouseLeave}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onInit={onInit}
        onNodeClick={onNodeClickHandler}
        fitView
        minZoom={0.5}
        maxZoom={3}
        defaultViewport={{ x: 0, y: 0, zoom: 1 }}
        nodeTypes={{}}
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}

