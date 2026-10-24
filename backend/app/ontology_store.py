from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from rdflib import Graph, OWL, RDF, RDFS, URIRef
from rdflib.namespace import Namespace

from .config import ONTOLOGY_FILE, SEED_FILE, WORKING_FILE

SG = Namespace('http://www.semanticweb.org/smartgrid-ontology#')


def _schema_resources(graph: Graph) -> set[URIRef]:
    schema_types = (
        OWL.Class,
        RDFS.Class,
        OWL.ObjectProperty,
        OWL.DatatypeProperty,
        OWL.AnnotationProperty,
        OWL.Ontology,
        OWL.Restriction,
    )
    return {
        subject
        for schema_type in schema_types
        for subject in graph.subjects(predicate=RDF.type, object=schema_type)
        if isinstance(subject, URIRef)
    }


def _domain_individuals(graph: Graph) -> set[URIRef]:
    schema_resources = _schema_resources(graph)
    return {
        subject
        for subject, class_uri in graph.subject_objects(RDF.type)
        if isinstance(subject, URIRef)
        and subject not in schema_resources
        and isinstance(class_uri, URIRef)
        and str(class_uri).startswith(str(SG))
    }


def load_graph() -> Graph:
    graph = Graph()
    if ONTOLOGY_FILE.exists():
        graph.parse(str(ONTOLOGY_FILE), format='xml')
    if SEED_FILE.exists():
        graph.parse(str(SEED_FILE), format='turtle')
    if WORKING_FILE.exists():
        graph.parse(str(WORKING_FILE), format='turtle')
    return graph


def save_graph(graph: Graph, path: Path | None = None) -> None:
    destination = path or WORKING_FILE
    destination.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=str(destination), format='turtle')


def get_stats(graph: Graph) -> Dict[str, Any]:
    total_capacity = sum(float(v.toPython()) for v in graph.objects(predicate=SG.capaciteProduction))
    total_consumption = sum(float(v.toPython()) for v in graph.objects(predicate=SG.consommationAnnuelle))
    classes = set(graph.subjects(predicate=RDF.type, object=OWL.Class))
    classes |= set(graph.subjects(predicate=RDF.type, object=RDFS.Class))
    class_count = len({str(s) for s in classes if isinstance(s, URIRef)})
    individuals = len(_domain_individuals(graph))
    return {
        'individuals': individuals,
        'classes': class_count,
        'total_capacity_kw': round(total_capacity, 2),
        'total_consumption_kwh': round(total_consumption, 2),
    }


def list_classes(graph: Graph) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    all_classes = set(graph.subjects(predicate=RDF.type, object=OWL.Class))
    all_classes |= set(graph.subjects(predicate=RDF.type, object=RDFS.Class))
    for cls in sorted(all_classes, key=lambda x: str(x)):
        if isinstance(cls, URIRef) and str(cls).startswith('http://www.semanticweb.org/smartgrid-ontology#'):
            members = set(graph.subjects(predicate=RDF.type, object=cls)) & _domain_individuals(graph)
            results.append({'name': str(cls).split('#')[-1], 'count': len(members)})
    return results


def list_individuals(graph: Graph, class_name: str | None = None) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    domain_individuals = _domain_individuals(graph)
    subject_list = sorted(domain_individuals, key=lambda x: str(x))
    for subject in subject_list:
        if class_name:
            cls_uri = SG[class_name]
            if (subject, RDF.type, cls_uri) not in graph:
                continue
        types = sorted({
            str(class_uri).split('#')[-1]
            for class_uri in graph.objects(subject, RDF.type)
            if isinstance(class_uri, URIRef) and str(class_uri).startswith(str(SG))
        })
        props = []
        for pred, obj in sorted(graph.predicate_objects(subject), key=lambda x: str(x[0])):
            if pred == RDF.type:
                continue
            value = obj.toPython() if hasattr(obj, 'toPython') else str(obj)
            props.append({
                'property': str(pred).split('#')[-1],
                'value': value,
                'kind': 'resource' if isinstance(obj, URIRef) else 'literal',
            })
        rows.append({'id': str(subject).split('#')[-1], 'types': types, 'properties': props})
    return rows


