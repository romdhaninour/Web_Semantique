from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import TweetTokenizer

from .ontology_store import SG, load_graph
from .sparql_service import SERVICE

SG_IRI = 'http://www.semanticweb.org/smartgrid-ontology#'
PREFIX = f'PREFIX sg: <{SG_IRI}>\n'
MAX_RESULTS = 50

ENTITY_ALIASES: dict[str, tuple[str, ...]] = {
    'SourceEnergie': ('source energie', 'sources energie', 'source d energie', 'sources d energie', 'source', 'sources', 'energy source', 'energy sources'),
    'Eolienne': ('eolienne', 'eoliennes', 'eolienne', 'wind turbine', 'wind turbines', 'wind turbine'),
    'PanneauSolaire': ('panneau solaire', 'panneaux solaires', 'solar panel', 'solar panels', 'solar'),
    'Batterie': ('batterie', 'batteries', 'battery', 'batteries'),
    'StationPompage': ('station pompage', 'station de pompage', 'stations de pompage', 'pumping station'),
    'Industriel': ('batiment industriel', 'batiments industriels', 'industriel', 'industriels', 'industrial building', 'industrial buildings', 'factory', 'factories'),
    'Residentiel': ('batiment residentiel', 'batiments residentiels', 'residentiel', 'residentiels', 'residential building', 'residential buildings'),
    'Tertiaire': ('batiment tertiaire', 'batiments tertiaires', 'tertiaire', 'tertiaires', 'tertiary building'),
    'HauteTension': ('haute tension', 'lignes haute tension', 'high voltage', 'high voltage line'),
    'MoyenneTension': ('moyenne tension', 'lignes moyenne tension', 'medium voltage', 'medium voltage line'),
    'LigneTransport': ('ligne', 'lignes', 'ligne transport', 'ligne de transport', 'lignes de transport', 'ligne electrique', 'line', 'lines', 'electric line', 'transmission line'),
    'Compteur': ('compteur', 'compteurs', 'meter', 'meters'),
    'Onduleur': ('onduleur', 'onduleurs', 'inverter', 'inverters'),
    'GestionnaireReseau': ('gestionnaire reseau', 'gestionnaire du reseau', 'gestionnaires du reseau', 'grid operator', 'network operator'),
}

CITY_NAMES = (
    'Tunis', 'Sfax', 'Bizerte', 'Ariana', 'Kebili', 'Tozeur', 'Gabes',
    'Sousse', 'Nabeul', 'Monastir', 'Kairouan', 'Zaghouan',
)
PROPERTY_ALIASES: dict[str, tuple[str, ...]] = {
    'capaciteProduction': ('production', 'produire', 'produisent', 'production capacity', 'capacite production', 'puissance', 'kw', 'capacity', 'capacite'),
    'consommationAnnuelle': ('consommation annuelle', 'consommation', 'consommer', 'energy consumption', 'annual consumption', 'kwh'),
    'capaciteStockage': ('capacite stockage', 'storage capacity', 'storage', 'stockage', 'stocker'),
    'nom': ('nom', 'name', 'label'),
}

FRENCH_MARKERS = {
    'a', 'au', 'aux', 'avec', 'batiment', 'batterie', 'capacité', 'capacite', 'combien',
    'consommation', 'des', 'du', 'en', 'est', 'et', 'la', 'le', 'les', 'ligne', 'lignes',
    'moins', 'plus', 'produire', 'produisent', 'quelles', 'quelle', 'quels', 'quel',
    'qui', 'réseau', 'reseau', 'sont', 'source', 'sources', 'sur', 'tension', 'toutes',
}
ENGLISH_MARKERS = {
    'above', 'all', 'are', 'battery', 'below', 'building', 'buildings', 'capacity',
    'consumption', 'energy', 'greater', 'how', 'less', 'line', 'list', 'more', 'of',
    'over', 'show', 'source', 'sources', 'than', 'the', 'turbine', 'what', 'which',
    'wind', 'with',
}

_TOKENIZER = TweetTokenizer(preserve_case=False, reduce_len=True)
_STEMMERS = {
    'fr': SnowballStemmer('french'),
    'en': SnowballStemmer('english'),
}
_NUMBER_PATTERN = re.compile(r'(?<![\w])(?P<number>\d+(?:[.,]\d+)?)\s*(?P<unit>kwh|kw)?(?![\w])')
_ACCENT_TRANSLATION = str.maketrans({
    'œ': 'oe',
    'æ': 'ae',
})


