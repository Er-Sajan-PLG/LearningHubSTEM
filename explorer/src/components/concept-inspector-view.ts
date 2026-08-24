import { ConceptDetails } from '../services/concept-data';
import { getDomainTheme } from '../styles/theme';

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
        <h3 style="font-size:1.1rem;color:#ffffff;">Explore LearningHubSTEM</h3>
        <p style="font-size:0.9rem;line-height:1.5;">Select any concept in the 3D graph or search for one above.</p>
        <div style="font-size:0.82rem;text-align:left;background:rgba(255,255,255,0.03);padding:12px;border-radius:8px;border:1px solid rgba(255,255,255,0.08);margin-top:12px;width:100%;">
          <div style="font-weight:600;margin-bottom:6px;color:#9ca3af;">Explore canonical details:</div>
          <div>• Definitions & Equations</div>
          <div>• Learning Prerequisites & Dependents</div>
          <div>• Real-World Applications</div>
          <div>• Common Misconceptions</div>
          <div>• Provenance & Research Sources</div>
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
            ${domainTheme.name}
          </span>
          <span class="type-badge">${entity.type}</span>
          <span class="type-badge" style="color:#34d399;">${entity.status}</span>
        </div>
        <h2 class="concept-title">${this.escapeHtml(entity.name)}</h2>
        <div class="concept-id">${this.escapeHtml(entity.id)}</div>
      </div>

      <div class="inspector-section">
        <div class="section-title">Definition</div>
        <div class="definition-text">${this.escapeHtml(entity.definition)}</div>
      </div>
    `;

    if (entity.equation) {
      html += `
        <div class="inspector-section">
          <div class="section-title">Mathematical Formula</div>
          <div class="equation-box">${this.escapeHtml(entity.equation)}</div>
        </div>
      `;
    }

    if (entity.symbol || entity.unit) {
      html += `
        <div class="inspector-section">
          <div class="section-title">Properties</div>
          <div style="display:flex;gap:12px;font-size:0.88rem;">
            ${entity.symbol ? `<div><span style="color:#9ca3af;">Symbol:</span> <strong>${this.escapeHtml(entity.symbol)}</strong></div>` : ''}
            ${entity.unit ? `<div><span style="color:#9ca3af;">Unit:</span> <strong>${this.escapeHtml(entity.unit)}</strong></div>` : ''}
          </div>
        </div>
      `;
    }

    // Prerequisites
    html += `
      <div class="inspector-section">
        <div class="section-title">Learning Prerequisites (${prerequisites.length})</div>
        ${prerequisites.length === 0 
          ? `<div style="font-size:0.85rem;color:#9ca3af;font-style:italic;">This is a foundational concept (no prior prerequisites).</div>`
          : `<ul class="entity-list">
              ${prerequisites.map(p => `
                <li class="entity-link" data-id="${p.id}">
                  <span>${this.escapeHtml(p.name)}</span>
                  <span style="font-size:0.75rem;color:#9ca3af;">${p.domain}</span>
                </li>
              `).join('')}
             </ul>`
        }
      </div>
    `;

    // Dependents ("What this enables")
    html += `
      <div class="inspector-section">
        <div class="section-title">What This Enables (${dependents.length})</div>
        ${dependents.length === 0
          ? `<div style="font-size:0.85rem;color:#9ca3af;font-style:italic;">No dependent concepts linked yet.</div>`
          : `<ul class="entity-list">
              ${dependents.map(d => `
                <li class="entity-link" data-id="${d.id}">
                  <span>${this.escapeHtml(d.name)}</span>
                  <span style="font-size:0.75rem;color:#9ca3af;">${d.domain}</span>
                </li>
              `).join('')}
             </ul>`
        }
      </div>
    `;

    // Related Concepts
    if (related.length > 0) {
      html += `
        <div class="inspector-section">
          <div class="section-title">Related Concepts (${related.length})</div>
          <ul class="entity-list">
            ${related.map(r => `
              <li class="entity-link" data-id="${r.id}">
                <span>${this.escapeHtml(r.name)}</span>
                <span style="font-size:0.75rem;color:#9ca3af;">${r.domain}</span>
              </li>
            `).join('')}
          </ul>
        </div>
      `;
    }

    // Applications
    if (entity.real_world_applications && entity.real_world_applications.length > 0) {
      html += `
        <div class="inspector-section">
          <div class="section-title">Applications</div>
          <ul style="font-size:0.88rem;color:#d1d5db;padding-left:18px;display:flex;flex-direction:column;gap:4px;">
            ${entity.real_world_applications.map(app => `<li>${this.escapeHtml(app)}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    // Common Misconceptions
    if (entity.common_misconceptions && entity.common_misconceptions.length > 0) {
      html += `
        <div class="inspector-section">
          <div class="section-title" style="color:#fca5a5;">Common Misconceptions</div>
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
          <div class="section-title">Research Provenance</div>
          <div style="font-size:0.8rem;color:#9ca3af;display:flex;flex-direction:column;gap:4px;">
            <div>Source: <strong>${this.escapeHtml(entity.provenance.source ?? 'Authoritative Scientific Standard')}</strong></div>
            <div>Source Kind: <strong>${this.escapeHtml(entity.provenance.source_kind ?? 'standard')}</strong></div>
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
