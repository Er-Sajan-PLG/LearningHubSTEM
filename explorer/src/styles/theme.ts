export interface DomainTheme {
  color: string;
  name: string;
  badgeBg: string;
  badgeBorder: string;
}

export const GRAPH_THEME = {
  domains: {
    physics: { color: '#3b82f6', name: 'Physics', badgeBg: 'rgba(59, 130, 246, 0.15)', badgeBorder: 'rgba(59, 130, 246, 0.4)' },
    chemistry: { color: '#10b981', name: 'Chemistry', badgeBg: 'rgba(16, 185, 129, 0.15)', badgeBorder: 'rgba(16, 185, 129, 0.4)' },
    biology: { color: '#ec4899', name: 'Biology', badgeBg: 'rgba(236, 72, 153, 0.15)', badgeBorder: 'rgba(236, 72, 153, 0.4)' },
    'earth-space': { color: '#f59e0b', name: 'Earth & Space Science', badgeBg: 'rgba(245, 158, 11, 0.15)', badgeBorder: 'rgba(245, 158, 11, 0.4)' },
    'scientific-practice': { color: '#8b5cf6', name: 'Scientific Practice', badgeBg: 'rgba(139, 92, 246, 0.15)', badgeBorder: 'rgba(139, 92, 246, 0.4)' },
    engineering: { color: '#06b6d4', name: 'Engineering', badgeBg: 'rgba(6, 182, 212, 0.15)', badgeBorder: 'rgba(6, 182, 212, 0.4)' }
  } as Record<string, DomainTheme>,
  
  edges: {
    logically_requires: { color: '#60a5fa', opacity: 0.8, directional: true, dash: false, width: 2 },
    mathematically_requires: { color: '#34d399', opacity: 0.8, directional: true, dash: false, width: 2 },
    part_of: { color: '#a78bfa', opacity: 0.6, directional: true, dash: true, width: 1.5 },
    special_case_of: { color: '#f472b6', opacity: 0.6, directional: true, dash: true, width: 1.5 },
    applies_to: { color: '#fbbf24', opacity: 0.6, directional: true, dash: false, width: 1.5 },
    appears_in_law: { color: '#fbbf24', opacity: 0.5, directional: false, dash: false, width: 1 },
    related_to: { color: '#6b7280', opacity: 0.4, directional: false, dash: false, width: 1 },
    default: { color: '#9ca3af', opacity: 0.4, directional: false, dash: false, width: 1 }
  },

  canvas: {
    background: '#090d16',
    nodeHighlightColor: '#ffffff',
    dimmedOpacity: 0.15
  }
};

export function getDomainTheme(domain: string): DomainTheme {
  return (
    GRAPH_THEME.domains[domain] ?? {
      color: '#9ca3af',
      name: domain,
      badgeBg: 'rgba(156, 163, 175, 0.15)',
      badgeBorder: 'rgba(156, 163, 175, 0.4)'
    }
  );
}
