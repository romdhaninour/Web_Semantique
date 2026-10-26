import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="app-shell">
      <aside class="sidebar">
        <a class="brand" routerLink="/" aria-label="Smart Grid, accueil">
          <span class="brand-mark" aria-hidden="true">
            <svg viewBox="0 0 40 40" fill="none">
              <path d="M21.7 4.5 9.5 22h8.1l-1.3 13.5L30.5 18h-8.2l-.6-13.5Z" fill="currentColor"/>
              <path d="M7 29.5a16 16 0 0 0 25.5-3M33 10.5A16 16 0 0 0 7.5 7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" opacity=".55"/>
            </svg>
          </span>
          <span class="brand-copy">
            <strong>SMART<span>GRID</span></strong>
            <small>SEMANTIC ENERGY NETWORK</small>
          </span>
        </a>
        <div class="sidebar-section-label">ESPACE DE TRAVAIL</div>
        <nav aria-label="Navigation principale">
          <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }">
            <span class="nav-icon" aria-hidden="true">⌂</span><span>Vue d’ensemble</span><span class="nav-arrow">›</span>
          </a>
          <a routerLink="/ask" routerLinkActive="active">
            <span class="nav-icon" aria-hidden="true">⌕</span><span>Questionner le réseau</span><span class="nav-arrow">›</span>
          </a>
          <a routerLink="/explorer" routerLinkActive="active">
            <span class="nav-icon" aria-hidden="true">◈</span><span>Explorer les données</span><span class="nav-arrow">›</span>
          </a>
          <a routerLink="/graph" routerLinkActive="active">
            <span class="nav-icon" aria-hidden="true">⠿</span><span>Graphe sémantique</span><span class="nav-arrow">›</span>
          </a>
          <a routerLink="/map" routerLinkActive="active">
            <span class="nav-icon" aria-hidden="true">◎</span><span>Carte du réseau</span><span class="nav-arrow">›</span>
          </a>
          <a routerLink="/admin" routerLinkActive="active">
            <span class="nav-icon" aria-hidden="true">⚙</span><span>Administration</span><span class="nav-arrow">›</span>
          </a>
        </nav>
        <div class="sidebar-bottom">
          <div class="network-status"><span></span> GRAPHE RDF CHARGÉ</div>
          <p class="sidebar-footer">Une lecture sémantique<br>du réseau énergétique tunisien.</p>
          <div class="sidebar-version"><span>LOCAL DEMO</span><span>RDF · SPARQL</span></div>
        </div>
      </aside>
      <div class="workspace">
        <header class="topbar">
          <div class="topbar-context"><span class="context-pulse"></span> PLATEFORME DE SUPERVISION <span class="context-divider">/</span> TUNISIE</div>
          <div class="topbar-right"><span class="topbar-live"><i></i> GRAPHE RDF ACTIF</span><span class="topbar-date">SMART GRID · WEB SÉMANTIQUE</span></div>
        </header>
        <main class="content"><router-outlet /></main>
        <footer class="workspace-footer"><span>SMART GRID SÉMANTIQUE</span><span>ÉNERGIE · DONNÉES · CONNAISSANCE</span></footer>
      </div>
    </div>
  `,
})
export class App {}
