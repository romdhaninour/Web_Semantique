import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, ClassSummary, Individual } from '../../services/api.service';

@Component({
  selector: 'app-admin-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="page-shell">
      <div>
        <p class="eyebrow">GESTION DU GRAPHE</p>
        <h1>Administration · CRUD & SPARQL</h1>
        <p class="subtitle">Gérez les ressources du réseau et exécutez des requêtes SPARQL.</p>
      </div>

        <div class="toolbar">
          <label class="filter">Classe
            <select [(ngModel)]="selectedClass" (change)="loadRecords()">
              <option value="">Toutes les classes</option>
              <option *ngFor="let item of classes" [value]="item.name">{{ item.name }} ({{ item.count }})</option>
            </select>
          </label>
          <button class="secondary" (click)="startCreate()">+ Nouvelle ressource</button>
        </div>

        <p class="notice" [class.error]="isError" *ngIf="notice">{{ notice }}</p>
        <p class="hint" *ngIf="busy">Chargement…</p>

        <div class="admin-grid">
          <section class="panel">
            <div class="panel-heading">
              <div><h2>Ressources</h2><p>{{ records.length }} résultat(s)</p></div>
              <button class="text-button" (click)="loadRecords()" [disabled]="busy">Actualiser</button>
            </div>
            <div class="record-list" *ngIf="records.length; else emptyRecords">
              <button class="record-row" *ngFor="let item of records" [class.active]="editingId === item.id"
                (click)="startEdit(item)">
                <strong>{{ item.id }}</strong>
                <span>{{ preview(item) }}</span>
              </button>
            </div>
            <ng-template #emptyRecords><p class="empty">Aucune ressource dans cette classe.</p></ng-template>
          </section>

          <section class="panel editor">
            <h2>{{ editingId ? 'Modifier la ressource' : 'Créer une ressource' }}</h2>
            <label>Identifiant local
              <input [(ngModel)]="formId" [disabled]="!!editingId" placeholder="ex. Panneau_Solaire_01" />
            </label>
            <label>Classe
              <select [(ngModel)]="formClass" [disabled]="!!editingId">
                <option *ngFor="let item of classes" [value]="item.name">{{ item.name }}</option>
              </select>
            </label>
            <label>Propriétés (objet JSON)
              <textarea [(ngModel)]="propertiesText" rows="8" spellcheck="false"
                placeholder='{"nom":"Centrale Nord","capaciteProduction":650}'></textarea>
            </label>
            <p class="hint">Les nombres restent numériques. En modification, les propriétés littérales sont ajoutées ou mises à jour; les liens RDF vers d'autres ressources sont préservés.</p>
            <div class="actions">
              <button (click)="saveRecord()" [disabled]="busy || !formId.trim()">{{ editingId ? 'Enregistrer' : 'Créer' }}</button>
              <button class="secondary" (click)="startCreate()">Réinitialiser</button>
              <button class="danger" *ngIf="editingId" (click)="deleteRecord()" [disabled]="busy">Supprimer</button>
            </div>
          </section>
        </div>

        <section class="panel sparql-panel">
          <div class="panel-heading">
            <div><h2>Console SPARQL</h2><p>Lecture avec SELECT · écriture avec INSERT / DELETE / DELETE + INSERT</p></div>
            <button class="secondary" (click)="runReasoner()" [disabled]="busy">Lancer le raisonneur</button>
          </div>
          <div class="sparql-controls">
            <label>Exemple
              <select [(ngModel)]="selectedExample" (change)="loadExample()">
                <option *ngFor="let example of examples" [value]="example.id">{{ example.label }}</option>
              </select>
            </label>
            <label>Opération
              <select [(ngModel)]="sparqlMode">
                <option value="query">Lecture — SELECT</option>
                <option value="update">Écriture — INSERT / DELETE</option>
              </select>
            </label>
          </div>
          <textarea [(ngModel)]="queryText" rows="8" spellcheck="false" aria-label="Requête SPARQL"></textarea>
          <p class="hint" *ngIf="sparqlMode === 'update'">Les opérations d’écriture modifient le fichier local du graphe. Testez d’abord avec l’individu d’exemple.</p>
          <button (click)="runSparql()" [disabled]="busy || !queryText.trim()">
            {{ sparqlMode === 'query' ? 'Exécuter SELECT' : 'Exécuter la mise à jour' }}
          </button>
          <div class="table-wrap" *ngIf="queryRows">
            <p class="hint">{{ queryCount }} ligne(s) retournée(s)</p>
            <pre>{{ queryRows | json }}</pre>
          </div>
          <p class="result-message" *ngIf="sparqlResult">{{ sparqlResult }}</p>
          <p class="reasoner-result" *ngIf="reasonerResult">{{ reasonerResult }}</p>
        </section>
    </section>
  `,
  styleUrls: ['./admin.scss']
})
export class AdminPageComponent implements OnInit {
  classes: ClassSummary[] = [];
  records: Individual[] = [];
  selectedClass = '';
  formId = '';
  formClass = '';
  propertiesText = '{}';
  editingId = '';
  readonly examples = [
    {
      id: 'sources',
      label: 'Recherche — toutes les sources',
      mode: 'query' as const,
      query: 'PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>\nSELECT ?source WHERE { ?source a sg:SourceEnergie . } LIMIT 10'
    },
    {
      id: 'filter',
      label: 'Filtrage — capacité > 500 kW',
      mode: 'query' as const,
      query: 'PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>\nSELECT ?source ?capacity WHERE { ?source a sg:SourceEnergie ; sg:capaciteProduction ?capacity . FILTER(?capacity > 500) } ORDER BY DESC(?capacity)'
    },
    {
      id: 'search',
      label: 'Recherche — identifiant contient « sfax »',
      mode: 'query' as const,
      query: 'PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>\nSELECT ?resource WHERE { ?resource a ?type . FILTER(CONTAINS(LCASE(STR(?resource)), "sfax")) }'
    },
    {
      id: 'insert',
      label: 'CRUD — CREATE (individu de démo)',
      mode: 'update' as const,
      query: 'PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>\nINSERT DATA { sg:Demo_Etudiant2 a sg:Eolienne ; sg:capaciteProduction 650 . }'
    },
    {
      id: 'update',
      label: 'CRUD — UPDATE (capacité)',
      mode: 'update' as const,
      query: 'PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>\nDELETE { sg:Demo_Etudiant2 sg:capaciteProduction 650 }\nINSERT { sg:Demo_Etudiant2 sg:capaciteProduction 720 }\nWHERE { sg:Demo_Etudiant2 sg:capaciteProduction 650 }'
    },
    {
      id: 'delete',
      label: 'CRUD — DELETE (individu de démo)',
      mode: 'update' as const,
      query: 'PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>\nDELETE WHERE { sg:Demo_Etudiant2 ?property ?value }'
    }
  ];
  selectedExample = 'sources';
  sparqlMode: 'query' | 'update' = 'query';
  queryText = this.examples[0].query;
  queryRows: Record<string, unknown>[] | null = null;
  queryCount = 0;
  sparqlResult = '';
  reasonerResult = '';
  notice = '';
  isError = false;
  busy = false;

  constructor(private api: ApiService, private changeDetector: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.loadWorkspace();
  }

  loadWorkspace(): void {
    this.busy = true;
    this.api.getClasses().subscribe({
      next: (classes) => {
        this.classes = classes;
        this.formClass = this.formClass || classes[0]?.name || '';
        this.busy = false;
        this.loadRecords();
        this.changeDetector.markForCheck();
      },
      error: () => {
        this.busy = false;
        this.showError('Impossible de charger les classes du graphe.');
        this.changeDetector.markForCheck();
      }
    });
  }

  loadRecords(): void {
    this.busy = true;
    this.api.getIndividuals(this.selectedClass || undefined).subscribe({
      next: (records) => {
        this.records = records;
        this.busy = false;
        this.changeDetector.markForCheck();
      },
      error: () => {
        this.busy = false;
        this.showError('Impossible de charger les ressources.');
        this.changeDetector.markForCheck();
      }
    });
  }

  startCreate(): void {
    this.editingId = '';
    this.formId = '';
    this.formClass = this.selectedClass || this.classes[0]?.name || '';
    this.propertiesText = '{}';
  }

  startEdit(item: Individual): void {
    this.editingId = item.id;
    this.formId = item.id;
    this.formClass = this.selectedClass || item.types[0] || this.classes[0]?.name || '';
    const properties: Record<string, string | number | boolean> = {};
    for (const property of item.properties) {
      if (property.kind === 'literal') {
        properties[property.property] = property.value;
      }
    }
    this.propertiesText = JSON.stringify(properties, null, 2);
    this.notice = '';
  }

  saveRecord(): void {
    let properties: Record<string, string | number | boolean>;
    try {
      const parsed: unknown = JSON.parse(this.propertiesText || '{}');
      if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
        throw new Error('Les propriétés doivent être un objet JSON.');
      }
      properties = parsed as Record<string, string | number | boolean>;
      if (Object.values(properties).some((value) => !['string', 'number', 'boolean'].includes(typeof value))) {
        throw new Error('Chaque valeur doit être une chaîne, un nombre ou un booléen.');
      }
    } catch (error) {
      this.showError(error instanceof Error ? error.message : 'JSON des propriétés invalide.');
      return;
    }

    if (!this.formClass) {
      this.showError('Choisissez une classe pour la ressource.');
      return;
    }

    this.busy = true;
    this.notice = '';
    const request = this.editingId
      ? this.api.updateIndividual(this.editingId, properties)
      : this.api.createIndividual({ id: this.formId.trim(), class_name: this.formClass, properties });
    request.subscribe({
      next: () => {
        this.busy = false;
        this.notice = this.editingId ? 'Ressource mise à jour.' : 'Ressource créée.';
        this.isError = false;
        this.loadRecords();
        if (!this.editingId) this.startCreate();
        this.changeDetector.markForCheck();
      },
      error: (error: { error?: { detail?: string } }) => {
        this.busy = false;
        this.showError(error.error?.detail || 'Enregistrement impossible.');
        this.changeDetector.markForCheck();
      }
    });
  }

  deleteRecord(): void {
    if (!this.editingId || !window.confirm(`Supprimer ${this.editingId} du graphe ?`)) return;
    const id = this.editingId;
    this.busy = true;
    this.api.deleteIndividual(id).subscribe({
      next: () => {
        this.busy = false;
        this.notice = `Ressource ${id} supprimée.`;
        this.isError = false;
        this.startCreate();
        this.loadRecords();
        this.changeDetector.markForCheck();
      },
      error: (error: { error?: { detail?: string } }) => {
        this.busy = false;
        this.showError(error.error?.detail || 'Suppression impossible.');
        this.changeDetector.markForCheck();
      }
    });
  }

  loadExample(): void {
    const example = this.examples.find((item) => item.id === this.selectedExample);
    if (!example) return;
    this.sparqlMode = example.mode;
    this.queryText = example.query;
    this.queryRows = null;
    this.queryCount = 0;
    this.sparqlResult = '';
  }

  runSparql(): void {
    this.busy = true;
    this.notice = '';
    this.queryRows = null;
    this.sparqlResult = '';
    if (this.sparqlMode === 'update') {
      this.api.updateSparql(this.queryText).subscribe({
        next: () => {
          this.busy = false;
          this.sparqlResult = 'Mise à jour SPARQL exécutée et enregistrée.';
          this.loadRecords();
          this.changeDetector.markForCheck();
        },
        error: (error: { error?: { detail?: string } }) => {
          this.busy = false;
          this.showError(error.error?.detail || 'Mise à jour SPARQL invalide.');
          this.changeDetector.markForCheck();
        }
      });
      return;
    }

    this.api.querySparql(this.queryText).subscribe({
      next: (result) => {
        this.queryRows = result.rows;
        this.queryCount = result.count;
        this.busy = false;
        this.changeDetector.markForCheck();
      },
      error: (error: { error?: { detail?: string } }) => {
        this.busy = false;
        this.showError(error.error?.detail || 'Requête SPARQL invalide.');
        this.changeDetector.markForCheck();
      }
    });
  }

  runReasoner(): void {
    this.busy = true;
    this.reasonerResult = '';
    this.api.runReasoner().subscribe({
      next: (result) => {
        this.busy = false;
        this.reasonerResult = result.classified.length
          ? `Raisonnement terminé : ${result.classified.join(', ')}`
          : 'Raisonnement terminé : aucune nouvelle classification.';
        this.loadWorkspace();
        this.changeDetector.markForCheck();
      },
      error: (error: { error?: { detail?: string } }) => {
        this.busy = false;
        this.showError(error.error?.detail || 'Le raisonneur n’a pas pu s’exécuter.');
        this.changeDetector.markForCheck();
      }
    });
  }

  preview(item: Individual): string {
    const label = item.properties.find((property) => property.property === 'nom' || property.property === 'name');
    return label ? String(label.value) : `${item.properties.length} propriété(s)`;
  }

  private showError(message: string): void {
    this.notice = message;
    this.isError = true;
  }
}