class UnsupportedQuestion(ValueError):
    pass


@dataclass(frozen=True)
class Translation:
    sparql: str
    intent: str
    language: str
    confidence: float
    tokens: list[str]
    stems: list[str]
    entities: list[str]
    metric: str | None
    comparator: str | None
    value: float | None
    location: str | None
    action: str
    target: str | None


def _normalize(text: str) -> str:
    expanded = text.casefold().translate(_ACCENT_TRANSLATION)
    return ''.join(
        char for char in unicodedata.normalize('NFKD', expanded)
        if not unicodedata.combining(char)
    )


def _tokens(text: str) -> list[str]:
    return [token for token in _TOKENIZER.tokenize(_normalize(text)) if re.search(r'[a-z0-9]', token)]


def _language(tokens: list[str]) -> str:
    french_score = sum(token in FRENCH_MARKERS for token in tokens)
    english_score = sum(token in ENGLISH_MARKERS for token in tokens)
    return 'en' if english_score > french_score else 'fr'


def _phrase_tokens(phrase: str) -> tuple[str, ...]:
    return tuple(_tokens(phrase))


_NORMALIZED_ENTITIES = {
    class_name: sorted(
        (_phrase_tokens(alias) for alias in aliases),
        key=len,
        reverse=True,
    )
    for class_name, aliases in ENTITY_ALIASES.items()
}
_NORMALIZED_PROPERTIES = {
    property_name: tuple(_phrase_tokens(alias) for alias in aliases)
    for property_name, aliases in PROPERTY_ALIASES.items()
}
_NORMALIZED_CITIES = {city: tuple(_tokens(city)) for city in CITY_NAMES}


def _contains_phrase(tokens: list[str], phrase: tuple[str, ...]) -> bool:
    return any(
        tuple(tokens[index:index + len(phrase)]) == phrase
        for index in range(len(tokens) - len(phrase) + 1)
    )


def _matches_alias(
    tokens: list[str],
    stems: list[str],
    alias: tuple[str, ...],
    language: str,
) -> bool:
    if _contains_phrase(tokens, alias):
        return True
    stemmed_alias = tuple(_STEMMERS[language].stem(token) for token in alias)
    return _contains_phrase(stems, stemmed_alias)


def _find_entities(tokens: list[str], stems: list[str], language: str) -> list[str]:
    matches: list[tuple[int, int, str]] = []
    for class_name, aliases in _NORMALIZED_ENTITIES.items():
        for alias in aliases:
            stemmed_alias = tuple(_STEMMERS[language].stem(token) for token in alias)
            for source in (tokens, stems):
                candidate = stemmed_alias if source is stems else alias
                for index in range(len(source) - len(candidate) + 1):
                    if tuple(source[index:index + len(candidate)]) == candidate:
                        matches.append((index, index + len(candidate), class_name))
    selected: list[tuple[int, int, str]] = []
    for match in sorted(matches, key=lambda item: (-(item[1] - item[0]), item[0])):
        if any(match[0] < current[1] and current[0] < match[1] for current in selected):
            continue
        selected.append(match)
    return sorted({match[2] for match in selected})


def _find_location(tokens: list[str]) -> str | None:
    for city, city_tokens in _NORMALIZED_CITIES.items():
        if _contains_phrase(tokens, city_tokens):
            return city
    return None


def _find_metric(tokens: list[str], stems: list[str], language: str) -> str | None:
    matches: list[tuple[int, str]] = []
    for property_name, aliases in _NORMALIZED_PROPERTIES.items():
        matches.extend(
            (len(alias), property_name)
            for alias in aliases
            if _matches_alias(tokens, stems, alias, language)
        )
    best_match = max(matches, key=lambda match: match[0], default=None)
    return best_match[1] if best_match else None


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    return value


def _find_number(question: str) -> float | None:
    match = _NUMBER_PATTERN.search(_normalize(question))
    if match is None:
        return None
    return float(match.group('number').replace(',', '.'))


