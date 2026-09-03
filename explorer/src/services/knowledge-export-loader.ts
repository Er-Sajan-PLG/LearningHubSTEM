export interface LhsProvenance {
  ai_drafted?: boolean;
  source_kind?: string;
  source?: string;
  reviewer?: string;
  reviewed_at?: string;
}

export interface LhsRelationship {
  type: string;
  target: string;
  note?: string;
}

export interface LhsEntity {
  id: string;
  type: string;
  name: string;
  domain: string;
  status: string;
  definition: string;
  symbol?: string | null;
  unit?: string | null;
  equation?: string | null;
  common_misconceptions?: string[];
  learning_objectives?: string[];
  real_world_applications?: string[];
  examples?: string[];
  key_experiments?: string[];
  provenance?: LhsProvenance;
  relationships?: LhsRelationship[];
}

/** Minimal view of a first-class connection (export contract v1.0, ADR-0023). */
export interface LhsConnection {
  id: string;
  source: string;
  relation: string;
  target: string;
  assertion: { status: string; type: string; review: { status: string } };
}

export interface LhsKnowledgeExport {
  export_version: string; // contract v1.0: connections + sources are REQUIRED (ADR-0023)
  schema_version: string;
  content_hash?: string; // ADR-0022: deterministic stamp; replaces wall-clock generated_at
  source?: string;
  entity_count: number;
  connection_count?: number;
  source_count?: number;
  entities: LhsEntity[];
  connections?: LhsConnection[]; // present in v1.x; `entities[].relationships` is a deprecated projection
}

export class KnowledgeExportLoadError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'KnowledgeExportLoadError';
  }
}

/** Export contract major version this explorer consumes (ADR-0023). */
export const SUPPORTED_EXPORT_MAJOR = 1;

export async function loadKnowledgeExport(url: string = '/exports/knowledge.json'): Promise<LhsKnowledgeExport> {
  let response: Response;
  try {
    response = await fetch(url);
  } catch (err) {
    throw new KnowledgeExportLoadError(`Failed to fetch knowledge export from ${url}: ${(err as Error).message}`);
  }

  if (!response.ok) {
    throw new KnowledgeExportLoadError(`HTTP ${response.status} when fetching knowledge export from ${url}`);
  }

  let data: LhsKnowledgeExport;
  try {
    data = await response.json();
  } catch (err) {
    throw new KnowledgeExportLoadError(`Failed to parse knowledge export JSON: ${(err as Error).message}`);
  }

  // Integrity Validation
  if (!data || typeof data !== 'object' || !Array.isArray(data.entities)) {
    throw new KnowledgeExportLoadError('Invalid knowledge export format: missing top-level entities array');
  }

  const major = parseInt(String(data.export_version ?? '').split('.')[0], 10);
  if (major !== SUPPORTED_EXPORT_MAJOR) {
    throw new KnowledgeExportLoadError(
      `Unsupported export_version '${data.export_version}' (explorer supports ${SUPPORTED_EXPORT_MAJOR}.x)`,
    );
  }
  if (!Array.isArray(data.connections)) {
    throw new KnowledgeExportLoadError('Invalid v1.x export: missing required connections array');
  }

  const idSet = new Set<string>();
  for (const entity of data.entities) {
    if (!entity.id || typeof entity.id !== 'string') {
      throw new KnowledgeExportLoadError('Invalid entity in export: missing stable string ID');
    }
    if (idSet.has(entity.id)) {
      throw new KnowledgeExportLoadError(`Duplicate entity ID in export: '${entity.id}'`);
    }
    idSet.add(entity.id);
  }

  for (const c of data.connections) {
    if (!idSet.has(c.source) || !idSet.has(c.target)) {
      throw new KnowledgeExportLoadError(`Connection ${c.id} references an unindexed entity`);
    }
  }

  // Validate relationship targets exist (deprecated projection; removed in contract 2.0)
  for (const entity of data.entities) {
    for (const rel of entity.relationships ?? []) {
      if (rel.target && !idSet.has(rel.target)) {
        console.warn(`Export contains relationship pointing to unindexed target '${rel.target}' from '${entity.id}'`);
      }
    }
  }

  return data;
}
