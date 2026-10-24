import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, ClassSummary, Individual } from '../../services/api.service';

@Component({
  selector: 'app-explorer-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="page-shell">
      <div>
        <p class="eyebrow">EXPLORATION RDF</p>
        <h1>Explorer le réseau</h1>
        <p class="subtitle">Parcourez les individus et leurs propriétés dans le graphe sémantique.</p>
      </div>

      <div class="toolbar">
        <label>Classe
          <select [(ngModel)]="selectedClass" (change)="loadClass()">
            <option value="">Toutes les classes</option>
            <option *ngFor="let classItem of classes" [value]="classItem.name">
              {{ classItem.name }} ({{ classItem.count }})
            </option>
          </select>
        </label>
        <label class="search">Recherche
          <input [(ngModel)]="searchText" placeholder="Nom ou valeur de propriété…" />
        </label>
        <span class="result-count">{{ filteredIndividuals.length }} ressource(s)</span>
      </div>

      <p class="status error" *ngIf="errorMessage">{{ errorMessage }}</p>
      <p class="status" *ngIf="loading">Chargement du graphe…</p>

      <div class="explorer-layout">
        <div class="list-grid">
          <button class="resource-card" *ngFor="let item of filteredIndividuals"
            [class.selected]="selected?.id === item.id" (click)="select(item)">
            <strong>{{ item.id }}</strong>
            <span>{{ item.types.join(' · ') }} — {{ item.properties.length }} propriétés</span>
            <small>{{ summary(item) }}</small>
          </button>
          <p class="empty" *ngIf="!loading && filteredIndividuals.length === 0">Aucune ressource ne correspond à votre recherche.</p>
        </div>

        <aside class="detail-panel" *ngIf="selected">
          <div class="detail-heading">
            <div><p class="eyebrow">INDIVIDU</p><h2>{{ selected.id }}</h2></div>
            <button class="close" type="button" (click)="selected = null" aria-label="Fermer le détail">×</button>
          </div>
          <p class="property-count">{{ selected.properties.length }} propriété(s) RDF</p>
          <dl>
            <div *ngFor="let property of selected.properties">
              <dt>{{ property.property }}</dt>
              <dd>{{ property.value }}</dd>
            </div>
          </dl>
        </aside>
      </div>
    </section>
  `,
  styleUrls: ['./explorer.scss']
})
export class ExplorerPageComponent implements OnInit {
  classes: ClassSummary[] = [];
  individuals: Individual[] = [];
  selectedClass = '';
  searchText = '';
  selected: Individual | null = null;
  loading = false;
  errorMessage = '';

  constructor(private api: ApiService, private changeDetector: ChangeDetectorRef) {}

  get filteredIndividuals(): Individual[] {
    const needle = this.searchText.trim().toLocaleLowerCase();
    if (!needle) return this.individuals;
    return this.individuals.filter((item) =>
      item.id.toLocaleLowerCase().includes(needle) ||
      item.types.some((type) => type.toLocaleLowerCase().includes(needle)) ||
      item.properties.some((property) =>
        property.property.toLocaleLowerCase().includes(needle) ||
        String(property.value).toLocaleLowerCase().includes(needle)
      )
    );
  }

  ngOnInit(): void {
    this.api.getClasses().subscribe({
      next: (classes) => {
        this.classes = classes;
        this.changeDetector.markForCheck();
      },
      error: () => {
        this.errorMessage = 'Impossible de charger les classes. Vérifiez que le serveur est démarré.';
        this.changeDetector.markForCheck();
      }
    });
    this.loadClass();
  }

  loadClass(): void {
    this.loading = true;
    this.errorMessage = '';
    this.selected = null;
    this.api.getIndividuals(this.selectedClass || undefined).subscribe({
      next: (items) => {
        this.individuals = items;
        this.loading = false;
        this.changeDetector.markForCheck();
      },
      error: () => {
        this.individuals = [];
        this.loading = false;
        this.errorMessage = 'Impossible de charger les individus depuis le graphe.';
        this.changeDetector.markForCheck();
      }
    });
  }

  select(item: Individual): void {
    this.selected = item;
  }

  summary(item: Individual): string {
    const label = item.properties.find((property) => property.property === 'nom' || property.property === 'name');
    return label ? String(label.value) : 'Ouvrir les propriétés';
  }
}