def _find_comparator(tokens: list[str], question: str) -> str | None:
    text = ' '.join(tokens)
    patterns = (
        (r'\b(?:au moins|at least|greater than or equal to|more than or equal to|superieur(?:e)? ou egal(?:e)? a)\b', r'>=', 'gte'),
        (r'\b(?:au plus|at most|less than or equal to|inferieur(?:e)? ou egal(?:e)? a)\b', r'<=', 'lte'),
        (r'\b(?:greater than|more than|above|over|superieur(?:e)? a|plus de|depasse)\b', r'(?<![<>])>(?!=)', 'gt'),
        (r'\b(?:less than|fewer than|below|under|inferieur(?:e)? a|moins de)\b', r'(?<![<>])<(?![=])', 'lt'),
        (r'\b(?:egal(?:e)? a|equal to|exactly)\b', r'(?<![<>])=(?!=)', 'eq'),
    )
    for phrase_pattern, symbol_pattern, comparator in patterns:
        if re.search(phrase_pattern, text) or re.search(symbol_pattern, question):
            return comparator
    return None


def _find_action(question: str) -> str:
    patterns = (
        ('CREATE', r'\b(?:creer|cree|creez|create|add|ajouter|ajoute|ajoutez)\b'),
        ('UPDATE', r'\b(?:modifier|modifie|modifiez|mettre a jour|mets a jour|change|changer|update|set)\b'),
        ('DELETE', r'\b(?:supprimer|supprime|supprimez|effacer|efface|delete|remove)\b'),
    )
    for action, pattern in patterns:
        if re.search(pattern, question):
            return action
    return 'READ'


def _find_resource_id(question: str, action: str) -> str | None:
    id_pattern = r'\b([A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_-]+)\b'
    if action != 'CREATE':
        direct_match = re.search(id_pattern, question)
        if direct_match:
            return direct_match.group(1)
    if action == 'READ':
        return None
    if action == 'CREATE':
        pattern = r'\b(?:nomm(?:e|ée?)|appel(?:e|ée?)|named|called|identifiant|id)\s+([A-Za-z][A-Za-z0-9_-]{1,63})\b'
    else:
        pattern = r'\b(?:pour|sur|de|of|for|named|called|individual|resource|ressource|individu)\s+(?:named\s+)?([A-Za-z][A-Za-z0-9-]{1,63})\b'
    match = re.search(pattern, question, re.IGNORECASE)
    if match is None:
        return None
    identifier = match.group(1)
    return identifier if re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{1,63}', identifier) else None


def _find_updated_text(question: str) -> str | None:
    match = re.search(
        r'\b(?:nom|name|label)\s+(?:a|to|comme|as)\s+["\']?([^"\']{2,80}?)["\']?(?:\s+(?:pour|sur|de|for|of)\b|[?.!]|$)',
        question,
    )
    return match.group(1).strip() if match else None


def _sparql_number(value: float) -> str:
    return str(int(value)) if value.is_integer() else format(value, '.12g')


def _sparql_literal(value: str) -> str:
    escaped = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
    return f'"{escaped}"'


def _make_insert_update(identifier: str, class_name: str, metric: str | None, value: float | None) -> str:
    triples = [f'sg:{identifier} a sg:{class_name} .']
    if metric and value is not None:
        triples.append(f'sg:{identifier} sg:{metric} {_sparql_number(value)} .')
    return PREFIX + 'INSERT DATA {\n  ' + '\n  '.join(triples) + '\n}'


def _make_property_update(identifier: str, metric: str, value: float | str) -> str:
    encoded_value = _sparql_literal(value) if isinstance(value, str) else _sparql_number(value)
    return (
        PREFIX
        + f'DELETE {{ sg:{identifier} sg:{metric} ?oldValue }}\n'
        + f'INSERT {{ sg:{identifier} sg:{metric} {encoded_value} }}\n'
        + f'WHERE {{ sg:{identifier} sg:{metric} ?oldValue }}'
    )


def _make_delete_update(identifier: str) -> str:
    return (
        PREFIX
        + f'DELETE {{ sg:{identifier} ?property ?value . ?subject ?predicate sg:{identifier} . }}\n'
        + f'WHERE {{ {{ sg:{identifier} ?property ?value }} UNION {{ ?subject ?predicate sg:{identifier} }} }}'
    )


