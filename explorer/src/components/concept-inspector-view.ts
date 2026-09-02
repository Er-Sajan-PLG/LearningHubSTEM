import { ConceptDetails } from '../services/concept-data';
import { LhsEntity } from '../services/knowledge-export-loader';
import { getDomainTheme } from '../styles/theme';

declare const katex: any;

export interface ConceptInspectorOptions {
  container: HTMLElement;
  onConceptSelect: (id: string) => void;
}

type TabId = 'overview' | 'relations' | 'examples' | 'misc';
const TABS: { id: TabId; label: string; icon: string }[] = [
  { id: 'overview', label: 'Overview', icon: '📖' },
  { id: 'relations', label: 'Relations', icon: '🔗' },
  { id: 'examples', label: 'Examples', icon: '🌐' },
  { id: 'misc', label: 'Misconceptions', icon: '💡' },
];

export class ConceptInspectorView {
  private container: HTMLElement;
  private onConceptSelect: (id: string) => void;
  private currentTab: TabId = 'overview';
  private currentDetails: ConceptDetails | null = null;

  constructor(options: ConceptInspectorOptions) {
    this.container = options.container;
    this.onConceptSelect = options.onConceptSelect;
  }

  public renderEmpty(): void {
    this.currentDetails = null;
    this.container.innerHTML = `
      <div class="empty-inspector">
        <div class="empty-icon">⚛</div>
        <h3 style="font-family:'Outfit',sans-serif;font-size:1.2rem;font-weight:700;color:#ffffff;">Explore STEMMA</h3>
        <p style="font-size:0.9rem;line-height:1.5;color:var(--text-secondary);">Select any concept in the 3D graph or search for one above.</p>
        <div style="font-size:0.84rem;text-align:left;background:rgba(15, 23, 42, 0.6);padding:14px 16px;border-radius:12px;border:1px solid var(--border-glass);margin-top:12px;width:100%;">
          <div style="font-weight:700;color:var(--accent-cyan);font-family:'Outfit',sans-serif;margin-bottom:8px;">Explore the constellation:</div>
          <div>✨ <strong>3D clusters</strong> — answers/s-drag, or click a cluster to fly to it</div>
          <div>📖 <strong>Overview</strong> — definition, formula, quantities</div>
          <div>🔗 <strong>Relations</strong> — prerequisites & dependents</div>
          <div>🌐 <strong>Examples</strong> — real-world applications & experiments</div>
          <div>💡 <strong>Misconceptions</strong> — common traps</div>
        </div>
      </div>
    `;
  }

