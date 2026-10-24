import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, Individual } from '../../services/api.service';

interface Place {
  city: string;
  token: string;
  x: number;
  y: number;
  labelX: number;
  labelY: number;
}

interface CityMarker extends Place {
  individuals: Individual[];
}

@Component({
  selector: 'app-map-page',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="page-shell">
      <div>
        <p class="eyebrow">RÉPARTITION TERRITORIALE</p>
        <h1>Carte des équipements</h1>
        <p class="subtitle">Les villes sont placées sur une silhouette géographique de la Tunisie. Les marqueurs regroupent les ressources du graphe dont l’identifiant mentionne une ville.</p>
      </div>

      <p class="status" *ngIf="loading">Chargement des ressources…</p>
      <p class="status error" *ngIf="errorMessage">{{ errorMessage }}</p>

      <div class="map-box" *ngIf="!loading && !errorMessage">
        <svg viewBox="0 0 800 620" role="img" aria-label="Carte géographique simplifiée de la Tunisie avec les villes référencées dans le graphe">
          <text class="sea-label" x="520" y="65">Mer Méditerranée</text>
          <path class="tunisia" d="M330 61 L348 68 L360 78 L378 82 L389 94 L405 99 L419 108 L438 111 L451 121 L469 125 L485 137 L505 143 L523 158 L540 171 L535 184 L523 195 L509 204 L497 218 L503 235 L498 252 L489 270 L495 287 L507 302 L510 320 L501 338 L506 357 L500 378 L506 396 L497 416 L506 435 L510 456 L500 474 L507 491 L495 507 L480 514 L466 505 L452 493 L437 481 L423 478 L411 487 L397 492 L383 486 L369 485 L354 492 L338 488 L325 480 L309 481 L295 474 L281 467 L283 450 L290 432 L292 412 L294 390 L289 370 L296 352 L292 333 L286 313 L289 291 L281 274 L291 255 L293 234 L301 215 L299 198 L306 181 L308 161 L317 143 L320 125 L329 107 L334 89 L348 75 Z"></path>
          <path class="island" d="M522 474 C534 470 545 478 544 490 C543 501 532 508 521 503 C514 498 514 483 522 474 Z"></path>
          <text class="island-label" x="548" y="497">Djerba</text>
          <g *ngFor="let marker of markers" class="map-marker" [class.active]="selectedCity === marker.city"
            [attr.transform]="'translate(' + marker.x + ' ' + marker.y + ')'"
            (click)="selectCity(marker.city)" (keydown.enter)="selectCity(marker.city)" tabindex="0" role="button"
            [attr.aria-label]="marker.city + ', ' + marker.individuals.length + ' ressources'">
            <circle r="8"></circle>
            <text [attr.x]="marker.labelX" [attr.y]="marker.labelY">{{ marker.city }} · {{ marker.individuals.length }}</text>
          </g>
        </svg>
      </div>

      <p class="hint">La silhouette et les positions des villes sont géographiques mais simplifiées. Le graphe ne fournit pas de coordonnées GPS pour chaque équipement : la ville est déduite de son identifiant; les ressources sans ville identifiable sont exclues.</p>

      <section class="detail-panel" *ngIf="selectedMarker as marker">
        <h2>{{ marker.city }} <span>{{ marker.individuals.length }} ressource(s)</span></h2>
        <div class="resource-list">
          <div *ngFor="let item of marker.individuals">
            <strong>{{ item.id }}</strong>
            <small>{{ item.types.join(' · ') }}</small>
          </div>
        </div>
      </section>

      <p class="unlocated" *ngIf="!loading && unlocatedCount">
        {{ unlocatedCount }} ressource(s) sans ville déductible depuis leur identifiant.
      </p>
    </section>
  `,
  styleUrls: ['./map.scss']
})
export class MapPageComponent implements OnInit {
  private readonly places: Place[] = [
    { city: 'Bizerte', token: 'bizerte', x: 375, y: 112, labelX: -12, labelY: -15 },
    { city: 'Tunis', token: 'tunis', x: 431, y: 160, labelX: 13, labelY: -9 },
    { city: 'Ariana', token: 'ariana', x: 438, y: 173, labelX: 13, labelY: 16 },
    { city: 'Nabeul', token: 'nabeul', x: 495, y: 187, labelX: 12, labelY: -8 },
    { city: 'Zaghouan', token: 'zaghouan', x: 408, y: 232, labelX: -78, labelY: 5 },
    { city: 'Sousse', token: 'sousse', x: 485, y: 285, labelX: 14, labelY: -8 },
    { city: 'Monastir', token: 'monastir', x: 496, y: 302, labelX: 14, labelY: 16 },
    { city: 'Kairouan', token: 'kairouan', x: 410, y: 304, labelX: -77, labelY: 5 },
    { city: 'Sfax', token: 'sfax', x: 475, y: 379, labelX: 14, labelY: 4 },
    { city: 'Gabès', token: 'gabes', x: 475, y: 438, labelX: 14, labelY: 5 },
    { city: 'Kébili', token: 'kebili', x: 367, y: 426, labelX: -56, labelY: -12 },
    { city: 'Tozeur', token: 'tozeur', x: 313, y: 400, labelX: -56, labelY: -12 }
  ];

  markers: CityMarker[] = [];
  selectedCity = '';
  unlocatedCount = 0;
  loading = true;
  errorMessage = '';

  constructor(private api: ApiService, private changeDetector: ChangeDetectorRef) {}

  get selectedMarker(): CityMarker | undefined {
    return this.markers.find((marker) => marker.city === this.selectedCity);
  }

  ngOnInit(): void {
    this.api.getIndividuals().subscribe({
      next: (individuals) => {
        const locations = this.places.map((place) => ({
          ...place,
          individuals: individuals.filter((item) => item.id.toLocaleLowerCase().includes(place.token))
        }));
        this.markers = locations.filter((marker) => marker.individuals.length > 0);
        this.unlocatedCount = individuals.filter((item) =>
          !this.places.some((place) => item.id.toLocaleLowerCase().includes(place.token))
        ).length;
        this.loading = false;
        this.changeDetector.markForCheck();
      },
      error: () => {
        this.loading = false;
        this.errorMessage = 'Impossible de charger les ressources de la carte.';
        this.changeDetector.markForCheck();
      }
    });
  }

  selectCity(city: string): void {
    this.selectedCity = this.selectedCity === city ? '' : city;
  }

}
