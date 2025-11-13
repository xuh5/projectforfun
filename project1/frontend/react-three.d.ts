/// <reference types="@react-three/fiber" />
/// <reference types="three" />
declare module 'd3-force-3d' {
  import {
    Force,
    ForceCenter,
    ForceCollide,
    ForceLink,
    ForceManyBody,
    ForceX,
    ForceY,
    Simulation,
    SimulationLinkDatum,
    SimulationNodeDatum
  } from 'd3-force';

  export * from 'd3-force';

  export function forceSimulation<
    NodeDatum extends SimulationNodeDatum,
    LinkDatum extends SimulationLinkDatum<NodeDatum> = SimulationLinkDatum<NodeDatum>
  >(nodes?: readonly NodeDatum[], alpha?: number): Simulation<NodeDatum, LinkDatum>;

  export function forceLink<
    NodeDatum extends SimulationNodeDatum,
    LinkDatum extends SimulationLinkDatum<NodeDatum> = SimulationLinkDatum<NodeDatum>
  >(links?: readonly LinkDatum[]): ForceLink<NodeDatum, LinkDatum>;

  export function forceCenter<NodeDatum extends SimulationNodeDatum>(
    x?: number,
    y?: number,
    z?: number
  ): ForceCenter<NodeDatum>;

  export function forceManyBody<NodeDatum extends SimulationNodeDatum>(): ForceManyBody<NodeDatum>;

  export function forceCollide<NodeDatum extends SimulationNodeDatum>(
    radius?: number | ((node: NodeDatum, i: number, nodes: NodeDatum[]) => number)
  ): ForceCollide<NodeDatum>;

  export function forceX<NodeDatum extends SimulationNodeDatum>(
    x?: number | ((node: NodeDatum, i?: number, nodes?: NodeDatum[]) => number)
  ): ForceX<NodeDatum>;

  export function forceY<NodeDatum extends SimulationNodeDatum>(
    y?: number | ((node: NodeDatum, i?: number, nodes?: NodeDatum[]) => number)
  ): ForceY<NodeDatum>;

  export function forceZ<NodeDatum extends SimulationNodeDatum>(
    z?: number | ((node: NodeDatum, i?: number, nodes?: NodeDatum[]) => number)
  ): Force<NodeDatum, undefined>;
}


