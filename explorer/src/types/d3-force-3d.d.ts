// Minimal type declarations for d3-force-3d (used for graph cluster forces).
declare module 'd3-force-3d' {
  export interface ForceSimulation3D<Datum> {
    (nodes: Datum[]): ForceSimulation3D<Datum>;
    nodes(nodes: Datum[]): ForceSimulation3D<Datum>;
    force(name: string, force: any): ForceSimulation3D<Datum>;
    stop(): ForceSimulation3D<Datum>;
    tick(): ForceSimulation3D<Datum>;
  }
  export interface ForceX3D<Datum> {
    (alpha: number): void;
    x(x: ((d: Datum) => number) | number): ForceX3D<Datum>;
    strength(strength: number | ((d: Datum) => number)): ForceX3D<Datum>;
  }
  export interface ForceY3D<Datum> extends ForceX3D<Datum> { y: ForceX3D<Datum>['x']; }
  export interface ForceZ3D<Datum> extends ForceX3D<Datum> { z: ForceX3D<Datum>['x']; }
  export function forceX<Datum = any>(x?: number): ForceX3D<Datum>;
  export function forceY<Datum = any>(y?: number): ForceY3D<Datum>;
  export function forceZ<Datum = any>(z?: number): ForceZ3D<Datum>;
}