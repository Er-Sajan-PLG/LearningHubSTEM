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
  // Seeded layout metadata (populated by projectKnowledgeGraph)
  cluster: string;        // topic/domain grouping id
  clusterLabel: string;   // human label for the cluster
  seedX: number;          // initial x position for the force simulation
  seedY: number;
  seedZ: number;
}

export interface GraphLink {
  source: string;
  target: string;
  relationship: string;
  color: string;
  directional: boolean;
  curvature: number;
  width: number;
  /** Epistemic trust annotation (plan v2 E1.6): review status of the underlying assertion. */
  reviewStatus: EdgeReviewStatus;
  /** Trust-graded opacity so unreviewed edges read as provisional. */
  opacity: number;
  /** Canonical connection id when the edge came from connections[]; null for the fallback projection. */
  connectionId: string | null;
}

/** Review states an edge can carry. `unknown` = derived from the deprecated inline projection. */
export type EdgeReviewStatus = 'canonical' | 'human_reviewed' | 'reviewed' | 'unreviewed' | 'unknown';

/**
 * Trust-graded edge opacity (E1.6). An unreviewed assertion must not look as solid as a
 * human-reviewed one: the explorer visualises epistemic status, it does not flatten it.
 */
export const REVIEW_OPACITY: Record<EdgeReviewStatus, number> = {
  canonical: 1.0,
  human_reviewed: 0.85,
  reviewed: 0.7,
  unreviewed: 0.28,
  unknown: 0.28,
};

export function reviewStatusOf(status: string | undefined): EdgeReviewStatus {
  switch (status) {
    case 'canonical':
    case 'human_reviewed':
    case 'reviewed':
      return status;
    case 'unreviewed':
      return 'unreviewed';
    default:
      return 'unknown';
  }
}

/**
 * Canonical edge list for the explorer (plan v2 E1.6 / ADR-0020).
 *
 * `connections[]` is the single source of relationship truth. The deprecated
 * `entities[].relationships` projection is used ONLY when an export carries no
 * connections (pre-v1.0 artifacts) — and then every edge is marked `unknown` trust,
 * because the projection has no review status to report.
 */
export interface EdgeRecord {
  source: string;
  relation: string;
  target: string;
  reviewStatus: EdgeReviewStatus;
  connectionId: string | null;
}

export function collectEdges(exportData: LhsKnowledgeExport): EdgeRecord[] {
  const connections = exportData.connections ?? [];
  if (connections.length > 0) {
    return connections
      .filter(c => (c.assertion?.status ?? 'active') === 'active')
      .map(c => ({
        source: c.source,
        relation: c.relation,
        target: c.target,
        reviewStatus: reviewStatusOf(c.assertion?.review?.status),
        connectionId: c.id,
      }));
  }
  // Fallback: deprecated inline projection (no trust information available).
  const edges: EdgeRecord[] = [];
  for (const entity of exportData.entities) {
    for (const rel of entity.relationships ?? []) {
      edges.push({
        source: entity.id,
        relation: rel.type,
        target: rel.target,
        reviewStatus: 'unknown',
        connectionId: null,
      });
    }
  }
  return edges;
}

export interface ClusterInfo {
  id: string;
  label: string;
  color: string;
  anchorX: number;
  anchorY: number;
  anchorZ: number;
}

export interface GraphProjection {
  nodes: GraphNode[];
  links: GraphLink[];
  clusters: ClusterInfo[];
}

// Map a physics entity slug to a topic cluster.
// This is a display-layer grouping (knowledge-curriculum-agnostic is irrelevant here;
// it simply organizes the 3D scene so related concepts sit near each other).
const PHYSICS_TOPIC_KEYWORDS: Record<string, string[]> = {
  'mechanics': ['force', 'mass', 'acceleration', 'displacement', 'distance', 'speed', 'time', 'momentum', 'impulse', 'inertia',
    'friction', 'newton', 'work', 'kinetic', 'potential', 'gravitation', 'weight', 'free-fall', 'projectile',
    'gravitational', 'mechanical', 'conservation', 'efficiency', 'equations-of-motion', 'velocity', 'power', 'energy', 'scalar', 'vector'],
  'waves-optics': ['wave', 'sound', 'light', 'amplitude', 'frequency', 'wavelength', 'wave-speed', 'reflect', 'refract',
    'lens', 'mirror', 'ray', 'electromagnetic-spectrum'],
  'electricity-magnetism': ['current', 'voltage', 'resistance', 'electric', 'ohm', 'coulomb', 'magnet', 'magnetic',
    'electromagnetic-induction', 'electromagnetism', 'motor', 'generator', 'flux', 'heating-effect'],
  'thermal': ['heat', 'temperature', 'thermal', 'specific-heat', 'change-of-state'],
  'atomic-nuclear': ['atomic', 'radioactiv', 'nuclear', 'fission', 'fusion'],
  'energy-and-environment': ['energy-sources', 'our-environment', 'buoyancy', 'density', 'pressure'],
  'measurement': ['unit', 'measurement', 'physical-quantity'],
};

