import ForceGraph3D from '3d-force-graph';
import * as THREE from 'three';
import { GraphProjection, GraphNode, GraphLink } from '../services/graph-projection';
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
  }

  private initGraph(): void {
    this.graph = (ForceGraph3D as any)()(this.container)
      .backgroundColor(GRAPH_THEME.canvas.background)
      .nodeId('id')
      .nodeLabel((node: any) => `<div style="background:rgba(17,24,39,0.9);padding:6px 10px;border-radius:6px;border:1px solid #374151;color:#fff;font-family:sans-serif;font-size:0.85rem;"><strong>${node.name}</strong><br/><span style="color:#9ca3af;font-size:0.75rem;">${node.domain} · ${node.type}</span></div>`)
      .nodeColor((node: any) => node.color)
      .nodeVal((node: any) => node.val)
      .linkColor((link: any) => link.color)
      .linkWidth((link: any) => link.width)
      .linkDirectionalArrowLength(4)
      .linkDirectionalArrowRelPos(0.9)
      .linkCurvature('curvature')
      .onNodeClick((node: any) => {
        if (node) {
          this.onNodeSelect(node.id);
          this.focusOnNode(node);
        }
      })
      .onBackgroundClick(() => {
        this.onNodeSelect(null);
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
        this.focusOnNode(node);
      }
    }
  }

  public focusOnNode(node: GraphNode): void {
    const distance = 120;
    const graphNode = this.graph.graphData().nodes.find((n: any) => n.id === node.id);
    if (!graphNode) return;

    const distRatio = 1 + distance / Math.hypot(graphNode.x || 1, graphNode.y || 1, graphNode.z || 1);

    this.graph.cameraPosition(
      { x: (graphNode.x || 0) * distRatio, y: (graphNode.y || 0) * distRatio, z: (graphNode.z || 0) * distRatio },
      { x: graphNode.x || 0, y: graphNode.y || 0, z: graphNode.z || 0 },
      1500
    );
  }

  public resetView(): void {
    this.graph.zoomToFit(1000, 40);
  }
}
