import { ConceptDetails } from '../services/concept-data';
import { getDomainTheme } from '../styles/theme';

declare const katex: any;

export interface ConceptInspectorOptions {
  container: HTMLElement;
  onConceptSelect: (id: string) => void;
}

export class ConceptInspectorView {
  private container: HTMLElement;
  private onConceptSelect: (id: string) => void;

  constructor(options: ConceptInspectorOptions) {
    this.container = options.container;
    this.onConceptSelect = options.onConceptSelect;
  }

  public renderEmpty(): void {
    this.container.innerHTML = `
      <div class="empty-inspector">
        <div class="empty-icon">⚛</div>
        <h3 style="font-family:'Outfit',sans-serif;font-size:1.2rem;font-weight:700;color:#ffffff;">Explore LearningHubSTEM</h3>
        <p style="font-size:0.9rem;line-height:1.5;color:var(--text-secondary);">Select any concept in the 3D graph or search for one above.</p>
        <div style="font-size:0.84rem;text-align:left;background:rgba(15, 23, 42, 0.6);padding:14px 16px;border-radius:12px;border:1px solid var(--border-glass);margin-top:12px;width:100%;display:flex;flex-direction:column;gap:8px;">
          <div style="font-weight:700;color:var(--accent-cyan);font-family:'Outfit',sans-serif;">Exploration Capabilities:</div>
          <div>✨ <strong>3D Knowledge Constellation</strong>: Rotate & navigate</div>
          <div>📚 <strong>Canonical Definitions</strong> & Equations</div>
          <div>🔗 <strong>Prerequisite DAG Chain</strong>: Click to pan camera</div>
          <div>💡 <strong>Applications</strong> & Common Misconceptions</div>
          <div>🔬 <strong>Research Provenance</strong> & Standards</div>
        </div>
      </div>
    `;
  }

