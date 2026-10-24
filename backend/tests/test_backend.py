import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.main import app

client = TestClient(app)


def test_health_and_stats():
    health = client.get('/api/health')
    assert health.status_code == 200
    assert health.json()['status'] == 'ok'

    stats = client.get('/api/stats')
    assert stats.status_code == 200
    assert stats.json()['individuals'] >= 60
    assert stats.json()['classes'] >= 19


def test_classes_and_queries():
    classes = client.get('/api/classes')
    assert classes.status_code == 200
    assert len(classes.json()) >= 19

    queries = client.get('/api/queries')
    assert queries.status_code == 200
    assert len(queries.json()) >= 20


def test_individuals_and_graph_only_include_grid_instances():
    stats = client.get('/api/stats').json()
    rows = client.get('/api/individuals').json()
    assert len(rows) == stats['individuals']
    assert rows
    assert all(row['types'] for row in rows)
    assert all(prop['kind'] in {'literal', 'resource'} for row in rows for prop in row['properties'])
    assert all(row['id'] != 'isRuleEnabled' for row in rows)

    graph = client.get('/api/graph')
    assert graph.status_code == 200
    graph_nodes = graph.json()['nodes']
    assert len(graph_nodes) == stats['individuals']
    wind_turbine = next(node for node in graph_nodes if node['label'] == 'Eolienne_Ariana1')
    assert any(
        prop['property'] == 'capaciteProduction' and prop['value'] == '490.0'
        for prop in wind_turbine['properties']
    )


def test_crud_preserves_numeric_values_and_class_updates_without_login(monkeypatch):
    from rdflib import Graph, Literal, RDF

    from backend.app import main as main_module
    from backend.app.ontology_store import SG

    working_graph = Graph()
    monkeypatch.setattr(main_module, 'load_graph', lambda: working_graph)
    monkeypatch.setattr(main_module, 'save_graph', lambda graph: None)

    created = client.post(
        '/api/individuals',
        json={'id': 'CRUD_Test_Item', 'class_name': 'SourceEnergie', 'properties': {'capaciteProduction': 650}},
    )
    assert created.status_code == 200
    item = SG['CRUD_Test_Item']
    assert working_graph.value(item, SG.capaciteProduction) == Literal(650)

    updated = client.put(
        '/api/individuals/CRUD_Test_Item',
        json={'class_name': 'Eolienne', 'capaciteProduction': 850},
    )
    assert updated.status_code == 200
    assert (item, RDF.type, SG.SourceEnergie) not in working_graph
    assert (item, RDF.type, SG.Eolienne) in working_graph
    assert working_graph.value(item, SG.capaciteProduction) == Literal(850)

    deleted = client.delete('/api/individuals/CRUD_Test_Item')
    assert deleted.status_code == 200
    assert not list(working_graph.triples((item, None, None)))