def _make_resource_read_query(identifier: str) -> str:
    return PREFIX + f'SELECT ?property ?value WHERE {{ sg:{identifier} ?property ?value }} LIMIT {MAX_RESULTS}'


def _make_filter_query(
    classes: list[str],
    metric: str,
    comparator: str,
    value: float,
    location: str | None,
) -> str:
    operator = {'gt': '>', 'gte': '>=', 'lt': '<', 'lte': '<=', 'eq': '='}[comparator]
    type_clause = (
        f'  ?resource a sg:{classes[0]} .\n'
        if len(classes) == 1
        else (
            '  ?resource a ?resourceType .\n'
            + (
                '  VALUES ?resourceType { ' + ' '.join(f'sg:{name}' for name in classes) + ' }\n'
                if classes else ''
            )
        )
    ) if classes else ''
    location_clause = (
        f'  FILTER(CONTAINS(LCASE(STR(?resource)), "{location.casefold()}"))\n'
        if location else ''
    )
    order_clause = 'ORDER BY DESC(?value)\n' if comparator == 'gt' else 'ORDER BY ASC(?value)\n'
    return (
        PREFIX
        + 'SELECT DISTINCT ?resource ?value WHERE {\n'
        + type_clause
        + f'  ?resource sg:{metric} ?value .\n'
        + f'  FILTER(?value {operator} {_sparql_number(value)})\n'
        + location_clause
        + '}\n'
        + order_clause
        + f'LIMIT {MAX_RESULTS}'
    )


def _make_list_query(classes: list[str], location: str | None) -> str:
    if len(classes) == 1:
        type_clause = f'?resource a sg:{classes[0]} .'
    elif classes:
        values = ' '.join(f'sg:{class_name}' for class_name in classes)
        type_clause = f'?resource a ?resourceType . VALUES ?resourceType {{ {values} }}'
    else:
        type_clause = '?resource a ?resourceType .'
    location_clause = (
        f' FILTER(CONTAINS(LCASE(STR(?resource)), "{location.casefold()}"))'
        if location else ''
    )
    return PREFIX + f'SELECT DISTINCT ?resource WHERE {{ {type_clause}{location_clause} }} LIMIT {MAX_RESULTS}'


def _make_ranking_query(classes: list[str], metric: str, location: str | None) -> str:
    type_clause = f'?resource a sg:{classes[0]} . ' if len(classes) == 1 else ''
    location_clause = (
        f' FILTER(CONTAINS(LCASE(STR(?resource)), "{location.casefold()}"))'
        if location else ''
    )
    return (
        PREFIX
        + f'SELECT DISTINCT ?resource ?value WHERE {{ {type_clause}?resource sg:{metric} ?value .{location_clause} }} '
        + 'ORDER BY DESC(?value) LIMIT 10'
    )


def _make_average_query(classes: list[str], metric: str, location: str | None) -> str:
    type_clause = (
        '?resource a ?type . '
        + 'VALUES ?type { ' + ' '.join(f'sg:{name}' for name in classes) + '} '
    )
    location_clause = (
        f'FILTER(CONTAINS(LCASE(STR(?resource)), "{location.casefold()}")) '
        if location else ''
    )
    return (
        PREFIX
        + f'SELECT ?type (AVG(?value) AS ?average) WHERE {{ {type_clause}'
        + f'?resource sg:{metric} ?value . {location_clause}}} '
        + 'GROUP BY ?type ORDER BY ?type'
    )


def _make_line_manager_voltage_query(comparator: str, value: float) -> str:
    operator = {'gt': '>', 'gte': '>=', 'lt': '<', 'lte': '<=', 'eq': '='}[comparator]
    return (
        PREFIX
        + 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n'
        + 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n'
        + 'SELECT DISTINCT ?line ?manager ?voltage WHERE {\n'
        + '  ?line rdf:type/rdfs:subClassOf* sg:LigneTransport .\n'
        + '  OPTIONAL { ?line sg:gerePar ?manager . }\n'
        + '  OPTIONAL { ?line sg:tensionLigne ?voltage . }\n'
        + f'  FILTER(BOUND(?manager) || (?voltage {operator} {_sparql_number(value)}))\n'
        + '}\n'
        + 'ORDER BY ?line'
    )