def named_queries() -> List[Dict[str, str]]:
    return [
        {
            'id': 'sources-over-500',
            'title_fr': 'Sources supérieures à 500 kW',
            'description': 'Montre les sources de production au-dessus de 500 kW.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> SELECT ?source ?capacity WHERE { ?source a sg:SourceEnergie . ?source sg:capaciteProduction ?capacity . FILTER(?capacity > 500) } ORDER BY DESC(?capacity)''',
        },
        {
            'id': 'industrial-buildings',
            'title_fr': 'Bâtiments industriels',
            'description': 'Liste les bâtiments industriels.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> SELECT ?building WHERE { ?building a sg:Industriel . }''',
        },
        {
            'id': 'largest-consumer',
            'title_fr': 'Plus gros consommateur',
            'description': 'Retourne le bâtiment avec la plus forte consommation annuelle.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> SELECT ?building ?consumption WHERE { ?building a sg:BatimentConsommateur . ?building sg:consommationAnnuelle ?consumption . } ORDER BY DESC(?consumption) LIMIT 5''',
        },
        {
            'id': 'line-manager',
            'title_fr': 'Gestionnaire des lignes',
            'description': 'Montre les lignes et leur gestionnaire.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> SELECT ?line ?manager WHERE { ?line a sg:LigneTransport . ?line sg:gerePar ?manager . }''',
        },
        {
            'id': 'wind-turbines',
            'title_fr': 'Éoliennes',
            'description': 'Liste les éoliennes.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> SELECT ?source WHERE { ?source a sg:Eolienne . }''',
        },
        {
            'id': 'count-sources',
            'title_fr': 'Nombre de sources',
            'description': 'Compter les sources d’énergie.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> SELECT (COUNT(?source) AS ?count) WHERE { ?source a sg:SourceEnergie . }''',
        },
        {
            'id': 'avg-solar-output',
            'title_fr': 'Production moyenne solaire',
            'description': 'Moyenne des capacités de production photovoltaïque.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> SELECT (AVG(?capacity) AS ?avgCapacity) WHERE { ?source a sg:PanneauSolaire . ?source sg:capaciteProduction ?capacity . }''',
        },
        {
            'id': 'long-lines',
            'title_fr': 'Lignes longues',
            'description': 'Lignes de transport supérieures à 100 km.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> SELECT ?line ?length WHERE { ?line a sg:LigneTransport . ?line sg:longueurLigne ?length . FILTER(?length > 100) }''',
        },
        {
            'id': 'high-voltage-lines',
            'title_fr': 'Lignes haute tension',
            'description': 'Affiche les lignes haute tension.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> SELECT ?line ?voltage WHERE { ?line a sg:HauteTension . ?line sg:tensionLigne ?voltage . }''',
        },
        {
            'id': 'battery-relationship',
            'title_fr': 'Batteries et sources',
            'description': 'Montre les relations entre batteries et sources.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> SELECT ?battery ?source WHERE { ?battery a sg:Batterie . ?battery sg:stockeEnergie ?source . }''',
        },
        {
            'id': 'meter-ownership',
            'title_fr': 'Compteurs des bâtiments',
            'description': 'Affiche les bâtiments et leurs compteurs.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> SELECT ?building ?meter WHERE { ?building sg:possedeCompteur ?meter . }''',
        },
        {
            'id': 'search-panel',
            'title_fr': 'Recherche panneaux solaires',
            'description': 'Cherche les panneaux solaires par nom.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> SELECT ?source WHERE { ?source a sg:PanneauSolaire . FILTER(CONTAINS(STR(?source), "Panneau")) }''',
        },
        {
            'id': 'source-classes',
            'title_fr': 'Classes de sources',
            'description': 'Montre les sous-classes de source d’énergie.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> SELECT ?class WHERE { ?class rdfs:subClassOf* sg:SourceEnergie . }''',
        },
        {
            'id': 'total-capacity',
            'title_fr': 'Capacité totale',
            'description': 'Calcule la capacité totale de production.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> SELECT (SUM(?capacity) AS ?total) WHERE { ?source a sg:SourceEnergie . ?source sg:capaciteProduction ?capacity . }''',
        },
        {
            'id': 'grid-operators',
            'title_fr': 'Gestionnaires de réseau',
            'description': 'Liste les gestionnaires de réseau.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> SELECT ?operator WHERE { ?operator a sg:GestionnaireReseau . }''',
        },
        {
            'id': 'line-to-building',
            'title_fr': 'Lignes vers bâtiments',
            'description': 'Relie les lignes aux bâtiments qu’elles alimentent.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> SELECT ?line ?building WHERE { ?line a sg:LigneTransport . ?line sg:transporteVers ?building . }''',
        },
        {
            'id': 'source-driven-by-relationship',
            'title_fr': 'Sources et batteries',
            'description': 'Vérifie les relations de stockage vers sources.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> ASK { ?battery a sg:Batterie . ?battery sg:stockeEnergie ?source . ?source a sg:SourceEnergie . }''',
        },
        {
            'id': 'source-power-map',
            'title_fr': 'Sources à forte capacité',
            'description': 'Cherche les sources avec capacité supérieure ou égale à 500 kW.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> SELECT ?source ?capacity WHERE { ?source a sg:SourceEnergie . ?source sg:capaciteProduction ?capacity . FILTER(?capacity >= 500) }''',
        },
        {
            'id': 'consumer-max',
            'title_fr': 'Consommateur maximal',
            'description': 'Trouve la consommation la plus élevée.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> SELECT ?building ?consumption WHERE { ?building a sg:BatimentConsommateur . ?building sg:consommationAnnuelle ?consumption . } ORDER BY DESC(?consumption) LIMIT 1''',
        },
        {
            'id': 'source-inverter',
            'title_fr': 'Onduleurs utilisés',
            'description': 'Liste les sources qui utilisent un onduleur.',
            'query': '''PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#> SELECT ?source ?inverter WHERE { ?source a sg:SourceEnergie . ?source sg:utiliseOnduleur ?inverter . }''',
        },
    ]
