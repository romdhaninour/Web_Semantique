import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-home-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <section class="page-shell">
      <h1>Smart Grid Sémantique</h1>
      <p class="subtitle">Supervision énergétique Tunisienne — données RDF, sources, lignes et consommations</p>
      <p class="error" *ngIf="errorMessage">{{ errorMessage }}</p>

      <div class="stats-grid">
        <div class="stat-card" *ngFor="let stat of stats">
          <div class="label">{{ stat.label }}</div>
          <div class="value">{{ stat.value }}</div>
        </div>
      </div>

      <div class="two-col">
        <div class="panel">
          <h2>Classes du graphe</h2>
          <ul>
            <li *ngFor="let item of classes | slice:0:8">
              <span class="dot" [style.background]="colorFor(item.name)"></span>
              {{ item.name }} <strong>{{ item.count }}</strong>
            </li>
          </ul>
        </div>
        <div class="panel">
          <h2>Actions rapides</h2>
          <div class="quick-links">
            <a routerLink="/ask">Questionner la grille</a>
            <a routerLink="/explorer">Explorer</a>
            <a routerLink="/graph">Graphique</a>
            <a routerLink="/admin">CRUD & SPARQL</a>
          </div>
        </div>
      </div>
    </section>
  `,
  styleUrls: ['./home.scss']
})
export class HomePageComponent implements OnInit {
  stats: any[] = [];
  classes: any[] = [];
  errorMessage = '';

  constructor(private api: ApiService, private changeDetector: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.api.getStats().subscribe((stats) => {
      this.stats = [
        { label: 'Individus', value: stats.individuals },
        { label: 'Classes', value: stats.classes },
        { label: 'Capacité totale', value: `${stats.total_capacity_kw} kW` },
        { label: 'Consommation', value: `${stats.total_consumption_kwh} kWh` },
      ];
      this.changeDetector.markForCheck();
    }, () => {
      this.errorMessage = 'Impossible de charger les statistiques du graphe. Vérifiez que l’application est démarrée avec le lanceur.';
      this.changeDetector.markForCheck();
    });
    this.api.getClasses().subscribe((classes) => {
      this.classes = classes;
      this.changeDetector.markForCheck();
    }, () => {
      this.errorMessage = 'Impossible de charger les classes de l’ontologie.';
      this.changeDetector.markForCheck();
    });
  }

  colorFor(name: string): string {
    const colors: Record<string, string> = {
      SourceEnergie: '#52B788',
      UniteStockage: '#F4A300',
      BatimentConsommateur: '#1B4332',
      LigneTransport: '#3A5A78',
      Compteur: '#8E6C88',
      Onduleur: '#8E6C88',
      GestionnaireReseau: '#8E6C88'
    };
    return colors[name] || '#0D1B2A';
  }
}
