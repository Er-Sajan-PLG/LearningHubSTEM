export type ExplorerMode = 'explore' | 'domain' | 'topic' | 'prerequisites' | 'curriculum';

export interface ExplorerState {
  selectedConceptId: string | null;
  activeMode: ExplorerMode;
  domainFilter: string;
  relationshipFilter: string;
  searchQuery: string;
  viewMode: '3d' | 'list';
}

type StateListener = (state: ExplorerState) => void;

export class ExplorerStateManager {
  private state: ExplorerState;
  private listeners: Set<StateListener> = new Set();

  constructor() {
    this.state = this.readFromUrl();
    window.addEventListener('popstate', () => {
      this.state = this.readFromUrl();
      this.notify();
    });
  }

  public getState(): ExplorerState {
    return { ...this.state };
  }

  public subscribe(listener: StateListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  public setState(updates: Partial<ExplorerState>): void {
    this.state = { ...this.state, ...updates };
    this.syncToUrl();
    this.notify();
  }

  public selectConcept(id: string | null): void {
    this.setState({ selectedConceptId: id });
  }

  public setMode(mode: ExplorerMode): void {
    this.setState({ activeMode: mode });
  }

  public setDomainFilter(domain: string): void {
    this.setState({ domainFilter: domain });
  }

  public setRelationshipFilter(relationship: string): void {
    this.setState({ relationshipFilter: relationship });
  }

  public setSearchQuery(query: string): void {
    this.setState({ searchQuery: query });
  }

  public resetFilters(): void {
    this.setState({
      domainFilter: 'all',
      relationshipFilter: 'all',
      searchQuery: '',
      activeMode: 'explore',
      viewMode: '3d'
    });
  }

  private notify(): void {
    for (const listener of this.listeners) {
      listener(this.getState());
    }
  }

  private readFromUrl(): ExplorerState {
    const params = new URLSearchParams(window.location.search);
    const concept = params.get('concept');
    const mode = (params.get('mode') as ExplorerMode) ?? 'explore';
    const domain = params.get('domain') ?? 'all';
    const rel = params.get('rel') ?? 'all';
    const view = (params.get('view') as '3d' | 'list') ?? '3d';

    return {
      selectedConceptId: concept,
      activeMode: mode,
      domainFilter: domain,
      relationshipFilter: rel,
      searchQuery: '',
      viewMode: view
    };
  }

  private syncToUrl(): void {
    const params = new URLSearchParams();
    if (this.state.selectedConceptId) {
      params.set('concept', this.state.selectedConceptId);
    }
    if (this.state.activeMode !== 'explore') {
      params.set('mode', this.state.activeMode);
    }
    if (this.state.domainFilter !== 'all') {
      params.set('domain', this.state.domainFilter);
    }
    if (this.state.relationshipFilter !== 'all') {
      params.set('rel', this.state.relationshipFilter);
    }
    if (this.state.viewMode !== '3d') {
      params.set('view', this.state.viewMode);
    }

    const newUrl = `${window.location.pathname}${params.toString() ? '?' + params.toString() : ''}`;
    if (newUrl !== `${window.location.pathname}${window.location.search}`) {
      window.history.pushState(null, '', newUrl);
    }
  }
}