def test_sparql_updates_persist_and_are_visible_to_later_queries(monkeypatch):
    from rdflib import Graph

    from backend.app import sparql_service

    working_graph = Graph()
    monkeypatch.setattr(sparql_service, 'load_graph', lambda: working_graph)
    monkeypatch.setattr(sparql_service, 'save_graph', lambda graph: None)

    inserted = client.post(
        '/api/sparql/update',
        json={
            'update': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
                INSERT DATA { sg:SPARQL_Test_Wind a sg:Eolienne ; sg:capaciteProduction 650 .}'''
        },
    )
    assert inserted.status_code == 200

    selected = client.post(
        '/api/sparql/query',
        json={
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
                SELECT ?capacity WHERE { sg:SPARQL_Test_Wind sg:capaciteProduction ?capacity .}'''
        },
    )
    assert selected.status_code == 200
    assert selected.json()['rows'] == [{'capacity': 650}]

    updated = client.post(
        '/api/sparql/update',
        json={
            'update': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
                DELETE { sg:SPARQL_Test_Wind sg:capaciteProduction 650 }
                INSERT { sg:SPARQL_Test_Wind sg:capaciteProduction 720 }
                WHERE { sg:SPARQL_Test_Wind sg:capaciteProduction 650 }'''
        },
    )
    assert updated.status_code == 200
    assert sparql_service.SERVICE.query(
        '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
           SELECT ?capacity WHERE { sg:SPARQL_Test_Wind sg:capaciteProduction ?capacity .}'''
    ) == [{'capacity': 720}]

    deleted = client.post(
        '/api/sparql/update',
        json={
            'update': 'PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> '
            'DELETE WHERE { sg:SPARQL_Test_Wind ?property ?value }'
        },
    )
    assert deleted.status_code == 200
    assert sparql_service.SERVICE.query(
        '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
           SELECT ?source WHERE { sg:SPARQL_Test_Wind a ?type .}'''
    ) == []


def test_reasoner_runs_without_login(monkeypatch):
    from rdflib import Graph

    from backend.app import main as main_module

    monkeypatch.setattr(main_module, 'load_graph', lambda: Graph())
    monkeypatch.setattr(main_module, 'save_graph', lambda graph: None)

    response = client.post('/api/reasoner/run')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_nlp_translates_french_numeric_question_and_executes_sparql():
    response = client.post(
        '/api/nlp/ask',
        json={'question': 'Quelles éoliennes produisent plus de 500 kW ?'},
    )
    assert response.status_code == 200
    result = response.json()
    assert result['intent'] == 'FILTER_NUMERIC'
    assert result['language'] == 'fr'
    assert result['entities'] == ['Eolienne']
    assert result['metric'] == 'capaciteProduction'
    assert result['comparator'] == 'gt'
    assert result['value'] == 500
    assert 'FILTER(?value > 500)' in result['sparql']
    assert 'NLTK TweetTokenizer' in result['nlp_tools']
    assert 'NLTK SnowballStemmer' in result['nlp_tools']
    assert result['count'] == len(result['rows'])
    assert result['rows']
    assert all(row['value'] > 500 for row in result['rows'])
    assert len({(row['resource'], row['value']) for row in result['rows']}) == len(result['rows'])


def test_nlp_translates_english_storage_question_and_inclusive_comparator():
    response = client.post(
        '/api/nlp/ask',
        json={'question': 'Which batteries have storage capacity at least 100 kWh?'},
    )
    assert response.status_code == 200
    result = response.json()
    assert result['language'] == 'en'
    assert result['entities'] == ['Batterie']
    assert result['metric'] == 'capaciteStockage'
    assert result['comparator'] == 'gte'
    assert 'FILTER(?value >= 100)' in result['sparql']
    assert result['rows']
    assert all(row['value'] >= 100 for row in result['rows'])


def test_nlp_translates_location_search_and_safe_unsupported_question():
    location = client.post(
        '/api/nlp/ask',
        json={'question': 'Quelles éoliennes à Sfax ?'},
    )
    assert location.status_code == 200
    result = location.json()
    assert result['intent'] == 'LIST_BY_CLASS'
    assert result['location'] == 'Sfax'
    assert 'CONTAINS(LCASE(STR(?resource)), "sfax")' in result['sparql']

    unsupported = client.post('/api/nlp/ask', json={'question': 'Quel temps fera-t-il demain ?'})
    assert unsupported.status_code == 422
    assert 'Question non reconnue' in unsupported.json()['detail']


def test_nlp_accepts_symbolic_numeric_comparators():
    response = client.post(
        '/api/nlp/ask',
        json={'question': 'Éoliennes avec production >= 500 kW'},
    )
    assert response.status_code == 200
    assert response.json()['comparator'] == 'gte'
    assert 'FILTER(?value >= 500)' in response.json()['sparql']


def test_nlp_generates_class_listing_and_ranking_queries():
    listing = client.post(
        '/api/nlp/ask',
        json={'question': 'Liste les bâtiments industriels'},
    )
    assert listing.status_code == 200
    assert listing.json()['intent'] == 'LIST_BY_CLASS'
    assert listing.json()['entities'] == ['Industriel']
    assert 'sg:Industriel' in listing.json()['sparql']

    ranking = client.post(
        '/api/nlp/ask',
        json={'question': 'Quelles éoliennes ont la plus grande production ?'},
    )
    assert ranking.status_code == 200
    assert ranking.json()['intent'] == 'RANKING'
    assert 'ORDER BY DESC(?value)' in ranking.json()['sparql']


def test_nlp_crud_previews_requires_confirmation_and_preserves_resource_id_case(monkeypatch):
    from rdflib import Graph, Literal, RDF

    from backend.app import nlp_service, sparql_service
    from backend.app.ontology_store import SG

    graph = Graph()
    monkeypatch.setattr(nlp_service, 'load_graph', lambda: graph)
    monkeypatch.setattr(sparql_service, 'load_graph', lambda: graph)
    monkeypatch.setattr(sparql_service, 'save_graph', lambda updated_graph: None)
    demo = SG['Demo_Eolienne']

    create_question = 'Crée une éolienne nommée Demo_Eolienne avec une capacité de production de 650 kW'
    preview = client.post('/api/nlp/ask', json={'question': create_question})
    assert preview.status_code == 200
    assert preview.json()['action'] == 'CREATE'
    assert preview.json()['target'] == 'Demo_Eolienne'
    assert preview.json()['requires_confirmation'] is True
    assert 'INSERT DATA' in preview.json()['sparql']
    assert not list(graph.predicate_objects(demo))

    created = client.post('/api/nlp/ask', json={'question': create_question, 'confirm': True})
    assert created.status_code == 200
    assert created.json()['mutation_executed'] is True
    assert (demo, RDF.type, SG.Eolienne) in graph
    assert graph.value(demo, SG.capaciteProduction) == Literal(650)

    duplicate = client.post('/api/nlp/ask', json={'question': create_question})
    assert duplicate.status_code == 422
    assert 'existe déjà' in duplicate.json()['detail']

    read = client.post(
        '/api/nlp/ask',
        json={'question': 'Lis la ressource Demo_Eolienne'},
    )
    assert read.status_code == 200
    assert read.json()['intent'] == 'READ_RESOURCE'
    assert read.json()['rows']

    update_question = 'Modifie la capacité de production de Demo_Eolienne à 720 kW'
    update_preview = client.post('/api/nlp/ask', json={'question': update_question})
    assert update_preview.status_code == 200
    assert update_preview.json()['requires_confirmation'] is True
    assert graph.value(demo, SG.capaciteProduction) == Literal(650)

    updated = client.post('/api/nlp/ask', json={'question': update_question, 'confirm': True})
    assert updated.status_code == 200
    assert updated.json()['mutation_executed'] is True
    assert graph.value(demo, SG.capaciteProduction) == Literal(720)

    graph.add((SG['Grid_Node'], SG.connectsTo, demo))
    delete_question = 'Supprime la ressource Demo_Eolienne'
    delete_preview = client.post('/api/nlp/ask', json={'question': delete_question})
    assert delete_preview.status_code == 200
    assert delete_preview.json()['requires_confirmation'] is True
    assert list(graph.predicate_objects(demo))

    deleted = client.post('/api/nlp/ask', json={'question': delete_question, 'confirm': True})
    assert deleted.status_code == 200
    assert deleted.json()['mutation_executed'] is True
    assert not list(graph.predicate_objects(demo))
    assert not list(graph.subject_predicates(demo))


def test_sparql_query_is_available_without_login():
    query = client.post(
        '/api/sparql/query',
        json={
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
                SELECT ?source WHERE { ?source a sg:SourceEnergie .} LIMIT 3'''
        },
    )
    assert query.status_code == 200
    assert len(query.json()['rows']) >= 3

    assert client.post('/api/auth/login', json={}).status_code == 404
