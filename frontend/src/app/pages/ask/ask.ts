import { ChangeDetectorRef, Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, NlpAnswer } from '../../services/api.service';

interface SpeechRecognitionResultLike {
  0: { transcript: string };
}

interface SpeechRecognitionEventLike {
  results: ArrayLike<SpeechRecognitionResultLike>;
}

interface SpeechRecognitionLike {
  lang: string;
  interimResults: boolean;
  maxAlternatives: number;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onerror: ((event: { error: string }) => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
}

type SpeechRecognitionConstructor = new () => SpeechRecognitionLike;
type SpeechWindow = Window & {
  SpeechRecognition?: SpeechRecognitionConstructor;
  webkitSpeechRecognition?: SpeechRecognitionConstructor;
};

@Component({
  selector: 'app-ask-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="page-shell">
      <div>
        <p class="eyebrow">TRAITEMENT DU LANGAGE NATUREL · FR / EN</p>
        <h1>Questionner la grille</h1>
        <p class="intro">Votre question est analysée localement, convertie en SPARQL, puis exécutée sur le graphe RDF.</p>
      </div>
      <div class="chat-box">
        <textarea [(ngModel)]="question" rows="3" placeholder="Ex. Quelles sources produisent plus de 500 kW ?"></textarea>
        <div class="actions">
          <button class="voice-button" type="button" *ngIf="speechAvailable" (click)="toggleVoiceInput()"
            [class.recording]="listening" [disabled]="loading">
            {{ listening ? 'Arrêter le micro' : 'Dicter une question' }}
          </button>
          <button (click)="ask()" [disabled]="loading || !question.trim() || !!response?.requires_confirmation">Questionner</button>
        </div>
        <p class="examples-title">Exemples à essayer</p>
        <div class="example-list">
          <button type="button" class="example-chip" (click)="question = 'Quelles éoliennes produisent plus de 500 kW ?'">Éoliennes > 500 kW</button>
          <button type="button" class="example-chip" (click)="question = 'Which solar panels have a capacity greater than 500 kW?'">Solar panels over 500 kW</button>
          <button type="button" class="example-chip" (click)="question = 'Liste les bâtiments industriels'">Bâtiments industriels</button>
          <button type="button" class="example-chip" (click)="question = 'Quelles éoliennes à Sfax ?'">Éoliennes à Sfax</button>
          <button type="button" class="example-chip mutation-chip" (click)="question = 'Crée une éolienne nommée Demo_Eolienne avec une capacité de production de 650 kW'">CRUD · Créer</button>
          <button type="button" class="example-chip mutation-chip" (click)="question = 'Modifie la capacité de production de Demo_Eolienne à 720 kW'">CRUD · Modifier</button>
          <button type="button" class="example-chip mutation-chip" (click)="question = 'Supprime la ressource Demo_Eolienne'">CRUD · Supprimer</button>
          <button type="button" class="example-chip mutation-chip" (click)="question = 'Lis la ressource Demo_Eolienne'">CRUD · Lire</button>
        </div>
      </div>
      <p class="status" *ngIf="listening">Écoute en cours… parlez distinctement.</p>
      <p class="status" *ngIf="loading">Analyse de la question…</p>
      <p class="error" *ngIf="errorMessage">{{ errorMessage }}</p>

      <div class="result-card" *ngIf="response">
        <div class="meta">
          <span class="badge">{{ response.intent }}</span>
          <span class="badge muted">{{ response.language }}</span>
          <span class="badge accent">conf. {{ response.confidence }}</span>
        </div>
        <div class="analysis">
          <strong>Analyse NLP</strong>
          <span>Opération : {{ actionLabel(response.action) }}</span>
          <span *ngIf="response.entities.length">Entités : {{ response.entities.join(', ') }}</span>
          <span *ngIf="response.metric">Propriété : {{ response.metric }} {{ response.comparator }} {{ response.value }}</span>
          <span *ngIf="response.location">Lieu : {{ response.location }}</span>
          <span>Outils : {{ response.nlp_tools.join(', ') }}</span>
        </div>
        <p class="mutation-notice" *ngIf="response.requires_confirmation">
          SPARQL de modification prêt pour <strong>{{ actionLabel(response.action) }}</strong>
          <span *ngIf="response.target"> de « {{ response.target }} »</span>.
          Vérifiez la requête ci-dessous puis confirmez pour l’exécuter.
        </p>
        <p class="mutation-success" *ngIf="response.mutation_executed">
          {{ response.action === 'DELETE' ? 'Suppression exécutée' : 'Modification exécutée' }} · {{ response.count }} résultat(s) affecté(s).
        </p>
        <details class="sparql-output">
          <summary>{{ response.requires_confirmation ? 'Vérifier la requête SPARQL avant exécution' : 'Voir la requête SPARQL générée et exécutée' }}</summary>
          <pre>{{ response.sparql }}</pre>
        </details>
        <div class="actions mutation-actions" *ngIf="response.requires_confirmation">
          <button type="button" class="cancel-button" (click)="cancelMutation()">Annuler</button>
          <button type="button" class="confirm-button" [disabled]="loading" (click)="confirmMutation()">
            {{ loading ? 'Exécution…' : 'Confirmer ' + actionLabel(response.action).toLowerCase() }}
          </button>
        </div>
        <div class="table-wrap" *ngIf="response.rows?.length">
          <table>
            <thead>
              <tr>
                <th *ngFor="let key of keys(response.rows[0])">{{ key }}</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let row of response.rows | slice:0:10">
                <td *ngFor="let key of keys(row)">{{ cellValue(row, key) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p *ngIf="!response.rows?.length && !response.requires_confirmation && !response.mutation_executed">Aucune ligne retournée.</p>
      </div>
    </section>
  `,
  styleUrls: ['./ask.scss']
})
export class AskPageComponent {
  question = 'Quelles sources produisent plus de 500 kW ?';
  response: NlpAnswer | null = null;
  loading = false;
  errorMessage = '';
  listening = false;
  readonly speechAvailable = typeof window !== 'undefined' &&
    !!((window as SpeechWindow).SpeechRecognition || (window as SpeechWindow).webkitSpeechRecognition);
  private recognition: SpeechRecognitionLike | null = null;

  constructor(private api: ApiService, private changeDetector: ChangeDetectorRef) {}

  toggleVoiceInput(): void {
    if (this.listening) {
      this.recognition?.stop();
      return;
    }
    const browserWindow = window as SpeechWindow;
    const SpeechRecognition = browserWindow.SpeechRecognition || browserWindow.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      this.errorMessage = 'La reconnaissance vocale n’est pas disponible dans ce navigateur.';
      return;
    }

    this.errorMessage = '';
    this.recognition = new SpeechRecognition();
    this.recognition.lang = 'fr-FR';
    this.recognition.interimResults = false;
    this.recognition.maxAlternatives = 1;
    this.recognition.onresult = (event) => {
      this.question = Array.from(event.results).map((result) => result[0].transcript).join(' ').trim();
      this.changeDetector.markForCheck();
    };
    this.recognition.onerror = (event) => {
      this.listening = false;
      this.errorMessage = event.error === 'not-allowed'
        ? 'Autorisez le microphone dans votre navigateur pour dicter une question.'
        : `La reconnaissance vocale a échoué (${event.error}). Réessayez ou saisissez votre question.`;
      this.changeDetector.markForCheck();
    };
    this.recognition.onend = () => {
      this.listening = false;
      this.changeDetector.markForCheck();
    };
    this.listening = true;
    this.recognition.start();
  }

  ask(): void {
    this.submitQuestion(false, this.question, true);
  }

  keys(row: any): string[] {
    return row ? Object.keys(row as any) : [];
  }

  cellValue(row: any, key: string): any {
    return row ? row[key] : null;
  }

  actionLabel(action: NlpAnswer['action']): string {
    return {
      READ: 'Lecture',
      CREATE: 'Création',
      UPDATE: 'Modification',
      DELETE: 'Suppression',
    }[action];
  }

  confirmMutation(): void {
    if (!this.response?.requires_confirmation) return;
    if (
      this.response.action === 'DELETE' &&
      !window.confirm(`Supprimer définitivement la ressource « ${this.response.target} » du graphe ?`)
    ) {
      return;
    }
    this.submitQuestion(true, this.response.question);
  }

  cancelMutation(): void {
    this.response = null;
    this.errorMessage = '';
    this.changeDetector.markForCheck();
  }

  private submitQuestion(confirm: boolean, question: string, clearResponse = false): void {
    this.loading = true;
    this.errorMessage = '';
    if (clearResponse) this.response = null;
    this.api.ask(question, confirm).subscribe({
      next: (result) => {
        this.response = result;
        this.loading = false;
        this.changeDetector.markForCheck();
      },
      error: (error: { error?: { detail?: string | { msg?: string }[] } }) => {
        this.loading = false;
        const detail = error.error?.detail;
        this.errorMessage = typeof detail === 'string'
          ? detail
          : Array.isArray(detail)
            ? detail.map((item) => item.msg).filter((message): message is string => Boolean(message)).join(' ')
              || 'Vérifiez la formulation et réessayez.'
            : 'La question n’a pas pu être traitée. Vérifiez le serveur et réessayez.';
        this.changeDetector.markForCheck();
      },
    });
  }
}
