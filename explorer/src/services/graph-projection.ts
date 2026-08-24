import { LhsKnowledgeExport, LhsEntity } from './knowledge-export-loader';
import { getDomainTheme, GRAPH_THEME } from '../styles/theme';

export interface GraphNode {
  id: string;
  name: string;
  domain: string;
  type: string;
  status: string;
  val: number; // node size weight
  color: string;
  entity: LhsEntity;
}

export interface GraphLink {
  source: string;
  target: string;
  relationship: string;
  color: string;
  directional: boolean;
  curvature: number;
  width: number;
}

export interface GraphProjection {
  nodes: GraphNode[];
  links: GraphLink[];
}

export function projectKnowledgeGraph(
  exportData: LhsKnowledgeExport,
  domainFilter: string = 'all',
  relationshipFilter: string = 'all',
  activeMode: string = 'explore'
): GraphProjection {
  const entityMap = new Map<string, LhsEntity>(exportData.entities.map(e => [e.id, e]));
  let filteredEntities = exportData.entities;

  // Filter by domain
  if (domainFilter !== 'all') {
    filteredEntities = filteredEntities.filter(e => e.domain === domainFilter);
  }

  const validIds = new Set<string>(filteredEntities.map(e => e.id));

  // Compute node sizes based on incoming/outgoing references (degree centrality)
  const degreeMap = new Map<string, number>();
  for (const entity of exportData.entities) {
    for (const rel of entity.relationships ?? []) {
      if (validIds.has(entity.id) && validIds.has(rel.target)) {
        degreeMap.set(entity.id, (degreeMap.get(entity.id) ?? 0) + 1);
        degreeMap.set(rel.target, (degreeMap.get(rel.target) ?? 0) + 1);
      }
    }
  }

  const nodes: GraphNode[] = filteredEntities.map(entity => {
    const domainTheme = getDomainTheme(entity.domain);
    const degree = degreeMap.get(entity.id) ?? 1;
    return {
      id: entity.id,
      name: entity.name,
      domain: entity.domain,
      type: entity.type,
      status: entity.status,
      val: Math.max(3, Math.min(12, 3 + degree * 0.8)),
      color: domainTheme.color,
      entity
    };
  });

  const links: GraphLink[] = [];

  for (const entity of filteredEntities) {
    for (const rel of entity.relationships ?? []) {
      if (!validIds.has(rel.target)) continue;

      // Mode-specific filtering
      if (activeMode === 'prerequisites') {
        // Prerequisite mode only includes logically_requires and mathematically_requires
        if (rel.type !== 'logically_requires' && rel.type !== 'mathematically_requires') {
          continue;
        }
      }

      if (relationshipFilter !== 'all' && rel.type !== relationshipFilter) {
        continue;
      }

      const style = GRAPH_THEME.edges[rel.type as keyof typeof GRAPH_THEME.edges] ?? GRAPH_THEME.edges.default;

      links.push({
        source: entity.id,
        target: rel.target,
        relationship: rel.type,
        color: style.color,
        directional: !!style.directional,
        curvature: rel.type === 'logically_requires' ? 0 : 0.1,
        width: style.width
      });
    }
  }

  return { nodes, links };
}