// Map the entity-id namespace prefix (the part before the dot) to its domain.
// LHS ids are lhs:<ns>.<slug> where ns is a short code (phys/bio/chem/earth/...).
const NS_TO_DOMAIN: Record<string, string> = {
  phys: 'physics',
  chem: 'chemistry',
  bio: 'biology',
  earth: 'earth-space',
  eng: 'engineering',
  math: 'mathematics',
  practice: 'scientific-practice',
  epist: 'scientific-practice',
};

// Map a math entity slug to a math sub-topic cluster (mirrors LHS math subdomains).
const MATH_TOPIC_KEYWORDS: Record<string, string[]> = {
  'algebra': ['algebraic', 'polynomial', 'quadratic', 'linear-copy', 'variable', 'equation', 'expression', 'function-copy', 'matrix'],
  'number-theory': ['number', 'integer', 'natural', 'rational', 'irrational', 'prime', 'sequence', 'series'],
  'geometry': ['geometry', 'angle', 'triangle', 'circle', 'pythagorean', 'trigonometric', 'theorem'],
  'statistics-probability': ['statistics', 'probability', 'mean', 'median', 'standard-deviation', 'permutation', 'combination'],
  'calculus': ['calculus', 'limit', 'derivative', 'integral', 'continuity'],
  'functions': ['function', 'exponential', 'logarithmic', 'linear-function', 'quadratic-function'],
  'measurement': ['area', 'volume', 'measurement'],
};

export function clusterForEntity(id: string): string {
  // id format: lhs:<ns>.<slug>  (e.g. lhs:bio.animal-cell)
  const match = id.match(/^lhs:([a-z0-9-]+)\.([a-z0-9-]+)$/);
  const ns = match ? match[1] : '';
  const slug = match ? match[2] : '';
  const domain = NS_TO_DOMAIN[ns] || ns || 'other';
  if (domain === 'physics') {
    for (const [cluster, keywords] of Object.entries(PHYSICS_TOPIC_KEYWORDS)) {
      if (keywords.some(k => slug.includes(k))) return cluster;
    }
    return 'mechanics';
  }
  // Mathematics sub-topics cluster the same way physics does (mirrors LHS math subdomains).
  if (domain === 'mathematics') {
    for (const [cluster, keywords] of Object.entries(MATH_TOPIC_KEYWORDS)) {
      if (keywords.some(k => slug.includes(k))) return cluster;
    }
    return 'mathematics';
  }
  return domain || 'other';
}

const CLUSTER_LABELS: Record<string, string> = {
  physics: 'Physics',
  mechanics: 'Mechanics & Motion',
  'waves-optics': 'Waves & Optics',
  'electricity-magnetism': 'Electricity & Magnetism',
  thermal: 'Thermal Physics',
  'atomic-nuclear': 'Atomic & Nuclear',
  'energy-and-environment': 'Energy & Environment',
  measurement: 'Measurement',
  chemistry: 'Chemistry',
  biology: 'Biology',
  'earth-space': 'Earth & Space',
  'scientific-practice': 'Scientific Practice',
  engineering: 'Engineering',
  mathematics: 'Mathematics',
  algebra: 'Algebra',
  'number-theory': 'Number Theory',
  geometry: 'Geometry',
  'statistics-probability': 'Statistics & Probability',
  calculus: 'Calculus',
  functions: 'Functions',
  other: 'Other',
};

// Arrange clusters on a sphere around the origin; physics-mechanics is the
// visual "core", the rest orbit as satellites. Anchor = place the cluster's
// centroid here and pin a soft force toward it so connected clusters sit near
// their domain, while cross-domain edges bridge the gaps.
const CLUSTER_POSITIONS: Record<string, [number, number, number]> = {
  mechanics: [0, 0, 18],                 // central core
  'measurement': [16, 10, 10],
  'waves-optics': [-18, 12, -4],
  'electricity-magnetism': [14, -12, 6],
  thermal: [-16, -10, 12],
  'atomic-nuclear': [20, 4, -12],
  'energy-and-environment': [-8, -6, 24],
  chemistry: [30, 14, -14],
  biology: [-30, 16, 10],
  'earth-space': [6, 30, -18],
  'scientific-practice': [-26, -24, -6],
  engineering: [30, -22, 6],
  mathematics: [28, -30, 20],
  algebra: [34, -26, 16],
  'number-theory': [26, -34, 12],
  geometry: [38, -22, 22],
  'statistics-probability': [30, -38, 20],
  calculus: [24, -28, 26],
  functions: [36, -32, 14],
  other: [0, -26, -20],
};

