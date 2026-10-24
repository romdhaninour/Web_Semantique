from __future__ import annotations

from typing import Any, Dict, List

from rdflib import Graph

from .ontology_store import load_graph, named_queries, save_graph


class SparqlService:
    def query(self, sparql: str) -> List[Dict[str, Any]]:
        graph = load_graph()
        results = graph.query(sparql)
        rows: List[Dict[str, Any]] = []
        for row in results:
            item = {}
            for key in results.vars:
                value = row.get(key)
                item[str(key)] = None if value is None else value.toPython()
            rows.append(item)
        return rows

    def ask(self, sparql: str) -> bool:
        return bool(load_graph().query(sparql).askAnswer)

    def update(self, sparql: str) -> None:
        graph = load_graph()
        graph.update(sparql)
        save_graph(graph)

    def catalog(self) -> List[Dict[str, Any]]:
        return named_queries()


SERVICE = SparqlService()
