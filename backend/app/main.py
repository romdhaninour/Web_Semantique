from __future__ import annotations

from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from rdflib import Literal, RDF, URIRef

from .config import ONTOLOGY_FILE, SEED_FILE
from .ontology_store import SG, get_stats, list_classes, list_individuals, load_graph, save_graph
from .nlp_service import TRANSLATOR, UnsupportedQuestion
from .sparql_service import SERVICE

app = FastAPI(title='Smart Grid Semantic API', version='0.1.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class QueryPayload(BaseModel):
    query: str


class NlpQuestionPayload(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    confirm: bool = False


class UpdatePayload(BaseModel):
    update: str


class IndividualCreatePayload(BaseModel):
    id: str
    class_name: str
    properties: Dict[str, Any] | None = None


@app.get('/api/health')
def health() -> Dict[str, Any]:
    return {'status': 'ok', 'ontology_exists': ONTOLOGY_FILE.exists(), 'seed_exists': SEED_FILE.exists()}


@app.get('/api/stats')
def stats() -> Dict[str, Any]:
    return get_stats(load_graph())


@app.get('/api/ontology/tree')
def ontology_tree() -> List[Dict[str, Any]]:
    return list_classes(load_graph())


@app.get('/api/classes')
def classes() -> List[Dict[str, Any]]:
    return list_classes(load_graph())


@app.get('/api/classes/{class_name}/individuals')
def class_individuals(class_name: str) -> List[Dict[str, Any]]:
    return list_individuals(load_graph(), class_name)


@app.get('/api/individuals')
def individuals(class_name: str | None = None) -> List[Dict[str, Any]]:
    return list_individuals(load_graph(), class_name)


@app.get('/api/individuals/{item_id}')
def single_individual(item_id: str) -> Dict[str, Any]:
    graph = load_graph()
    subject = SG[item_id]
    triples = list(graph.predicate_objects(subject))
    return {'id': item_id, 'types': [t for t in graph.objects(subject, RDF.type)], 'properties': [{'property': str(p), 'value': str(o)} for p, o in triples]}


@app.post('/api/individuals')
def create_individual(payload: IndividualCreatePayload) -> Dict[str, Any]:
    graph = load_graph()
    subject = SG[payload.id]
    graph.add((subject, RDF.type, SG[payload.class_name]))
    for key, value in (payload.properties or {}).items():
        prop = SG[key]
        if isinstance(value, (int, float)):
            graph.add((subject, prop, Literal(value)))
        else:
            graph.add((subject, prop, Literal(str(value))))
    save_graph(graph)
    return {'ok': True, 'id': payload.id}


@app.put('/api/individuals/{item_id}')
def update_individual(item_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    graph = load_graph()
    subject = SG[item_id]
    for key, value in payload.items():
        if key == 'class_name':
            for existing_type in list(graph.objects(subject, RDF.type)):
                if isinstance(existing_type, URIRef) and str(existing_type).startswith(str(SG)):
                    graph.remove((subject, RDF.type, existing_type))
            graph.add((subject, RDF.type, SG[value]))
            continue
        graph.set((subject, SG[key], Literal(value if isinstance(value, (int, float, bool)) else str(value))))
    save_graph(graph)
    return {'ok': True, 'id': item_id}


@app.delete('/api/individuals/{item_id}')
def delete_individual(item_id: str) -> Dict[str, Any]:
    graph = load_graph()
    subject = SG[item_id]
    for triple in list(graph.triples((subject, None, None))):
        graph.remove(triple)
    for triple in list(graph.triples((None, None, subject))):
        graph.remove(triple)
    save_graph(graph)
    return {'ok': True, 'id': item_id}


@app.get('/api/properties')
def properties() -> List[Dict[str, str]]:
    graph = load_graph()
    items: List[Dict[str, str]] = []
    for pred in sorted(set(graph.predicates()), key=lambda p: str(p)):
        if str(pred).startswith('http://www.semanticweb.org/smartgrid-ontology#'):
            items.append({'uri': str(pred), 'name': str(pred).split('#')[-1]})
    return items


@app.get('/api/graph')
def graph() -> Dict[str, List[Dict[str, Any]]]:
    graph_obj = load_graph()
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    individual_records = list_individuals(graph_obj)
    records_by_uri = {str(SG[item['id']]): item for item in individual_records}
    individuals = {SG[item['id']] for item in individual_records}
    for subject in sorted(individuals, key=str):
        type_names = sorted(
            str(class_uri).split('#')[-1]
            for class_uri in graph_obj.objects(subject, RDF.type)
            if isinstance(class_uri, URIRef) and str(class_uri).startswith(str(SG))
        )
        nodes.append({
            'id': str(subject),
            'label': str(subject).split('#')[-1],
            'type': type_names[0] if type_names else 'Individual',
            'properties': records_by_uri[str(subject)]['properties'],
        })
    for subj, pred, obj in graph_obj:
        if subj in individuals and obj in individuals:
            edges.append({'source': str(subj), 'target': str(obj), 'label': str(pred).split('#')[-1]})
    return {'nodes': nodes, 'edges': edges}


@app.get('/api/queries')
def queries() -> List[Dict[str, Any]]:
    return SERVICE.catalog()


@app.post('/api/queries/{query_id}/run')
def run_named_query(query_id: str) -> Dict[str, Any]:
    selected = [item for item in SERVICE.catalog() if item['id'] == query_id]
    if not selected:
        raise HTTPException(status_code=404, detail='Query not found')
    query = selected[0]['query']
    return {'rows': SERVICE.query(query), 'count': len(SERVICE.query(query))}


@app.post('/api/sparql/query')
def sparql_query(payload: QueryPayload) -> Dict[str, Any]:
    try:
        rows = SERVICE.query(payload.query)
        return {'rows': rows, 'count': len(rows)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post('/api/sparql/update')
def sparql_update(payload: UpdatePayload) -> Dict[str, Any]:
    try:
        SERVICE.update(payload.update)
        return {'ok': True}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post('/api/reasoner/run')
def reasoner() -> Dict[str, Any]:
    graph = load_graph()
    classified: List[str] = []
    for subject, _, capacity in list(graph.triples((None, SG.capaciteProduction, None))):
        try:
            value = float(capacity.toPython())
        except Exception:
            continue
        if value > 500 and (subject, RDF.type, SG.SourceGrandeCapacite) not in graph:
            graph.add((subject, RDF.type, SG.SourceGrandeCapacite))
            classified.append(str(subject).split('#')[-1])
    for subject, _, consumption in list(graph.triples((None, SG.consommationAnnuelle, None))):
        try:
            value = float(consumption.toPython())
        except Exception:
            continue
        if value > 10000 and (subject, RDF.type, SG.GrosConsommateur) not in graph:
            graph.add((subject, RDF.type, SG.GrosConsommateur))
            classified.append(str(subject).split('#')[-1])
    save_graph(graph)
    return {'status': 'ok', 'classified': classified, 'message': 'Reasoner run complete'}


@app.get('/api/validation/checks')
def validation_checks() -> Dict[str, Any]:
    stats = get_stats(load_graph())
    catalog = SERVICE.catalog()
    checks = {
        'individuals_ok': stats['individuals'] >= 60,
        'classes_ok': stats['classes'] >= 19,
        'catalog_ok': len(catalog) >= 20,
        'overall': stats['individuals'] >= 60 and stats['classes'] >= 19 and len(catalog) >= 20,
    }
    return checks


@app.post('/api/nlp/ask')
def nlp_ask(payload: NlpQuestionPayload) -> Dict[str, Any]:
    try:
        return TRANSLATOR.answer(payload.question, confirm=payload.confirm)
    except UnsupportedQuestion as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('backend.app.main:app', host='127.0.0.1', port=8002, reload=True)