class NlpSparqlTranslator:
    def translate(self, question: str) -> Translation:
        normalized = _normalize(question).strip()
        if not normalized:
            raise UnsupportedQuestion('Saisissez une question non vide.')

        tokens = _tokens(normalized)
        language = _language(tokens)
        stems = [_STEMMERS[language].stem(token) for token in tokens]
        classes = _find_entities(tokens, stems, language)
        metric = _find_metric(tokens, stems, language)
        location = _find_location(tokens)
        value = _find_number(normalized)
        comparator = _find_comparator(tokens, normalized) if value is not None else None
        action = _find_action(normalized)
        target = _find_resource_id(question, action)

        if action == 'READ' and any(term in tokens for term in ('average', 'avg', 'mean', 'moyenne')):
            if not classes:
                raise UnsupportedQuestion('Pour calculer une moyenne, précisez une classe, par exemple « éoliennes ».')
            if metric is None:
                if any(class_name in {'Batterie', 'StationPompage'} for class_name in classes):
                    metric = 'capaciteStockage'
                else:
                    metric = 'capaciteProduction'
            sparql = _make_average_query(classes, metric, location)
            intent = 'AGGREGATE_AVERAGE'
            confidence = 0.94
        elif action == 'READ' and target is not None:
            sparql = _make_resource_read_query(target)
            intent = 'READ_RESOURCE'
            confidence = 0.95
        elif action == 'CREATE':
            if len(classes) != 1:
                raise UnsupportedQuestion('Pour créer une ressource, précisez une classe unique, par exemple « éolienne ».')
            if target is None:
                raise UnsupportedQuestion('Précisez le nouvel identifiant avec « nommée Nom_Ressource ».')
            if value is not None and metric is None:
                metric = 'capaciteStockage' if classes[0] in {'Batterie', 'UniteStockage'} else 'capaciteProduction'
            sparql = _make_insert_update(target, classes[0], metric, value)
            intent = 'CREATE'
            confidence = 0.96
        elif action == 'UPDATE':
            if target is None:
                raise UnsupportedQuestion('Précisez l’identifiant de la ressource à modifier, par exemple « Eolienne_Demo ».')
            if metric is None:
                raise UnsupportedQuestion('Précisez la propriété à modifier, par exemple « production » ou « stockage ».')
            if value is None and metric == 'nom':
                text_value = _find_updated_text(normalized)
                if text_value is None:
                    raise UnsupportedQuestion('Précisez la nouvelle valeur du nom, par exemple « change le nom à Parc_Nord ».')
                sparql = _make_property_update(target, metric, text_value)
            elif value is not None:
                sparql = _make_property_update(target, metric, value)
            else:
                raise UnsupportedQuestion('Précisez la propriété et la nouvelle valeur numérique à modifier.')
            intent = 'UPDATE'
            confidence = 0.94
        elif action == 'DELETE':
            if target is None:
                raise UnsupportedQuestion('Précisez l’identifiant exact de la ressource à supprimer, par exemple « Eolienne_Demo ».')
            sparql = _make_delete_update(target)
            intent = 'DELETE'
            confidence = 0.95
        elif (
            'LigneTransport' in classes
            and any(term in tokens for term in ('manager', 'managers', 'managed', 'gestionnaire', 'gestionnaires'))
            and any(term in tokens for term in ('voltage', 'tension'))
            and value is not None
            and comparator is not None
            and any(term in tokens for term in ('or', 'ou'))
        ):
            sparql = _make_line_manager_voltage_query(comparator, value)
            intent = 'OPTIONAL_JOIN_FILTER'
            metric = 'tensionLigne'
            confidence = 0.95
        elif value is not None and comparator is not None:
            selected_metric = metric or ('capaciteStockage' if 'Batterie' in classes else 'capaciteProduction')
            sparql = _make_filter_query(classes, selected_metric, comparator, value, location)
            intent = 'FILTER_NUMERIC'
            confidence = 0.96 if classes or metric else 0.86
            metric = selected_metric
        elif metric and any(term in tokens for term in ('plus', 'maximum', 'highest', 'largest', 'top', 'most')):
            sparql = _make_ranking_query(classes, metric, location)
            intent = 'RANKING'
            confidence = 0.9
        elif classes or location:
            sparql = _make_list_query(classes, location)
            intent = 'LIST_BY_CLASS' if classes else 'SEARCH_LOCATION'
            confidence = 0.92 if classes else 0.84
        else:
            raise UnsupportedQuestion(
                'Question non reconnue. Essayez une recherche par classe, par ville ou un filtre numérique, '
                'par exemple « Quelles éoliennes produisent plus de 500 kW ? ».'
            )

        return Translation(
            sparql=sparql,
            intent=intent,
            language=language,
            confidence=confidence,
            tokens=tokens,
            stems=stems,
            entities=classes,
            metric=metric,
            comparator=comparator,
            value=value,
            location=location,
            action=action,
            target=target,
        )

    def answer(self, question: str, confirm: bool = False) -> dict[str, Any]:
        translation = self.translate(question)
        if translation.action == 'READ' and translation.intent == 'READ_RESOURCE':
            graph = load_graph()
            if not list(graph.predicate_objects(SG[translation.target])):
                raise UnsupportedQuestion(f'La ressource « {translation.target} » est introuvable.')
        if translation.action != 'READ':
            graph = load_graph()
            subject = SG[translation.target]
            existing_triples = set(graph.predicate_objects(subject))
            existing_triples.update((s, p, subject) for s, p in graph.subject_predicates(subject))
            if translation.action == 'CREATE' and existing_triples:
                raise UnsupportedQuestion(f'La ressource « {translation.target} » existe déjà.')
            if translation.action in {'UPDATE', 'DELETE'} and not existing_triples:
                raise UnsupportedQuestion(f'La ressource « {translation.target} » est introuvable.')
            if translation.action == 'UPDATE' and not list(graph.objects(subject, SG[translation.metric])):
                raise UnsupportedQuestion(
                    f'La ressource « {translation.target} » ne possède pas la propriété « {translation.metric} ».'
                )
            if not confirm:
                return self._response(question, translation, [], requires_confirmation=True)

            deleted_count = len(existing_triples)
            SERVICE.update(translation.sparql)
            updated_graph = load_graph()
            if translation.action == 'DELETE':
                rows: list[dict[str, Any]] = []
                count = deleted_count
            else:
                rows = [
                    {key: _json_value(value) for key, value in row.items()}
                    for row in SERVICE.query(
                        PREFIX
                        + f'SELECT ?property ?value WHERE {{ sg:{translation.target} ?property ?value }}'
                    )
                ]
                count = (
                    len(rows)
                    if translation.action == 'CREATE'
                    else len(list(updated_graph.objects(subject, SG[translation.metric])))
                )
            return self._response(
                question,
                translation,
                rows,
                requires_confirmation=False,
                mutation_executed=True,
                count=count,
            )

        rows_by_identity: dict[tuple[tuple[str, str], ...], dict[str, Any]] = {}
        for row in SERVICE.query(translation.sparql):
            json_row = {key: _json_value(value) for key, value in row.items()}
            identity = tuple(sorted((key, str(value)) for key, value in json_row.items()))
            rows_by_identity.setdefault(identity, json_row)
        rows = list(rows_by_identity.values())
        return self._response(question, translation, rows)

    @staticmethod
    def _response(
        question: str,
        translation: Translation,
        rows: list[dict[str, Any]],
        *,
        requires_confirmation: bool = False,
        mutation_executed: bool = False,
        count: int | None = None,
    ) -> dict[str, Any]:
        return {
            'question': question,
            'language': translation.language,
            'intent': translation.intent,
            'action': translation.action,
            'confidence': translation.confidence,
            'tokens': translation.tokens,
            'stems': translation.stems,
            'entities': translation.entities,
            'metric': translation.metric,
            'comparator': translation.comparator,
            'value': translation.value,
            'location': translation.location,
            'target': translation.target,
            'sparql': translation.sparql,
            'count': len(rows) if count is None else count,
            'rows': rows,
            'requires_confirmation': requires_confirmation,
            'mutation_executed': mutation_executed,
            'nlp_tools': ['NLTK TweetTokenizer', 'NLTK SnowballStemmer'],
        }


TRANSLATOR = NlpSparqlTranslator()
