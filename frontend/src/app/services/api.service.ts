import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface GraphProperty {
  property: string;
  value: string | number | boolean;
  kind: 'literal' | 'resource';
}

export interface Individual {
  id: string;
  types: string[];
  properties: GraphProperty[];
}

export interface ClassSummary {
  name: string;
  count: number;
}

export interface GridStats {
  individuals: number;
  classes: number;
  total_capacity_kw: number;
  total_consumption_kwh: number;
}

export interface IndividualPayload {
  id: string;
  class_name: string;
  properties: Record<string, string | number | boolean>;
}

export interface NlpAnswer {
  question: string;
  language: string;
  intent: string;
  confidence: number;
  tokens: string[];
  stems: string[];
  entities: string[];
  metric: string | null;
  comparator: string | null;
  value: number | null;
  location: string | null;
  action: 'READ' | 'CREATE' | 'UPDATE' | 'DELETE';
  target: string | null;
  sparql: string;
  count: number;
  rows: Record<string, unknown>[];
  requires_confirmation: boolean;
  mutation_executed: boolean;
  nlp_tools: string[];
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly baseUrl = '/api';

  constructor(private http: HttpClient) {}

  health(): Observable<{ status: string; ontology_exists: boolean; seed_exists: boolean }> {
    return this.http.get<{ status: string; ontology_exists: boolean; seed_exists: boolean }>(`${this.baseUrl}/health`);
  }

  getStats(): Observable<GridStats> {
    return this.http.get<GridStats>(`${this.baseUrl}/stats`);
  }

  getClasses(): Observable<ClassSummary[]> {
    return this.http.get<ClassSummary[]>(`${this.baseUrl}/classes`);
  }

  getIndividuals(className?: string): Observable<Individual[]> {
    const url = className
      ? `${this.baseUrl}/classes/${encodeURIComponent(className)}/individuals`
      : `${this.baseUrl}/individuals`;
    return this.http.get<Individual[]>(url);
  }

  ask(question: string, confirm = false): Observable<NlpAnswer> {
    return this.http.post<NlpAnswer>(`${this.baseUrl}/nlp/ask`, { question, confirm });
  }

  querySparql(query: string): Observable<{ rows: Record<string, unknown>[]; count: number }> {
    return this.http.post<{ rows: Record<string, unknown>[]; count: number }>(`${this.baseUrl}/sparql/query`, { query });
  }

  updateSparql(update: string): Observable<{ ok: boolean }> {
    return this.http.post<{ ok: boolean }>(`${this.baseUrl}/sparql/update`, { update });
  }

  runReasoner(): Observable<{ status: string; classified: string[]; message: string }> {
    return this.http.post<{ status: string; classified: string[]; message: string }>(
      `${this.baseUrl}/reasoner/run`,
      {},
    );
  }

  getGraph(): Observable<{
    nodes: {
      id: string;
      label: string;
      type: string;
      properties: GraphProperty[];
    }[];
    edges: { source: string; target: string; label: string }[];
  }> {
    return this.http.get<{
      nodes: {
        id: string;
        label: string;
        type: string;
        properties: GraphProperty[];
      }[];
      edges: { source: string; target: string; label: string }[];
    }>(`${this.baseUrl}/graph`);
  }

  getQueries(): Observable<Record<string, unknown>[]> {
    return this.http.get<Record<string, unknown>[]>(`${this.baseUrl}/queries`);
  }

  runQuery(id: string): Observable<{ rows: Record<string, unknown>[]; count: number }> {
    return this.http.post<{ rows: Record<string, unknown>[]; count: number }>(
      `${this.baseUrl}/queries/${encodeURIComponent(id)}/run`,
      {},
    );
  }

  updateIndividual(id: string, payload: Record<string, string | number | boolean>): Observable<{ ok: boolean; id: string }> {
    return this.http.put<{ ok: boolean; id: string }>(
      `${this.baseUrl}/individuals/${encodeURIComponent(id)}`,
      payload,
    );
  }

  deleteIndividual(id: string): Observable<{ ok: boolean; id: string }> {
    return this.http.delete<{ ok: boolean; id: string }>(`${this.baseUrl}/individuals/${encodeURIComponent(id)}`);
  }

  createIndividual(payload: IndividualPayload): Observable<{ ok: boolean; id: string }> {
    return this.http.post<{ ok: boolean; id: string }>(`${this.baseUrl}/individuals`, payload);
  }
}
