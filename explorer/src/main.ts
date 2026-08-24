import './styles/explorer.css';
import { loadKnowledgeExport, LhsKnowledgeExport } from './services/knowledge-export-loader';
import { projectKnowledgeGraph } from './services/graph-projection';
import { getConceptDetails } from './services/concept-data';
import { ExplorerStateManager, ExplorerState } from './state/explorer-state';
import { GraphView } from './components/graph-view';
import { ConceptInspectorView } from './components/concept-inspector-view';
import { SearchFilterBar } from './components/search-filter-bar';
import { AccessibleListView } from './components/accessible-list-view';

class ExplorerApp {
  private stateManager: ExplorerStateManager;
  private exportData: LhsKnowledgeExport | null = null;
  private graphView: GraphView | null = null;
  private inspectorView: ConceptInspectorView | null = null;
  private searchFilterBar: SearchFilterBar | null = null;
  private accessibleListView: AccessibleListView | null = null;

  constructor() {
    this.stateManager = new ExplorerStateManager();
  }

  public async start(): Promise<void> {
    this.showLoading(true);

    try {
      // Try /exports/knowledge.json first, then relative fallback
      try {
        this.exportData = await loadKnowledgeExport('/exports/knowledge.json');
      } catch (err) {
        console.warn('Primary fetch /exports/knowledge.json failed, trying ./exports/knowledge.json...', err);
        this.exportData = await loadKnowledgeExport('./exports/knowledge.json');
      }
      
      this.showLoading(false);
      this.initUI();
    } catch (err) {
      console.error('Failed to load LearningHubSTEM knowledge export:', err);
      this.showLoading(false);
      this.showError((err as Error).message);
    }
  }

  private initUI(): void {
    if (!this.exportData) return;

    // 1. Init Toolbar
    const toolbarContainer = document.getElementById('toolbar')!;
    this.searchFilterBar = new SearchFilterBar({
      container: toolbarContainer,
      onSearch: (q) => this.stateManager.setSearchQuery(q),
      onDomainChange: (d) => this.stateManager.setDomainFilter(d),
      onRelationshipChange: (r) => this.stateManager.setRelationshipFilter(r),
      onModeChange: (m) => this.stateManager.setMode(m),
      onViewToggle: (v) => this.stateManager.setState({ viewMode: v }),
      onReset: () => {
        this.stateManager.resetFilters();
        if (this.graphView) this.graphView.resetView();
      }
    });

    // 2. Init 3D Graph View
    const graphContainer = document.getElementById('graphCanvas')!;
    try {
      this.graphView = new GraphView({
        container: graphContainer,
        onNodeSelect: (id) => this.stateManager.selectConcept(id)
      });
    } catch (err) {
      console.error('Failed to initialize 3D Force Graph WebGL context:', err);
      this.showError(`WebGL/3D Renderer Error: ${(err as Error).message}. You can switch to accessible list mode.`);
    }

    // 3. Init Inspector View
    const inspectorContainer = document.getElementById('inspector')!;
    this.inspectorView = new ConceptInspectorView({
      container: inspectorContainer,
      onConceptSelect: (id) => this.stateManager.selectConcept(id)
    });

    // 4. Init Accessible List View
    const listContainer = document.getElementById('accessibleList')!;
    this.accessibleListView = new AccessibleListView({
      container: listContainer,
      onConceptSelect: (id) => this.stateManager.selectConcept(id)
    });

    // 5. Subscribe to State Changes
    this.stateManager.subscribe(state => this.onStateChange(state));

    // Initial State Sync
    this.onStateChange(this.stateManager.getState());
  }

  private onStateChange(state: ExplorerState): void {
    if (!this.exportData || !this.inspectorView || !this.searchFilterBar || !this.accessibleListView) {
      return;
    }

    this.searchFilterBar.updateState(state);

    // Toggle 3D graph vs accessible list pane based on viewMode
    const graphPane = document.getElementById('graphCanvas')!;
    const listPane = document.getElementById('accessibleList')!;
    const useList = state.viewMode === 'list';
    graphPane.style.display = useList ? 'none' : 'block';
    listPane.style.display = useList ? 'block' : 'none';

    // Filter entities for search
    let matchingEntities = this.exportData.entities;
    if (state.searchQuery) {
      const q = state.searchQuery.toLowerCase();
      matchingEntities = matchingEntities.filter(
        e => e.name.toLowerCase().includes(q) || e.id.toLowerCase().includes(q) || e.definition.toLowerCase().includes(q)
      );
    }

    // Projection
    const projection = projectKnowledgeGraph(
      { ...this.exportData, entities: matchingEntities },
      state.domainFilter,
      state.relationshipFilter,
      state.activeMode
    );

    if (!useList && this.graphView) {
      this.graphView.updateProjection(projection, state.selectedConceptId);
    }

    this.accessibleListView.render(matchingEntities, state.selectedConceptId);

    // Update Inspector
    if (state.selectedConceptId) {
      try {
        const details = getConceptDetails(state.selectedConceptId, this.exportData);
        this.inspectorView.renderDetails(details);
      } catch (err) {
        this.inspectorView.renderEmpty();
      }
    } else {
      this.inspectorView.renderEmpty();
    }
  }

  private showLoading(show: boolean): void {
    const el = document.getElementById('loadingOverlay');
    if (el) el.style.display = show ? 'flex' : 'none';
  }

  private showError(msg: string): void {
    const overlay = document.getElementById('errorOverlay');
    const msgEl = document.getElementById('errorMessage');
    const retryBtn = document.getElementById('retryBtn');

    if (msgEl) msgEl.innerText = msg;
    if (overlay) overlay.style.display = 'flex';

    if (retryBtn) {
      retryBtn.onclick = () => {
        if (overlay) overlay.style.display = 'none';
        this.start();
      };
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const app = new ExplorerApp();
  app.start();
});
