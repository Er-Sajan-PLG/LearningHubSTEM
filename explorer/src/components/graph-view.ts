import ForceGraph3D from '3d-force-graph';
import * as THREE from 'three';
import { forceX, forceY, forceZ } from 'd3-force-3d';
import { GraphProjection, GraphNode } from '../services/graph-projection';
import { GRAPH_THEME } from '../styles/theme';

export interface GraphViewOptions {
  container: HTMLElement;
  onNodeSelect: (nodeId: string | null) => void;
  onClusterSelect?: (clusterId: string | null) => void;
}

// Shape per entity type: quantity=sphere, law=octahedron, equation=box,
// concept=icosahedron, unit=m-small sphere.
const NODE_GEOMETRY_BY_TYPE: Record<string, (() => THREE.BufferGeometry) | undefined> = {
  law: () => new THREE.OctahedronGeometry(1, 0),
  equation: () => new THREE.BoxGeometry(1, 1, 1),
  quantity: () => new THREE.SphereGeometry(1, 24, 24),
  concept: () => new THREE.IcosahedronGeometry(1, 1),
  unit: () => new THREE.SphereGeometry(1, 20, 20),
};
const _geomCache = new Map<string, THREE.BufferGeometry>();
function geometryFor(type: string): THREE.BufferGeometry {
  if (!_geomCache.has(type || '')) {
    const maker = NODE_GEOMETRY_BY_TYPE[type || ''] || NODE_GEOMETRY_BY_TYPE.quantity!;
    _geomCache.set(type || '', maker());
  }
  return _geomCache.get(type || '')!;
}

// A persistent, always-visible sprite label so users can orient in 3D without
// hovering. Hubs (high degree) get larger labels.
function makeLabelSprite(node: GraphNode): THREE.Sprite {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d')!;
  const fontSize = 42;
  canvas.width = 700;
  canvas.height = 180;
  ctx.font = `${fontSize}px Inter, sans-serif`;
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'center';
  const label = `${node.name}`;
  // faint pill background
  const w = ctx.measureText(label).width + 60;
  const h = 90;
  ctx.fillStyle = 'rgba(6, 10, 22, 0.55)';
  ctx.beginPath();
  ctx.roundRect((canvas.width - w) / 2, (canvas.height - h) / 2, w, h, 40);
  ctx.fill();
  ctx.fillStyle = '#ffffff';
  ctx.shadowColor = node.color;
  ctx.shadowBlur = 18;
  ctx.fillText(label, canvas.width / 2, canvas.height / 2);
  const texture = new THREE.CanvasTexture(canvas);
  const material = new THREE.SpriteMaterial({ map: texture, transparent: true, depthWrite: false });
  const sprite = new THREE.Sprite(material);
  sprite.scale.set(9, 2.3, 1);
  sprite.position.y = 1.6;
  return sprite;
}

export class GraphView {
  private graph: any;
  private container: HTMLElement;
  private onNodeSelect: (nodeId: string | null) => void;
  private onClusterSelect?: (clusterId: string | null) => void;
  private currentProjection: GraphProjection | null = null;
  private selectedNodeId: string | null = null;
  private hoveredNodeId: string | null = null;
  private isAutoRotating: boolean = false;
  private clusterAnchors = new Map<string, { x: number; y: number; z: number }>();
  private spriteLayer: THREE.Group = new THREE.Group();

  constructor(options: GraphViewOptions) {
    this.container = options.container;
    this.onNodeSelect = options.onNodeSelect;
    this.onClusterSelect = options.onClusterSelect;
    this.initGraph();
    this.attachResizeListener();
  }

  private initGraph(): void {
    const Factory = (ForceGraph3D as any).default || ForceGraph3D;
    const width = this.container.clientWidth || Math.floor(window.innerWidth * 0.75);
    const height = this.container.clientHeight || (window.innerHeight - 61);

    this.graph = Factory()(this.container)
      .width(width)
      .height(height)
      .backgroundColor(GRAPH_THEME.canvas.background)
      .nodeId('id')
      .nodeLabel((node: any) => `
        <div style="background:rgba(15,23,42,0.95);backdrop-filter:blur(8px);padding:8px 14px;border-radius:10px;border:1px solid ${node.color}55;color:#fff;font-family:'Inter',sans-serif;font-size:0.85rem;box-shadow:0 10px 25px rgba(0,0,0,0.6);max-width:300px;">
          <div style="font-weight:800;color:#fff;font-size:0.95rem;font-family:'Outfit',sans-serif;">${node.name}</div>
          <div style="display:flex;align-items:center;gap:6px;margin-top:2px;">
            <span style="color:${node.color};font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">${node.domain}</span>
            <span style="color:#94a3b8;font-size:0.72rem;">· ${node.type}</span>
          </div>
          ${node.clusterLabel ? `<div style="color:#64748b;font-size:0.7rem;margin-top:2px;">${node.clusterLabel}</div>` : ''}
        </div>
      `)
      .nodeColor((node: any) => {
        if (this.selectedNodeId && node.id !== this.selectedNodeId) {
          const isConnected = this.currentProjection?.links.some(
            l => (l.source === this.selectedNodeId && l.target === node.id) ||
                 (l.target === this.selectedNodeId && l.source === node.id)
          );
          return isConnected ? node.color : '#334155';
        }
        return node.color;
      })
      .nodeVal((node: any) => node.val)
      .nodeThreeObject((node: any) => {
        const geo = geometryFor(node.type);
        const mat = new THREE.MeshStandardMaterial({
          color: node.color,
          emissive: node.color,
          emissiveIntensity: this.selectedNodeId === node.id ? 0.8 : 0.18,
          roughness: 0.3,
          metalness: 0.5,
        });
        const mesh = new THREE.Mesh(geo, mat);
        const s = node.val / 6.5;
        mesh.scale.set(s, s, s);

        // persistent sprite label
        const sprite = makeLabelSprite(node);
        const group = new THREE.Group();
        group.add(mesh);
        group.add(sprite);
        return group;
      })
      .nodeThreeObjectExtend(true)
      .linkColor((link: any) => {
        if (this.selectedNodeId) {
          const isConnected = link.source === this.selectedNodeId || link.target === this.selectedNodeId;
          return isConnected ? link.color : 'rgba(51, 65, 85, 0.2)';
        }
        return link.color;
      })
      .linkWidth((link: any) => {
        if (this.selectedNodeId) {
          const isConnected = link.source === this.selectedNodeId || link.target === this.selectedNodeId;
          return isConnected ? link.width * 1.6 : 0.6;
        }
        return link.width;
      })
      .linkOpacity((link: any) => {
        if (this.selectedNodeId) {
          const isConnected = link.source === this.selectedNodeId || link.target === this.selectedNodeId;
          return isConnected ? 1 : 0.06;
        }
        return 0.55;
      })
      .linkDirectionalParticles((link: any) => link.directional ? 2 : 0)
      .linkDirectionalParticleSpeed((link: any) => link.particleSpeed || 0.005)
      .linkDirectionalParticleWidth(2.5)
      .linkDirectionalArrowLength((link: any) => link.directional ? 4 : 0)
      .linkDirectionalArrowRelPos(0.9)
      .linkCurvature('curvature')
      .onNodeHover((node: any) => { this.hoveredNodeId = node ? node.id : null; })
      .onNodeClick((node: any) => {
        if (node && node.id) { this.onNodeSelect(node.id); this.focusOnNode(node); }
      })
      .onBackgroundClick(() => {
        this.onNodeSelect(null);
        if (this.onClusterSelect) this.onClusterSelect(null);
      });

    if (this.graph.d3Force) {
      this.graph.d3Force('charge').strength(-90);
      this.graph.d3Force('link').distance(60);
    }
  }

