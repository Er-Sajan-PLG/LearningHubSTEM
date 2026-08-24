import ForceGraph3D from '3d-force-graph';
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
        <div style="background:rgba(17,24,39,0.95);padding:8px 12px;border-radius:8px;border:1px solid rgba(255,255,255,0.15);color:#fff;font-family:sans-serif;font-size:0.85rem;box-shadow:0 4px 12px rgba(0,0,0,0.5);">
          <strong style="color:#ffffff;font-size:0.95rem;">${node.name}</strong><br/>
          <span style="color:#9ca3af;font-size:0.78rem;">${node.domain} · ${node.type}</span>
        </div>
      `)
      .nodeColor((node: any) => node.color)
      .nodeVal((node: any) => node.val)
      .linkColor((link: any) => link.color)
      .linkWidth((link: any) => link.width)
      .linkDirectionalArrowLength(4)
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
        // Small delay to ensure force simulation nodes are positioned
        setTimeout(() => this.focusOnNode(node), 200);
      }
    }
  }

  public focusOnNode(node: GraphNode): void {
    const distance = 120;
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

  public resetView(): void {
    this.graph.zoomToFit(1000, 40);
  }
}