const DOMAIN_COLOR: Record<string, string> = {
  physics: '#38bdf8',
  chemistry: '#34d399',
  biology: '#f472b6',
  'earth-space': '#fbbf24',
  'scientific-practice': '#a78bfa',
  engineering: '#22d3ee',
  mathematics: '#e879f9',
};

export function getClusterColor(cluster: string): string {
  if (DOMAIN_COLOR[cluster]) return DOMAIN_COLOR[cluster];
  // physics sub-topics share the physics color with slight derivation
  if (cluster in PHYSICS_TOPIC_KEYWORDS) return '#38bdf8';
  // math sub-topics share the mathematics color
  if (cluster in MATH_TOPIC_KEYWORDS) return '#e879f9';
  return '#94a3b8';
}

export function getClusterLabel(cluster: string): string {
  return CLUSTER_LABELS[cluster] ?? cluster;
}

export function projectKnowledgeGraph(
  exportData: LhsKnowledgeExport,
  domainFilter: string = 'all',
  relationshipFilter: string = 'all',
  activeMode: string = 'explore'
): GraphProjection {
  let filteredEntities = exportData.entities;
  const edges = collectEdges(exportData);

  if (domainFilter !== 'all') {
    filteredEntities = filteredEntities.filter(e => e.domain === domainFilter);
  }

  const validIds = new Set<string>(filteredEntities.map(e => e.id));

  // degree centrality for node size
  const degreeMap = new Map<string, number>();
  for (const edge of edges) {
    if (validIds.has(edge.source) && validIds.has(edge.target)) {
      degreeMap.set(edge.source, (degreeMap.get(edge.source) ?? 0) + 1);
      degreeMap.set(edge.target, (degreeMap.get(edge.target) ?? 0) + 1);
    }
  }

  // Build cluster membership + anchors
  const clusterMap = new Map<string, ClusterInfo>();
  const nodes: GraphNode[] = filteredEntities.map(entity => {
    const cluster = clusterForEntity(entity.id);
    if (!clusterMap.has(cluster)) {
      const [ax, ay, az] = CLUSTER_POSITIONS[cluster] ?? CLUSTER_POSITIONS.other;
      clusterMap.set(cluster, {
        id: cluster,
        label: getClusterLabel(cluster),
        color: getClusterColor(cluster),
        anchorX: ax, anchorY: ay, anchorZ: az,
      });
    }
    const domainTheme = getDomainTheme(entity.domain);
    const degree = degreeMap.get(entity.id) ?? 1;
    // Seed each node near its cluster anchor with slight jitter so nodes within
    // a cluster spread out but the cluster stays recognizable.
    const anchor = clusterMap.get(cluster)!;
    const jitter = () => (Math.random() - 0.5) * 7;
    return {
      id: entity.id,
      name: entity.name,
      domain: entity.domain,
      type: entity.type,
      status: entity.status,
      val: Math.max(3, Math.min(12, 3 + degree * 0.8)),
      color: domainTheme.color,
      entity,
      cluster,
      clusterLabel: anchor.label,
      seedX: anchor.anchorX + jitter(),
      seedY: anchor.anchorY + jitter(),
      seedZ: anchor.anchorZ + jitter(),
    };
  });

  const links: GraphLink[] = [];
  for (const edge of edges) {
    if (!validIds.has(edge.source) || !validIds.has(edge.target)) continue;
    if (activeMode === 'prerequisites') {
      if (edge.relation !== 'logically_requires' && edge.relation !== 'mathematically_requires') continue;
    }
    if (relationshipFilter !== 'all' && edge.relation !== relationshipFilter) continue;

    const style = GRAPH_THEME.edges[edge.relation as keyof typeof GRAPH_THEME.edges] ?? GRAPH_THEME.edges.default;
    links.push({
      source: edge.source,
      target: edge.target,
      relationship: edge.relation,
      color: style.color,
      directional: !!style.directional,
      curvature: edge.relation === 'logically_requires' ? 0 : 0.1,
      width: style.width,
      reviewStatus: edge.reviewStatus,
      opacity: REVIEW_OPACITY[edge.reviewStatus],
      connectionId: edge.connectionId,
    });
  }

  const clusters = Array.from(clusterMap.values());
  return { nodes, links, clusters };
}