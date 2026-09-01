export interface DomainTheme {
  color: string;
  name: string;
  badgeBg: string;
  badgeBorder: string;
  glowColor: string;
  icon: string;
}

export const GRAPH_THEME = {
  domains: {
    physics: {
      color: '#38bdf8',
      name: 'Physics',
      badgeBg: 'rgba(56, 189, 248, 0.12)',
      badgeBorder: 'rgba(56, 189, 248, 0.4)',
      glowColor: 'rgba(56, 189, 248, 0.6)',
      icon: '⚡'
    },
    chemistry: {
      color: '#34d399',
      name: 'Chemistry',
      badgeBg: 'rgba(52, 211, 153, 0.12)',
      badgeBorder: 'rgba(52, 211, 153, 0.4)',
      glowColor: 'rgba(52, 211, 153, 0.6)',
      icon: '🧪'
    },
    biology: {
      color: '#f472b6',
      name: 'Biology',
      badgeBg: 'rgba(244, 114, 182, 0.12)',
      badgeBorder: 'rgba(244, 114, 182, 0.4)',
      glowColor: 'rgba(244, 114, 182, 0.6)',
      icon: '🧬'
    },
    'earth-space': {
      color: '#fbbf24',
      name: 'Earth & Space',
      badgeBg: 'rgba(251, 191, 36, 0.12)',
      badgeBorder: 'rgba(251, 191, 36, 0.4)',
      glowColor: 'rgba(251, 191, 36, 0.6)',
      icon: '🪐'
    },
    'scientific-practice': {
      color: '#a78bfa',
      name: 'Scientific Practice',
      badgeBg: 'rgba(167, 139, 250, 0.12)',
      badgeBorder: 'rgba(167, 139, 250, 0.4)',
      glowColor: 'rgba(167, 139, 250, 0.6)',
      icon: '📐'
    },
    engineering: {
      color: '#22d3ee',
      name: 'Engineering',
      badgeBg: 'rgba(34, 211, 238, 0.12)',
      badgeBorder: 'rgba(34, 211, 238, 0.4)',
      glowColor: 'rgba(34, 211, 238, 0.6)',
      icon: '⚙️'
    },
    mathematics: {
      color: '#e879f9',
      name: 'Mathematics',
      badgeBg: 'rgba(232, 121, 249, 0.12)',
      badgeBorder: 'rgba(232, 121, 249, 0.4)',
      glowColor: 'rgba(232, 121, 249, 0.6)',
      icon: '∑'
    }
  } as Record<string, DomainTheme>,

  edges: {
    logically_requires: { color: '#38bdf8', opacity: 0.8, directional: true, particleSpeed: 0.006, width: 2.2 },
    mathematically_requires: { color: '#34d399', opacity: 0.8, directional: true, particleSpeed: 0.007, width: 2.2 },
    part_of: { color: '#a78bfa', opacity: 0.5, directional: true, particleSpeed: 0.003, width: 1.5 },
    special_case_of: { color: '#f472b6', opacity: 0.5, directional: true, particleSpeed: 0.003, width: 1.5 },
    applies_to: { color: '#fbbf24', opacity: 0.6, directional: true, particleSpeed: 0.004, width: 1.8 },
    appears_in_law: { color: '#fbbf24', opacity: 0.4, directional: false, particleSpeed: 0, width: 1.2 },
    related_to: { color: '#64748b', opacity: 0.35, directional: false, particleSpeed: 0, width: 1.0 },
    default: { color: '#94a3b8', opacity: 0.3, directional: false, particleSpeed: 0, width: 1.0 }
  },

  canvas: {
    background: '#030712',
    gridColor: 'rgba(56, 189, 248, 0.03)',
    dimmedOpacity: 0.12
  }
};

export function getDomainTheme(domain: string): DomainTheme {
  return (
    GRAPH_THEME.domains[domain] ?? {
      color: '#94a3b8',
      name: domain,
      badgeBg: 'rgba(148, 163, 184, 0.12)',
      badgeBorder: 'rgba(148, 163, 184, 0.4)',
      glowColor: 'rgba(148, 163, 184, 0.6)',
      icon: '📌'
    }
  );
}