  public renderDetails(details: ConceptDetails): void {
    this.currentDetails = details;
    const { entity } = details;
    const domainTheme = getDomainTheme(entity.domain);

    // Header (always visible)
    let header = `
      <div class="inspector-header">
        <div class="badge-row">
          <span class="domain-badge" style="background:${domainTheme.badgeBg};color:${domainTheme.color};border:1px solid ${domainTheme.badgeBorder}">
            <span>${domainTheme.icon}</span> ${domainTheme.name}
          </span>
          <span class="type-badge">${entity.type}</span>
          <span class="type-badge" style="color:var(--accent-emerald);border-color:rgba(16,185,129,0.3);">${entity.status}</span>
        </div>
        <h2 class="concept-title">${this.escapeHtml(entity.name)}</h2>
        <div class="concept-id">${this.escapeHtml(entity.id)}</div>
      </div>
    `;

    // Tab bar
    let tabBar = `<div class="inspect-tabs">`;
    for (const t of TABS) {
      tabBar += `<button class="inspect-tab${t.id === this.currentTab ? ' active' : ''}" data-tab="${t.id}">${t.icon} ${t.label}</button>`;
    }
    tabBar += `</div><div class="inspect-body">`;

    this.container.innerHTML = header + tabBar + this.renderTab(this.currentTab, details) + `</div>`;

    // wire tabs
    const tabs = this.container.querySelectorAll('.inspect-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const id = tab.getAttribute('data-tab') as TabId;
        this.currentTab = id;
        if (this.currentDetails) this.renderDetails(this.currentDetails);
      });
    });
    // wire relation links
    const links = this.container.querySelectorAll('.entity-link');
    links.forEach(link => {
      link.addEventListener('click', () => {
        const id = link.getAttribute('data-id');
        if (id) this.onConceptSelect(id);
      });
    });
  }

  private renderTab(tab: TabId, details: ConceptDetails): string {
    const { entity } = details;
    switch (tab) {
      case 'overview':
        return this.renderOverview(details);
      case 'relations':
        return this.renderRelations(details);
      case 'examples':
        return this.renderExamples(entity);
      case 'misc':
        return this.renderMisconceptions(entity);
      default:
        return '';
    }
  }

  private renderOverview(details: ConceptDetails): string {
    const { entity } = details;
    let html = `
      <div class="inspector-section">
        <div class="section-title">📖 Canonical Definition</div>
        <div class="definition-text">${this.escapeHtml(entity.definition)}</div>
      </div>
    `;
    if (entity.equation) {
      let renderedEq = this.escapeHtml(entity.equation);
      if (typeof katex !== 'undefined') {
        try { renderedEq = katex.renderToString(entity.equation, { throwOnError: false, displayMode: true }); } catch (e) { /* fallthrough */ }
      }
      html += `
        <div class="inspector-section">
          <div class="section-title">📐 Formula</div>
          <div class="equation-box">${renderedEq}</div>
        </div>`;
    }
    if (entity.symbol || entity.unit) {
      html += `
        <div class="inspector-section">
          <div class="section-title">⚖️ Quantities</div>
          <div style="display:flex;gap:12px;flex-wrap:wrap;">
            ${entity.symbol ? `<div class="pill-chip"><span>Symbol</span><strong>${this.escapeHtml(entity.symbol)}</strong></div>` : ''}
            ${entity.unit ? `<div class="pill-chip"><span>SI Unit</span><strong>${this.escapeHtml(entity.unit)}</strong></div>` : ''}
          </div>
        </div>`;
    }
    // learning objectives
    if (entity.learning_objectives && entity.learning_objectives.length) {
      html += `
        <div class="inspector-section">
          <div class="section-title">🎯 Learning Objectives</div>
          <ul class="text-list">
            ${entity.learning_objectives.map(o => `<li>${this.escapeHtml(o)}</li>`).join('')}
          </ul>
        </div>`;
    }
    // provenance
    if (entity.provenance) {
      html += `
        <div class="inspector-section">
          <div class="section-title">🔬 Source</div>
          <div style="font-size:0.8rem;color:var(--text-secondary);background:rgba(15,23,42,0.5);padding:8px 10px;border-radius:8px;border:1px solid var(--border-glass);">
            <div>Standard: <strong style="color:#fff;">${this.escapeHtml(entity.provenance.source ?? '—')}</strong></div>
            <div>Kind: <strong style="color:var(--accent-cyan);">${this.escapeHtml(entity.provenance.source_kind ?? 'standard')}</strong></div>
          </div>
        </div>`;
    }
    return html;
  }

  private renderRelations(details: ConceptDetails): string {
    const { prerequisites, dependents, related } = details;
    let html = '';
    html += `
      <div class="inspector-section">
        <div class="section-title">⬅️ Prerequisites (${prerequisites.length})</div>
        ${prerequisites.length === 0
          ? `<div class="muted">Foundational core concept (no prerequisites).</div>`
          : `<ul class="entity-list">${prerequisites.map(p => this.entityLink(p, 'Pan ➔')).join('')}</ul>`}
      </div>`;
    html += `
      <div class="inspector-section">
        <div class="section-title">➡️ Enables (${dependents.length})</div>
        ${dependents.length === 0
          ? `<div class="muted">No downstream dependents linked yet.</div>`
          : `<ul class="entity-list">${dependents.map(d => this.entityLink(d, 'Pan ➔')).join('')}</ul>`}
      </div>`;
    if (related.length) {
      html += `
        <div class="inspector-section">
          <div class="section-title">🔗 Related (${related.length})</div>
          <ul class="entity-list">${related.map(r => this.entityLink(r, r.domain)).join('')}</ul>
        </div>`;
    }
    if (!prerequisites.length && !dependents.length && !related.length) {
      html += `<div class="muted">No relationships recorded for this concept yet.</div>`;
    }
    return html;
  }

  private renderExamples(entity: LhsEntity): string {
      let html = '';
      if (entity.real_world_applications && entity.real_world_applications.length) {
        html += `
          <div class="inspector-section">
            <div class="section-title">🌐 Real-World Applications</div>
            <ul class="insp-list">${entity.real_world_applications.map((a: string) => `<li>${this.escapeHtml(a)}</li>`).join('')}</ul>
          </div>`;
      }
      if (entity.examples && entity.examples.length) {
        html += `
          <div class="inspector-section">
            <div class="section-title">Examples</div>
            <ul class="insp-list">${entity.examples.map((e: string) => `<li>${this.escapeHtml(e)}</li>`).join('')}</ul>
          </div>`;
      }
      if (entity.key_experiments && entity.key_experiments.length) {
        html += `
          <div class="inspector-section">
            <div class="section-title">🧪 Key Experiments</div>
            <ul class="insp-list">${entity.key_experiments.map((k: string) => `<li>${this.escapeHtml(k)}</li>`).join('')}</ul>
          </div>`;
      }
      if (!html) html = `<div class="muted">No examples recorded yet.</div>`;
      return html;
    }

    private renderMisconceptions(entity: LhsEntity): string {
      let html = '';
      if (entity.common_misconceptions && entity.common_misconceptions.length) {
        html = entity.common_misconceptions.map((m: string) => `<div class="misconception-card">${this.escapeHtml(m)}</div>`).join('');
      } else {
        html = `<div class="muted">No known misconceptions.</div>`;
      }
      return html;
    }

    private entityLink(p: LhsEntity, right: string): string {
    const theme = getDomainTheme(p.domain);
    return `
      <li class="entity-link" data-id="${p.id}">
        <div style="display:flex;align-items:center;gap:8px;">
          <span>${theme.icon}</span><span>${this.escapeHtml(p.name)}</span>
        </div>
        <span style="font-size:0.72rem;color:${theme.color};">${right}</span>
      </li>`;
  }

  private escapeHtml(str: string): string {
    return str
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#039;');
  }
}