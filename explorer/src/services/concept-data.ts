import { LhsEntity, LhsKnowledgeExport } from './knowledge-export-loader';

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

  for (const rel of target.relationships ?? []) {
    const relEntity = entityMap.get(rel.target);
    if (!relEntity) continue;
    if (prereqTypes.has(rel.type)) {
      prerequisites.push(relEntity);
    } else {
      related.push(relEntity);
    }
  }

  // Find dependents (entities that specify 'id' as their prerequisite target)
  const dependents: LhsEntity[] = [];
  for (const entity of exportData.entities) {
    if (entity.id === id) continue;
    for (const rel of entity.relationships ?? []) {
      if (rel.target === id && prereqTypes.has(rel.type)) {
        dependents.push(entity);
        break;
      }
    }
  }

  return {
    entity: target,
    prerequisites,
    dependents,
    related
  };
}
