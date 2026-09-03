import { LhsEntity, LhsKnowledgeExport } from './knowledge-export-loader';
import { collectEdges } from './graph-projection';

export interface ConceptDetails {
  entity: LhsEntity;
  prerequisites: LhsEntity[];
  dependents: LhsEntity[];
  related: LhsEntity[];
}

export class ConceptNotFoundError extends Error {
  constructor(id: string) {
    super(`Concept not found in export: '${id}'`);
    this.name = 'ConceptNotFoundError';
  }
}

export function getConceptDetails(id: string, exportData: LhsKnowledgeExport): ConceptDetails {
  const entityMap = new Map<string, LhsEntity>(exportData.entities.map(e => [e.id, e]));
  const target = entityMap.get(id);

  if (!target) {
    throw new ConceptNotFoundError(id);
  }

  const prereqTypes = new Set(['logically_requires', 'mathematically_requires']);
  const prerequisites: LhsEntity[] = [];
  const related: LhsEntity[] = [];

  // Edges come from canonical connections[] (ADR-0020 / plan v2 E1.6); the inline
  // relationships[] projection is only a fallback for pre-v1.0 exports.
  const edges = collectEdges(exportData);

  for (const edge of edges) {
    if (edge.source !== id) continue;
    const relEntity = entityMap.get(edge.target);
    if (!relEntity) continue;
    if (prereqTypes.has(edge.relation)) {
      prerequisites.push(relEntity);
    } else {
      related.push(relEntity);
    }
  }

  // Dependents: entities whose prerequisite edge points at this concept.
  const dependents: LhsEntity[] = [];
  const seenDependents = new Set<string>();
  for (const edge of edges) {
    if (edge.target !== id || edge.source === id) continue;
    if (!prereqTypes.has(edge.relation)) continue;
    if (seenDependents.has(edge.source)) continue;
    const dep = entityMap.get(edge.source);
    if (!dep) continue;
    seenDependents.add(edge.source);
    dependents.push(dep);
  }

  return {
    entity: target,
    prerequisites,
    dependents,
    related
  };
}
