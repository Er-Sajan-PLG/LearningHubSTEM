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

export interface LhsKnowledgeExport {
  export_version: string;
  schema_version: string;
  content_hash?: string; // ADR-0022: deterministic stamp; replaces wall-clock generated_at
  source?: string;
  entity_count: number;
  entities: LhsEntity[];
}

export class KnowledgeExportLoadError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'KnowledgeExportLoadError';
  }
}

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

  // Validate relationship targets exist
  for (const entity of data.entities) {
    for (const rel of entity.relationships ?? []) {
      if (rel.target && !idSet.has(rel.target)) {
        console.warn(`Export contains relationship pointing to unindexed target '${rel.target}' from '${entity.id}'`);
      }
    }
  }

  return data;
}