  public renderDetails(details: ConceptDetails): void {
    const { entity, prerequisites, dependents, related } = details;
    const domainTheme = getDomainTheme(entity.domain);

    let html = `
      <div class="inspector-header">
        <div class="badge-row">
          <span class="domain-badge" style="background:${domainTheme.badgeBg};color:${domainTheme.color};border:1px solid ${domainTheme.badgeBorder}">
            <span>${domainTheme.icon}</span> ${domainTheme.name}
          </span>
          <span class="type-badge">${entity.type}</span>
          <span class="type-badge" style="color:var(--accent-emerald);border-color:rgba(16, 185, 129, 0.3);">${entity.status}</span>
        </div>
        <h2 class="concept-title">${this.escapeHtml(entity.name)}</h2>
        <div class="concept-id">${this.escapeHtml(entity.id)}</div>
      </div>

      <!-- Definition -->
      <div class="inspector-section">
        <div class="section-title">📖 Canonical Definition</div>
        <div class="definition-text">${this.escapeHtml(entity.definition)}</div>
      </div>
    `;

    // Mathematical Formula
    if (entity.equation) {
      let renderedEq = this.escapeHtml(entity.equation);
      if (typeof katex !== 'undefined') {
        try {
          renderedEq = katex.renderToString(entity.equation, { throwOnError: false, displayMode: true });
        } catch (e) {
          // fallback to raw string
        }
      }

      html += `
        <div class="inspector-section">
          <div class="section-title">📐 Mathematical Formula</div>
          <div class="equation-box">${renderedEq}</div>
        </div>
      `;
    }

    // Properties
    if (entity.symbol || entity.unit) {
      html += `
        <div class="inspector-section">
          <div class="section-title">⚖️ Physical Quantities</div>
          <div style="display:flex;gap:16px;font-size:0.9rem;">
            ${entity.symbol ? `<div style="background:rgba(15, 23, 42, 0.6);padding:6px 12px;border-radius:8px;border:1px solid var(--border-glass);"><span style="color:var(--text-muted);">Symbol:</span> <strong style="color:var(--accent-cyan);">${this.escapeHtml(entity.symbol)}</strong></div>` : ''}
            ${entity.unit ? `<div style="background:rgba(15, 23, 42, 0.6);padding:6px 12px;border-radius:8px;border:1px solid var(--border-glass);"><span style="color:var(--text-muted);">SI Unit:</span> <strong style="color:var(--accent-cyan);">${this.escapeHtml(entity.unit)}</strong></div>` : ''}
          </div>
        </div>
      `;
    }

    // Prerequisites ("Requires")
    html += `
      <div class="inspector-section">
        <div class="section-title">⬅️ Prerequisites (${prerequisites.length})</div>
        ${prerequisites.length === 0 
          ? `<div style="font-size:0.85rem;color:var(--text-muted);font-style:italic;">Foundational core concept (no prerequisites).</div>`
          : `<ul class="entity-list">
              ${prerequisites.map(p => {
                const theme = getDomainTheme(p.domain);
                return `
                  <li class="entity-link" data-id="${p.id}">
                    <div style="display:flex;align-items:center;gap:8px;">
                      <span>${theme.icon}</span>
                      <span>${this.escapeHtml(p.name)}</span>
                    </div>
                    <span style="font-size:0.75rem;color:${theme.color};">Pan ➔</span>
                  </li>
                `;
              }).join('')}
             </ul>`
        }
      </div>
    `;

    // Dependents ("Enables")
    html += `
      <div class="inspector-section">
        <div class="section-title">➡️ What This Enables (${dependents.length})</div>
        ${dependents.length === 0
          ? `<div style="font-size:0.85rem;color:var(--text-muted);font-style:italic;">No downstream dependent concepts linked yet.</div>`
          : `<ul class="entity-list">
              ${dependents.map(d => {
                const theme = getDomainTheme(d.domain);
                return `
                  <li class="entity-link" data-id="${d.id}">
                    <div style="display:flex;align-items:center;gap:8px;">
                      <span>${theme.icon}</span>
                      <span>${this.escapeHtml(d.name)}</span>
                    </div>
                    <span style="font-size:0.75rem;color:${theme.color};">Pan ➔</span>
                  </li>
                `;
              }).join('')}
             </ul>`
        }
      </div>
    `;

    // Related Concepts
    if (related.length > 0) {
      html += `
        <div class="inspector-section">
          <div class="section-title">🔗 Related Concepts (${related.length})</div>
          <ul class="entity-list">
            ${related.map(r => {
              const theme = getDomainTheme(r.domain);
              return `
                <li class="entity-link" data-id="${r.id}">
                  <div style="display:flex;align-items:center;gap:8px;">
                    <span>${theme.icon}</span>
                    <span>${this.escapeHtml(r.name)}</span>
                  </div>
                  <span style="font-size:0.75rem;color:var(--text-muted);">${r.domain}</span>
                </li>
              `;
            }).join('')}
          </ul>
        </div>
      `;
    }

    // Applications
    if (entity.real_world_applications && entity.real_world_applications.length > 0) {
      html += `
        <div class="inspector-section">
          <div class="section-title">🌐 Real-World Applications</div>
          <ul style="font-size:0.9rem;color:#cbd5e1;padding-left:18px;display:flex;flex-direction:column;gap:6px;line-height:1.5;">
            ${entity.real_world_applications.map(app => `<li>${this.escapeHtml(app)}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    // Common Misconceptions
    if (entity.common_misconceptions && entity.common_misconceptions.length > 0) {
      html += `
        <div class="inspector-section">
          <div class="section-title" style="color:#fca5a5;">💡 Common Misconceptions</div>
          ${entity.common_misconceptions.map(m => `
            <div class="misconception-card">${this.escapeHtml(m)}</div>
          `).join('')}
        </div>
      `;
    }

    // Provenance
    if (entity.provenance) {
      html += `
        <div class="inspector-section">
          <div class="section-title">🔬 Provenance & Source</div>
          <div style="font-size:0.82rem;color:var(--text-secondary);display:flex;flex-direction:column;gap:4px;background:rgba(15,23,42,0.5);padding:10px;border-radius:8px;border:1px solid var(--border-glass);">
            <div>Source Standard: <strong style="color:#ffffff;">${this.escapeHtml(entity.provenance.source ?? 'Authoritative Scientific Standard')}</strong></div>
            <div>Review Status: <strong style="color:var(--accent-cyan);">${this.escapeHtml(entity.provenance.source_kind ?? 'standard')}</strong></div>
          </div>
        </div>
      `;
    }

    this.container.innerHTML = html;

    // Attach click listeners to links
    const links = this.container.querySelectorAll('.entity-link');
    links.forEach(link => {
      link.addEventListener('click', () => {
        const id = link.getAttribute('data-id');
        if (id) this.onConceptSelect(id);
      });
    });
  }

  private escapeHtml(str: string): string {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
}