  private applyClusterForces(): void {
    if (!this.graph || !this.currentProjection) return;
    // Gently pull each node toward its seeded cluster coordinate so grouped
    // regions hold their shape instead of collapsing into a single blob. The
    // seed positions were computed in graph-projection.ts per domain/topic.
    const get = (d: any, key: string) => (d && typeof d[key] === 'number' ? d[key] : 0);
    this.graph.d3Force('clusterX', forceX().x((d: any) => get(d, 'seedX')).strength(0.06));
    this.graph.d3Force('clusterY', forceY().y((d: any) => get(d, 'seedY')).strength(0.06));
    this.graph.d3Force('clusterZ', forceZ().z((d: any) => get(d, 'seedZ')).strength(0.06));
  }

  private attachResizeListener(): void {
    window.addEventListener('resize', () => {
      if (this.graph && this.container) {
        const w = this.container.clientWidth || Math.floor(window.innerWidth * 0.75);
        const h = this.container.clientHeight || (window.innerHeight - 61);
        this.graph.width(w).height(h);
      }
    });
  }

  public updateProjection(projection: GraphProjection, selectedId: string | null): void {
    this.currentProjection = projection;
    this.selectedNodeId = selectedId;
    this.clusterAnchors.clear();
    for (const cluster of projection.clusters) {
      this.clusterAnchors.set(cluster.id, { x: cluster.anchorX, y: cluster.anchorY, z: cluster.anchorZ });
    }
    const dataNodes = projection.nodes.map(n => ({ ...n, x: n.seedX, y: n.seedY, z: n.seedZ }));
    this.graph.graphData({ nodes: dataNodes, links: projection.links.map(l => ({ ...l })) });
    this.applyClusterForces();
    if (selectedId) {
      const node = projection.nodes.find(n => n.id === selectedId);
      if (node) setTimeout(() => this.focusOnNode(node), 250);
    }
  }

  public focusOnNode(node: GraphNode): void {
    const distance = 70;
    const nodes = this.graph.graphData().nodes;
    const graphNode = nodes.find((n: any) => n.id === node.id);
    if (!graphNode) return;
    const x = graphNode.x || 0, y = graphNode.y || 0, z = graphNode.z || 0;
    const distRatio = 1 + distance / (Math.hypot(x, y, z) || 1);
    this.graph.cameraPosition(
      { x: x * distRatio, y: y * distRatio, z: z * distRatio },
      { x, y, z },
      1400
    );
  }

  public focusOnCluster(clusterId: string): void {
    const anchor = this.clusterAnchors.get(clusterId);
    if (!anchor) return;
    this.graph.cameraPosition(
      { x: anchor.x * 2, y: anchor.y * 2, z: anchor.z * 2 },
      { x: anchor.x, y: anchor.y, z: anchor.z },
      1600
    );
  }

  public toggleAutoRotate(): boolean {
    this.isAutoRotating = !this.isAutoRotating;
    const controls = this.graph.controls();
    if (controls) { controls.autoRotate = this.isAutoRotating; controls.autoRotateSpeed = 0.8; }
    return this.isAutoRotating;
  }
  public zoomIn(): void {
    const cam = this.graph.cameraPosition();
    this.graph.cameraPosition({ x: cam.x * 0.8, y: cam.y * 0.8, z: cam.z * 0.8 });
  }
  public zoomOut(): void {
    const cam = this.graph.cameraPosition();
    this.graph.cameraPosition({ x: cam.x * 1.25, y: cam.y * 1.25, z: cam.z * 1.25 });
  }
  public resetView(): void {
    this.graph.zoomToFit(1000, 60);
  }
}