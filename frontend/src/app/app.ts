import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  styleUrl: './app.scss',
  template: `
    <div class="app-shell">
      <aside class="sidebar">
        <div class="brand">Smart Grid</div>
        <p class="brand-caption">Supervision sémantique</p>
        <nav>
          <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }">Accueil</a>
          <a routerLink="/ask" routerLinkActive="active">Questionner la grille</a>
          <a routerLink="/explorer" routerLinkActive="active">Explorer les données</a>
          <a routerLink="/graph" routerLinkActive="active">Graphe</a>
          <a routerLink="/map" routerLinkActive="active">Carte</a>
          <a routerLink="/admin" routerLinkActive="active">Administration</a>
        </nav>
        <p class="sidebar-footer">Supervision énergétique · RDF / SPARQL</p>
      </aside>
      <main class="content">
        <router-outlet />
      </main>
    </div>
  `,
})
export class App {}
