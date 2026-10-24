import { Routes } from '@angular/router';
import { HomePageComponent } from './pages/home/home';
import { AskPageComponent } from './pages/ask/ask';
import { ExplorerPageComponent } from './pages/explorer/explorer';
import { GraphPageComponent } from './pages/graph/graph';
import { MapPageComponent } from './pages/map/map';
import { AdminPageComponent } from './pages/admin/admin';

export const routes: Routes = [
  { path: '', component: HomePageComponent },
  { path: 'ask', component: AskPageComponent },
  { path: 'explorer', component: ExplorerPageComponent },
  { path: 'graph', component: GraphPageComponent },
  { path: 'map', component: MapPageComponent },
  { path: 'admin', component: AdminPageComponent },
  { path: '**', redirectTo: '' }
];
