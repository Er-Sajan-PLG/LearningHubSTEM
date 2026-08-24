import ForceGraph3D from '3d-force-graph';
import * as THREE from 'three';
import { GraphProjection, GraphNode } from '../services/graph-projection';
import { GRAPH_THEME } from '../styles/theme';

export interface GraphViewOptions {
  container: HTMLElement;
  onNodeSelect: (nodeId: string | null) => void;
}

export class GraphView {
  private graph: any;
  private container: HTMLElement;
  private onNodeSelect: (nodeId: string | null) => void;
  private currentProjection: GraphProjection | null = null;
  private selectedNodeId: string | null = null;
  private hoveredNodeId: string | null = null;
  private isAutoRotating: boolean = false;

  constructor(options: GraphViewOptions) {
    this.container = options.container;
    this.onNodeSelect = options.onNodeSelect;
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
        <div style="background:rgba(15, 23, 42, 0.95);backdrop-filter:blur(8px);padding:8px 14px;border-radius:10px;border:1px solid rgba(56, 189, 248, 0.4);color:#fff;font-family:'Inter',sans-serif;font-size:0.85rem;box-shadow:0 10px 25px rgba(0,0,0,0.6);">
          <strong style="color:#ffffff;font-size:0.95rem;font-family:'Outfit',sans-serif;">${node.name}</strong><br/>
          <span style="color:#38bdf8;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;">${node.domain}</span>
          <span style="color:#94a3b8;font-size:0.75rem;"> · ${node.type}</span>
        </div>
      `)
      .nodeColor((node: any) => {
        if (this.selectedNodeId && node.id !== this.selectedNodeId) {
          // Check if node is connected to selectedNodeId
          const isConnected = this.currentProjection?.links.some(
            l => (l.source === this.selectedNodeId && l.target === node.id) ||
                 (l.target === this.selectedNodeId && l.source === node.id)
          );
          return isConnected ? node.color : '#334155';
        }
        return node.color;
      })
      .nodeVal((node: any) => node.val)
      // Custom 3D Glowing Mesh Nodes
      .nodeThreeObject((node: any) => {
        const group = new THREE.Group();

        // Core Sphere Mesh with glowing material
        const size = Math.max(3, node.val);
        const geometry = new THREE.SphereGeometry(size, 24, 24);
        const material = new THREE.MeshStandardMaterial({
          color: node.color,
          emissive: node.color,
          emissiveIntensity: this.selectedNodeId === node.id ? 0.9 : 0.4,
          roughness: 0.2,
          metalness: 0.8
        });
        const mesh = new THREE.Mesh(geometry, material);
        group.add(mesh);

        // Outer Halo Ring for selected / high-degree nodes
        if (this.selectedNodeId === node.id || node.val > 6) {
          const ringGeo = new THREE.RingGeometry(size * 1.3, size * 1.5, 32);
          const ringMat = new THREE.MeshBasicMaterial({
            color: node.color,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.6
          });
          const ringMesh = new THREE.Mesh(ringGeo, ringMat);
          group.add(ringMesh);
        }

        return group;
      })
      // Animated Energy Particles along links
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
          return isConnected ? link.width * 1.5 : 0.8;
        }
        return link.width;
      })
      .linkDirectionalParticles((link: any) => link.directional ? 2 : 0)
      .linkDirectionalParticleSpeed((link: any) => link.particleSpeed || 0.005)
      .linkDirectionalParticleWidth(2.5)
      .linkDirectionalArrowLength((link: any) => link.directional ? 4 : 0)
      .linkDirectionalArrowRelPos(0.9)
      .linkCurvature('curvature')
      .onNodeClick((node: any) => {
        if (node && node.id) {
          this.onNodeSelect(node.id);
          this.focusOnNode(node);
        }
      })
      .onBackgroundClick(() => {
        this.onNodeSelect(null);
      });

    // Custom force parameters for spacious 3D layout
    this.graph.d3Force('charge').strength(-160);
    this.graph.d3Force('link').distance(65);
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

    this.graph.graphData({
      nodes: projection.nodes.map(n => ({ ...n })),
      links: projection.links.map(l => ({ ...l }))
    });

    if (selectedId) {
      const node = projection.nodes.find(n => n.id === selectedId);
      if (node) {
        setTimeout(() => this.focusOnNode(node), 200);
      }
    }
  }

  public focusOnNode(node: GraphNode): void {
    const distance = 110;
    const nodes = this.graph.graphData().nodes;
    const graphNode = nodes.find((n: any) => n.id === node.id);
    if (!graphNode) return;

    const x = graphNode.x || 0;
    const y = graphNode.y || 0;
    const z = graphNode.z || 0;

    const distRatio = 1 + distance / (Math.hypot(x, y, z) || 1);

    this.graph.cameraPosition(
      { x: x * distRatio, y: y * distRatio, z: z * distRatio },
      { x, y, z },
      1500
    );
  }

  public toggleAutoRotate(): boolean {
    this.isAutoRotating = !this.isAutoRotating;
    const controls = this.graph.controls();
    if (controls) {
      controls.autoRotate = this.isAutoRotating;
      controls.autoRotateSpeed = 0.8;
    }
    return this.isAutoRotating;
  }

  public zoomIn(): void {
    const cam = this.graph.cameraPosition();
    this.graph.cameraPosition(
      { x: cam.x * 0.8, y: cam.y * 0.8, z: cam.z * 0.8 },
      null,
      400
    );
  }

  public zoomOut(): void {
    const cam = this.graph.cameraPosition();
    this.graph.cameraPosition(
      { x: cam.x * 1.25, y: cam.y * 1.25, z: cam.z * 1.25 },
      null,
      400
    );
  }

  public resetView(): void {
    this.graph.zoomToFit(1000, 40);
  }
}
