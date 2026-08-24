import { ExplorerState, ExplorerMode } from '../state/explorer-state';

export interface SearchFilterBarOptions {
  container: HTMLElement;
  onSearch: (query: string) => void;
  onDomainChange: (domain: string) => void;
  onRelationshipChange: (rel: string) => void;
  onModeChange: (mode: ExplorerMode) => void;
  onReset: () => void;
}

export class SearchFilterBar {
  private container: HTMLElement;
  private options: SearchFilterBarOptions;
  private debounceTimer: number | null = null;

  constructor(options: SearchFilterBarOptions) {
    this.container = options.container;
    this.options = options;
    this.render();
  }

  public render(): void {
    this.container.innerHTML = `
      <div class="explorer-header">
        <div class="brand-title">
          <div class="brand-logo"></div>
          <span>LearningHubSTEM <span style="font-weight:400;color:var(--text-muted);font-size:0.85rem;">3D Explorer</span></span>
        </div>

        <div class="toolbar-controls">
          <input type="text" id="searchInput" class="search-input" placeholder="Search concepts (e.g. force)..." />

          <select id="domainSelect" class="select-control">
            <option value="all">All Domains</option>
            <option value="physics">Physics</option>
            <option value="chemistry">Chemistry</option>
            <option value="biology">Biology</option>
            <option value="earth-space">Earth & Space</option>
            <option value="scientific-practice">Practices</option>
            <option value="engineering">Engineering</option>
          </select>

          <select id="relSelect" class="select-control">
            <option value="all">All Relationships</option>
            <option value="logically_requires">Prerequisites (Logical)</option>
            <option value="mathematically_requires">Prerequisites (Math)</option>
            <option value="part_of">Part Of</option>
            <option value="special_case_of">Special Case Of</option>
            <option value="related_to">Related</option>
          </select>

          <div class="mode-btn-group">
            <button class="mode-btn active" data-mode="explore">Explore</button>
            <button class="mode-btn" data-mode="prerequisites">Prereqs</button>
            <button class="mode-btn" data-mode="domain">Domain</button>
          </div>

          <button id="resetBtn" class="action-btn">Reset View</button>
        </div>
      </div>
    `;

    this.attachEvents();
  }

  public updateState(state: ExplorerState): void {
    const searchInput = this.container.querySelector('#searchInput') as HTMLInputElement;
    if (searchInput && searchInput.value !== state.searchQuery) {
      searchInput.value = state.searchQuery;
    }

    const domainSelect = this.container.querySelector('#domainSelect') as HTMLSelectElement;
    if (domainSelect) domainSelect.value = state.domainFilter;

    const relSelect = this.container.querySelector('#relSelect') as HTMLSelectElement;
    if (relSelect) relSelect.value = state.relationshipFilter;

    const modeBtns = this.container.querySelectorAll('.mode-btn');
    modeBtns.forEach(btn => {
      const mode = btn.getAttribute('data-mode');
      if (mode === state.activeMode) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }

  private attachEvents(): void {
    const searchInput = this.container.querySelector('#searchInput') as HTMLInputElement;
    if (searchInput) {
      searchInput.addEventListener('input', () => {
        if (this.debounceTimer) window.clearTimeout(this.debounceTimer);
        this.debounceTimer = window.setTimeout(() => {
          this.options.onSearch(searchInput.value.trim());
        }, 200);
      });
    }

    const domainSelect = this.container.querySelector('#domainSelect') as HTMLSelectElement;
    if (domainSelect) {
      domainSelect.addEventListener('change', () => {
        this.options.onDomainChange(domainSelect.value);
      });
    }

    const relSelect = this.container.querySelector('#relSelect') as HTMLSelectElement;
    if (relSelect) {
      relSelect.addEventListener('change', () => {
        this.options.onRelationshipChange(relSelect.value);
      });
    }

    const modeBtns = this.container.querySelectorAll('.mode-btn');
    modeBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const mode = btn.getAttribute('data-mode') as ExplorerMode;
        if (mode) this.options.onModeChange(mode);
      });
    });

    const resetBtn = this.container.querySelector('#resetBtn') as HTMLButtonElement;
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        this.options.onReset();
      });
    }
  }
}
