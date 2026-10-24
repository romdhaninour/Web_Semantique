import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

interface GridNode {
  id: string;
  label: string;
  type: string;
  properties: { property: string; value: string | number | boolean; kind: 'literal' | 'resource' }[];
}

interface GridEdge {
  source: string;
  target: string;
  label: string;
}

interface PositionedNode extends GridNode {
  x: number;
  y: number;
  category: string;
  radius: number;
}

interface PositionedEdge extends GridEdge {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  midX: number;
  midY: number;
}

@Component({
  selector: 'app-graph-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="page-shell">
      <div class="heading">
        <div><p class="eyebrow">DONNÉES RDF</p><h1>Graphe du réseau</h1></div>
        <div class="controls">
          <label>Rechercher un individu
            <input type="search" [(ngModel)]="searchTerm" (ngModelChange)="onFiltersChanged()" placeholder="Ex. Eolienne_Sfax1">
          </label>
          <label>Filtrer par classe
            <select [(ngModel)]="selectedType" (ngModelChange)="onFiltersChanged()">
              <option value="">Toutes les classes</option>
              <option *ngFor="let type of types" [value]="type">{{ type }}</option>
            </select>
          </label>
          <button type="button" class="refresh-button" (click)="refreshGraph()" [disabled]="loading">
            {{ loading ? 'Actualisation…' : 'Actualiser le graphe' }}
          </button>
        </div>
      </div>
      <p class="summary" *ngIf="!loading">
        {{ matchingNodeCount }} résultat(s) du filtre · {{ visibleNodes.length }} nœuds affichés avec leurs voisins ·
        {{ visibleEdges.length }} relations visibles
      </p>
      <p class="status" *ngIf="loading">Chargement du graphe RDF…</p>
      <p class="status error" *ngIf="errorMessage">{{ errorMessage }}</p>
      <div class="graph-canvas" *ngIf="!loading && !errorMessage">
        <p class="empty-state" *ngIf="!visibleNodes.length">Aucun individu ne correspond à ces filtres.</p>
        <svg *ngIf="visibleNodes.length" viewBox="0 0 1200 760"
          role="img" aria-label="Réseau RDF interactif avec individus reliés par leurs relations">
          <defs>
            <marker id="graph-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
              <path d="M0,0 L8,4 L0,8 z"></path>
            </marker>
          </defs>
          <g class="network-guides">
            <circle cx="600" cy="380" r="145"></circle>
            <circle cx="600" cy="380" r="285"></circle>
            <circle cx="600" cy="380" r="425"></circle>
          </g>
          <g class="edges">
            <g *ngFor="let edge of visibleEdges; trackBy: trackEdge"
              class="graph-edge"
              [class.highlighted]="isConnectedToSelection(edge)"
              [class.dimmed]="selectedNode && !isConnectedToSelection(edge)">
              <line [attr.x1]="edge.x1" [attr.y1]="edge.y1"
                [attr.x2]="edge.x2" [attr.y2]="edge.y2"
                marker-end="url(#graph-arrow)">
                <title>{{ edgeDescription(edge) }}</title>
              </line>
              <text [attr.x]="edge.midX" [attr.y]="edge.midY">{{ edge.label }}</text>
            </g>
          </g>
          <g>
            <g *ngFor="let node of visibleNodes; trackBy: trackNode" class="graph-node"
              [class.selected]="selectedNode?.id === node.id"
              [class.neighbor]="isNeighbor(node)"
              [class.filter-match]="isFilterMatch(node)"
              [class.dimmed]="selectedNode && !isInSelectionNeighborhood(node)"
              (click)="selectNode(node)"
              [attr.transform]="'translate(' + node.x + ' ' + node.y + ')'">
              <circle [attr.r]="node.radius" [attr.fill]="colorFor(node.type)"></circle>
              <text [attr.x]="node.radius + 7" y="4">{{ node.label }}</text>
              <title>{{ node.label }} — {{ node.type }}. Cliquez pour consulter les propriétés.</title>
            </g>
          </g>
        </svg>
      </div>
      <section class="node-details" *ngIf="selectedNode as node">
        <div>
          <p class="eyebrow">INDIVIDU SÉLECTIONNÉ</p>
          <h2>{{ node.label }}</h2>
          <p class="node-type">{{ node.type }}</p>
        </div>
        <p *ngIf="!node.properties.length" class="empty-properties">Aucune propriété enregistrée.</p>
        <dl *ngIf="node.properties.length">
          <div *ngFor="let property of node.properties; trackBy: trackProperty">
            <dt>{{ property.property }}</dt>
            <dd>{{ property.value }}</dd>
          </div>
        </dl>
      </section>
      <div class="legend" aria-label="Légende des familles de ressources">
        <span><i class="production"></i>Production</span>
        <span><i class="storage"></i>Stockage</span>
        <span><i class="network"></i>Réseau</span>
        <span><i class="consumption"></i>Consommation</span>
        <span><i class="other"></i>Autres</span>
      </div>
      <p class="hint">Chaque cercle représente un individu; chaque flèche représente une relation RDF. Les couleurs indiquent la famille des ressources et la taille du cercle reflète le nombre de connexions. Un filtre conserve ses résultats et les individus reliés afin de garder les flèches visibles. Survolez un nœud ou un lien pour afficher son libellé; cliquez pour fixer la sélection et consulter ses propriétés.</p>
    </section>
  `,
  styleUrls: ['./graph.scss']
})
export class GraphPageComponent implements OnInit {
  graph: { nodes: GridNode[]; edges: GridEdge[] } = { nodes: [], edges: [] };
  selectedType = '';
  searchTerm = '';
  selectedNode: GridNode | null = null;
  loading = true;
  errorMessage = '';
  private cachedLayoutKey = '';
  private cachedLayout: { nodes: PositionedNode[]; edges: PositionedEdge[] } = { nodes: [], edges: [] };
  private nodePositions = new Map<string, PositionedNode>();
  private matchingIds = new Set<string>();

  constructor(private api: ApiService, private changeDetector: ChangeDetectorRef) {}

  get types(): string[] {
    return [...new Set(this.graph.nodes.map((node) => node.type))].sort();
  }

  private get layout(): { nodes: PositionedNode[]; edges: PositionedEdge[] } {
    const query = this.searchTerm.trim().toLocaleLowerCase();
    const key = `${this.selectedType}|${query}|${this.graph.nodes.length}|${this.graph.edges.length}`;
    if (key === this.cachedLayoutKey) return this.cachedLayout;

    const matches = this.graph.nodes
      .filter((node) => !this.selectedType || node.type === this.selectedType)
      .filter((node) => !query || node.label.toLocaleLowerCase().includes(query));
    const hasFilter = Boolean(this.selectedType || query);
    this.matchingIds = new Set(matches.map((node) => node.id));
    const edges = hasFilter
      ? this.graph.edges.filter((edge) => this.matchingIds.has(edge.source) || this.matchingIds.has(edge.target))
      : this.graph.edges;
    const visibleIds = new Set(matches.map((node) => node.id));
    for (const edge of edges) {
      visibleIds.add(edge.source);
      visibleIds.add(edge.target);
    }
    const nodes = this.graph.nodes
      .filter((node) => visibleIds.has(node.id))
      .map((node) => ({ ...node, category: this.categoryFor(node.type), x: 0, y: 0, radius: 11 }));
    const positioned = this.forceLayout(nodes, edges);
    const positions = new Map(positioned.map((node) => [node.id, node]));
    const degree = new Map<string, number>();
    for (const edge of edges) {
      degree.set(edge.source, (degree.get(edge.source) ?? 0) + 1);
      degree.set(edge.target, (degree.get(edge.target) ?? 0) + 1);
    }
    for (const node of positioned) {
      node.radius = Math.min(18, 9 + (degree.get(node.id) ?? 0) * 1.2);
    }
    this.cachedLayout = {
      nodes: positioned,
      edges: edges.map((edge) => {
        const source = positions.get(edge.source);
        const target = positions.get(edge.target);
        if (!source || !target) {
          return { ...edge, x1: 0, y1: 0, x2: 0, y2: 0, midX: 0, midY: 0 };
        }
        const dx = target.x - source.x;
        const dy = target.y - source.y;
        const distance = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
        const unitX = dx / distance;
        const unitY = dy / distance;
        return {
          ...edge,
          x1: source.x + unitX * source.radius,
          y1: source.y + unitY * source.radius,
          x2: target.x - unitX * (target.radius + 4),
          y2: target.y - unitY * (target.radius + 4),
          midX: (source.x + target.x) / 2,
          midY: (source.y + target.y) / 2,
        };
      }),
    };
    this.cachedLayoutKey = key;
    this.nodePositions = positions;
    return this.cachedLayout;
  }

  get visibleNodes(): PositionedNode[] {
    return this.layout.nodes;
  }

  get visibleEdges(): PositionedEdge[] {
    return this.layout.edges;
  }

  get matchingNodeCount(): number {
    this.layout;
    return this.matchingIds.size;
  }

  ngOnInit(): void {
    this.refreshGraph();
  }

  refreshGraph(): void {
    this.loading = true;
    this.errorMessage = '';
    this.api.getGraph().subscribe({
      next: (graph) => {
        this.graph = graph;
        this.cachedLayoutKey = '';
        this.matchingIds.clear();
        this.selectedNode = this.selectedNode
          ? graph.nodes.find((node) => node.id === this.selectedNode?.id) ?? null
          : null;
        this.loading = false;
        this.changeDetector.markForCheck();
      },
      error: () => {
        this.loading = false;
        this.errorMessage = 'Impossible de charger le graphe RDF. Vérifiez que l’API est disponible.';
        this.changeDetector.markForCheck();
      }
    });
  }

  positionFor(id: string): PositionedNode | undefined {
    return this.nodePositions.get(id);
  }

  edgeDescription(edge: GridEdge): string {
    const source = this.graph.nodes.find((node) => node.id === edge.source)?.label ?? edge.source;
    const target = this.graph.nodes.find((node) => node.id === edge.target)?.label ?? edge.target;
    return `${source} — ${edge.label} → ${target}`;
  }

  selectNode(node: GridNode): void {
    this.selectedNode = node;
  }

  onFiltersChanged(): void {
    this.selectedNode = null;
    this.cachedLayoutKey = '';
  }

  isFilterMatch(node: GridNode): boolean {
    this.layout;
    return this.matchingIds.has(node.id);
  }

  isConnectedToSelection(edge: GridEdge): boolean {
    return this.selectedNode !== null
      && (edge.source === this.selectedNode.id || edge.target === this.selectedNode.id);
  }

  isNeighbor(node: GridNode): boolean {
    return this.selectedNode !== null && this.graph.edges.some((edge) =>
      (edge.source === this.selectedNode?.id && edge.target === node.id)
      || (edge.target === this.selectedNode?.id && edge.source === node.id));
  }

  isInSelectionNeighborhood(node: GridNode): boolean {
    return this.selectedNode?.id === node.id || this.isNeighbor(node);
  }

  trackNode(_index: number, node: GridNode): string {
    return node.id;
  }

  trackEdge(_index: number, edge: GridEdge): string {
    return `${edge.source}-${edge.label}-${edge.target}`;
  }

  private forceLayout(nodes: PositionedNode[], edges: GridEdge[]): PositionedNode[] {
    const width = 1200;
    const height = 760;
    const centerX = width / 2;
    const centerY = height / 2;
    const count = nodes.length;
    if (!count) return [];

    const positions = nodes.map((node, index) => {
      const angle = index * 2.399963229728653;
      const radius = 55 + Math.sqrt(index / count) * 260;
      return {
        ...node,
        x: centerX + Math.cos(angle) * radius,
        y: centerY + Math.sin(angle) * radius * 0.72,
      };
    });
    const indexById = new Map(positions.map((node, index) => [node.id, index]));
    const links = edges.flatMap((edge) => {
      const source = indexById.get(edge.source);
      const target = indexById.get(edge.target);
      return source === undefined || target === undefined ? [] : [{ source, target }];
    });

    for (let iteration = 0; iteration < 150; iteration++) {
      const forces = positions.map(() => ({ x: 0, y: 0 }));
      for (let left = 0; left < count; left++) {
        for (let right = left + 1; right < count; right++) {
          const dx = positions[left].x - positions[right].x;
          const dy = positions[left].y - positions[right].y;
          const distanceSquared = Math.max(dx * dx + dy * dy, 25);
          const force = 6200 / distanceSquared;
          const fx = (dx / Math.sqrt(distanceSquared)) * force;
          const fy = (dy / Math.sqrt(distanceSquared)) * force;
          forces[left].x += fx;
          forces[left].y += fy;
          forces[right].x -= fx;
          forces[right].y -= fy;
        }
      }
      for (const link of links) {
        const dx = positions[link.target].x - positions[link.source].x;
        const dy = positions[link.target].y - positions[link.source].y;
        const distance = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
        const force = (distance - 155) * 0.014;
        const fx = (dx / distance) * force;
        const fy = (dy / distance) * force;
        forces[link.source].x += fx;
        forces[link.source].y += fy;
        forces[link.target].x -= fx;
        forces[link.target].y -= fy;
      }
      for (let index = 0; index < count; index++) {
        forces[index].x += (centerX - positions[index].x) * 0.008;
        forces[index].y += (centerY - positions[index].y) * 0.008;
        positions[index].x = Math.max(38, Math.min(width - 38, positions[index].x + forces[index].x));
        positions[index].y = Math.max(38, Math.min(height - 38, positions[index].y + forces[index].y));
      }
    }
    return positions;
  }

  trackProperty(_index: number, property: GridNode['properties'][number]): string {
    return `${property.property}-${property.value}`;
  }

  private categoryFor(type: string): string {
    const name = type.toLocaleLowerCase();
    if (name.includes('batterie') || name.includes('stockage')) return 'storage';
    if (name.includes('ligne') || name.includes('tension') || name.includes('compteur')
      || name.includes('onduleur') || name.includes('gestionnaire') || name.includes('station')) return 'network';
    if (name.includes('batiment') || name.includes('industriel') || name.includes('residentiel')
      || name.includes('tertiaire')) return 'consumption';
    if (name.includes('source') || name.includes('eolienne') || name.includes('solaire')) return 'production';
    return 'other';
  }

  colorFor(type: string): string {
    const colors: Record<string, string> = {
      production: '#27835f',
      storage: '#e89a28',
      network: '#3975a5',
      consumption: '#7657a8',
      other: '#507080',
    };
    return colors[this.categoryFor(type)];
  }
}
