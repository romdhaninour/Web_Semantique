import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-home-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <section class="page-shell home-dashboard">
      <div class="page-heading">
        <div>
          <p class="eyebrow"><span></span> TABLEAU DE BORD ÉNERGÉTIQUE · TUNISIE</p>
          <h1>Le réseau, <em>en clair.</em></h1>
          <p class="subtitle">Explorez les équipements, les flux et les connaissances de votre graphe énergétique.</p>
        </div>
        <div class="heading-meta"><span class="meta-dot"></span> SYNCHRONISÉ AVEC LE GRAPHE RDF</div>
      </div>
      <p class="error" *ngIf="errorMessage">{{ errorMessage }}</p>

      <section class="energy-banner">
        <div class="banner-copy">
          <div class="banner-kicker"><span class="kicker-line"></span> VUE SÉMANTIQUE DU RÉSEAU</div>
          <h2>De la donnée à<br><span>l’intelligence énergétique.</span></h2>
          <p>Unifiez production, stockage et consommation dans un réseau de connaissances interrogeable.</p>
          <a class="banner-action" routerLink="/graph">Explorer le graphe <span aria-hidden="true">↗</span></a>
        </div>
        <div class="energy-visual" aria-label="Illustration des ressources reliées dans le graphe énergétique">
          <div class="visual-orbit orbit-one"></div>
          <div class="visual-orbit orbit-two"></div>
          <svg class="energy-lines" viewBox="0 0 460 260" fill="none" aria-hidden="true">
            <path d="M80 135 179 74l99 61 93-79M80 135l102 87 96-87 93 72M179 74l3 148M278 135l93-79M278 135l93 72" />
            <path class="flow-line" d="M80 135 179 74l99 61 93-79M80 135l102 87 96-87 93 72" />
          </svg>
          <div class="energy-node node-wind"><span>↗</span><small>PRODUCTION</small></div>
          <div class="energy-node node-grid"><span>ϟ</span><small>RÉSEAU RDF</small></div>
          <div class="energy-node node-solar"><span>☼</span><small>SOLAIRE</small></div>
          <div class="energy-node node-storage"><span>▥</span><small>STOCKAGE</small></div>
          <div class="energy-node node-home"><span>⌂</span><small>USAGES</small></div>
          <div class="visual-caption"><span></span> FLUX DE CONNAISSANCE <b>·</b> SPARQL</div>
        </div>
      </section>

      <div class="stats-grid">
        <div class="stat-card" *ngFor="let stat of stats; let i = index">
          <div class="stat-topline">
            <span class="stat-icon" [class.accent]="i === 2" [class.warm]="i === 3">{{ ['◈', '⌘', 'ϟ', '↗'][i] }}</span>
            <span class="stat-index">0{{ i + 1 }}</span>
          </div>
          <div class="label">{{ stat.label }}</div>
          <div class="value">{{ stat.value }}</div>
        </div>
      </div>

      <div class="dashboard-grid">
        <section class="panel classes-panel">
          <div class="panel-heading">
            <div><p class="section-label">VOCABULAIRE DE L’ONTOLOGIE</p><h2>Familles d’équipements</h2></div>
            <a routerLink="/explorer">Tout explorer <span aria-hidden="true">↗</span></a>
          </div>
          <ul>
            <li *ngFor="let item of classes | slice:0:8">
              <span class="class-symbol" [style.--class-color]="colorFor(item.name)">{{ symbolFor(item.name) }}</span>
              <span class="class-name">{{ item.name }}<small>Classe RDF</small></span>
              <strong>{{ item.count }}<small>ressources</small></strong>
            </li>
          </ul>
        </section>
        <section class="panel actions-panel">
          <div class="panel-heading">
            <div><p class="section-label">OUTILS DU RÉSEAU</p><h2>Que souhaitez-vous faire ?</h2></div>
          </div>
          <a class="tool-link" routerLink="/ask"><span class="tool-icon question-icon">⌕</span><span><strong>Interroger le réseau</strong><small>Posez une question en français ou en anglais</small></span><b>↗</b></a>
          <a class="tool-link" routerLink="/explorer"><span class="tool-icon data-icon">◈</span><span><strong>Parcourir les ressources</strong><small>Filtrez les individus et leurs propriétés</small></span><b>↗</b></a>
          <a class="tool-link" routerLink="/admin"><span class="tool-icon sparql-icon">{{ '{ }' }}</span><span><strong>Console SPARQL</strong><small>Interrogez et administrez le graphe RDF</small></span><b>↗</b></a>
          <div class="semantic-note"><span>ϟ</span><p><strong>Un réseau qui a du sens.</strong><br>Chaque ressource est reliée à son contexte.</p></div>
        </section>
      </div>
    </section>
  `,
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

  symbolFor(name: string): string {
    const symbols: Record<string, string> = {
      SourceEnergie: '↗',
      UniteStockage: '▥',
      BatimentConsommateur: '⌂',
      LigneTransport: '⌁',
      Compteur: '◉',
      Onduleur: 'ϟ',
      GestionnaireReseau: '⌘'
    };
    return symbols[name] || '◈';
  }
}
