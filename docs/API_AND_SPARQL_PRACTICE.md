# FastAPI and SPARQL practice guide

This guide contains API calls to demonstrate the backend, natural-language questions for the NLP endpoint, and SPARQL exercises from basic to advanced. The examples use the project's current routes and RDF vocabulary.

## 1. Start the application

1. From the repository root, run `Start Smart Grid.bat`.
2. Open the frontend when it launches.
3. Open FastAPI's interactive documentation at `http://127.0.0.1:8002/docs`.
4. In Swagger, expand an endpoint, click **Try it out**, enter the request if needed, then click **Execute**.

The API normally listens on port `8002`. If the launcher reports a different API port, use that port instead.

## 2. Useful FastAPI requests

| Method and route | What to demonstrate |
|---|---|
| `GET /api/health` | API status and whether ontology/seed files were found |
| `GET /api/validation/checks` | Project data/catalogue validation thresholds |
| `GET /api/stats` | Individual/class counts and total values |
| `GET /api/classes` | Ontology classes and their individual counts |
| `GET /api/individuals` | Grid individuals |
| `GET /api/individuals?class_name=Eolienne` | Individuals filtered by class |
| `GET /api/individuals/Eolienne_Sfax1` | One resource and its properties |
| `GET /api/graph` | Graph nodes and relationships |
| `GET /api/queries` | The predefined SPARQL query catalogue |
| `POST /api/sparql/query` | Execute a read-only SPARQL query |
| `POST /api/sparql/update` | Execute a SPARQL update; changes are saved |
| `POST /api/nlp/ask` | Translate a supported French/English question into SPARQL |
| `POST /api/reasoner/run` | Apply the project's targeted numeric classification rules |

### Example: check the service

Open `GET /api/health` and click **Execute**. A healthy response has `"status": "ok"` and indicates whether the ontology and seed data files exist.

### Example: check the dataset

Open `GET /api/validation/checks`. The current checks expect at least 60 individuals, 19 classes, and 20 catalogue queries. A passing response has `"overall": true`.

Open `GET /api/stats` to see the actual counts and totals used by the dashboard.

### Example: retrieve a resource

Open `GET /api/individuals/Eolienne_Sfax1`. The response shows the resource's types and properties. This is a useful way to connect the API response to the same resource in the frontend Explorer.

## 3. Natural-language questions for `/api/nlp/ask`

In Swagger, open `POST /api/nlp/ask`, click **Try it out**, and submit a JSON body such as:

```json
{
  "question": "Quelles éoliennes produisent plus de 500 kW ?",
  "confirm": false
}
```

Inspect the response fields `language`, `intent`, `entities`, `metric`, `comparator`, `value`, `sparql`, `count`, `rows`, and `nlp_tools`.

The following are examples aligned with the translator's current vocabulary and rules. Try them one at a time; a successful response should include the generated query and its results.

### Class and city searches

1. `Quelles sont les éoliennes ?`
2. `Quels panneaux solaires sont à Bizerte ?`
3. `Quelles batteries sont à Tunis ?`
4. `Quelles lignes haute tension ?`
5. `Which wind turbines are in Sfax?`
6. `List the solar panels in Tozeur.`
7. `Which industrial buildings are there?`
8. `Show the batteries in Gabes.`

### Numeric filters

9. `Quelles éoliennes produisent plus de 500 kW ?`
10. `Quels panneaux solaires ont une production supérieure ou égale à 500 kW ?`
11. `Quelles sources ont une capacité de production inférieure à 400 kW ?`
12. `Quelles batteries ont une capacité de stockage au moins 100 kWh ?`
13. `Which batteries have storage capacity at least 100 kWh?`
14. `Which wind turbines have production capacity below 500 kW?`
15. `Which energy sources have capacity equal to 600 kW?`
16. `Which buildings have annual consumption greater than 10000 kWh?`

### Rankings

17. `Quelles sources ont la production la plus élevée ?`
18. `Which batteries have the highest storage capacity?`
19. `Show the buildings with the largest annual consumption.`

### Aggregations

20. `Quelle est la production moyenne des éoliennes et des panneaux solaires ?`
21. `What is the average capacity for wind turbines and solar panels?`
22. `What is the average storage capacity for batteries?`

These questions generate an `AVG` query grouped by the requested class, so the results show a separate average for each class. The translator is rule- and lexicon-based, not a general conversational AI. If a wording is outside its supported vocabulary, it may return HTTP `422`. Try a simpler supported wording rather than presenting an unsupported question as a successful feature.

### NLP CRUD: optional, use a temporary resource only

These are write operations. First send each question with `"confirm": false`; check the preview and generated SPARQL. For a mutation, submit the same question with `"confirm": true` only after confirming the identifier is temporary and unused. Do not use a real project resource.

Create:

```json
{
  "question": "Crée une éolienne nommée Demo_Eolienne avec une capacité de production de 650 kW",
  "confirm": false
}
```

Update the temporary resource's production:

```json
{
  "question": "Modifie la capacité de production de Demo_Eolienne à 720 kW",
  "confirm": false
}
```

Read it:

```json
{
  "question": "Lis la ressource Demo_Eolienne",
  "confirm": false
}
```

Delete it only if it was created for this test:

```json
{
  "question": "Supprime la ressource Demo_Eolienne",
  "confirm": false
}
```

The translator previews writes before confirmation. Deletion removes the resource's outgoing and incoming triples. Verify the result afterward, and remember that confirmed changes persist in `backend/data/working_graph.ttl`.

## 4. Run SPARQL through FastAPI

Use `POST /api/sparql/query` for SELECT/ASK queries. The request body is JSON with a `query` string:

```json
{
  "query": "PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>\nSELECT ?source WHERE { ?source a sg:Eolienne . }"
}
```

The response contains `rows` and `count`. For SPARQL updates, use `POST /api/sparql/update` with an `update` string instead. Updates persist; use only the temporary-resource example in the write section below.

The shared prefix used in the examples is:

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
```

## 5. SPARQL question bank: beginner

For each question, run the query with `POST /api/sparql/query` and explain what the pattern or filter does.

### 1. List all wind turbines

**Question:** Which resources are wind turbines?

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT ?turbine
WHERE {
  ?turbine a sg:Eolienne .
}
ORDER BY ?turbine
```

### 2. Show each wind turbine's production capacity

**Question:** How much production capacity does each wind turbine have?

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT ?turbine ?capacity
WHERE {
  ?turbine a sg:Eolienne ;
           sg:capaciteProduction ?capacity .
}
ORDER BY DESC(?capacity)
```

### 3. Find production sources above a threshold

**Question:** Which energy sources have production capacity above 500?

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT ?source ?capacity
WHERE {
  ?source a sg:SourceEnergie ;
          sg:capaciteProduction ?capacity .
  FILTER(?capacity > 500)
}
ORDER BY DESC(?capacity)
```

### 4. Search resource identifiers by city text

**Question:** Which resource identifiers contain “sfax”?

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT ?resource
WHERE {
  ?resource a ?type .
  FILTER(CONTAINS(LCASE(STR(?resource)), "sfax"))
}
ORDER BY ?resource
```

### 5. List production sources and their inverters

**Question:** Which inverter is used by each energy source?

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT ?source ?inverter
WHERE {
  ?source a sg:SourceEnergie ;
          sg:utiliseOnduleur ?inverter .
}
ORDER BY ?source
```

### 6. Show lines and their managers

**Question:** Which organization manages each transmission line?

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT ?line ?manager
WHERE {
  ?line a sg:LigneTransport ;
        sg:gerePar ?manager .
}
```

## 6. SPARQL question bank: intermediate

### 7. Find sources connected to high-voltage lines

**Question:** Which energy sources connect to a high-voltage line, and what is each line's manager?

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT DISTINCT ?source ?line ?manager
WHERE {
  ?source a sg:SourceEnergie ;
          sg:estConnecteA ?line .
  ?line a sg:HauteTension ;
        sg:gerePar ?manager .
}
ORDER BY ?source
```

### 8. Find sources producing energy for buildings

**Question:** Which sources produce energy for which buildings?

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT ?source ?building
WHERE {
  ?source sg:produitEnergie ?building .
}
ORDER BY ?building
```

### 9. Find batteries and the sources they store energy from

**Question:** Which batteries are related to which energy sources?

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT ?battery ?source
WHERE {
  ?battery a sg:Batterie ;
           sg:stockeEnergie ?source .
  ?source a sg:SourceEnergie .
}
```

### 10. Show source capacity and optional efficiency

**Question:** List sources with their capacity, including efficiency when it is recorded.

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT ?source ?capacity ?efficiency
WHERE {
  ?source a sg:SourceEnergie ;
          sg:capaciteProduction ?capacity .
  OPTIONAL { ?source sg:rendement ?efficiency . }
}
ORDER BY DESC(?capacity)
```

### 11. Count sources by type

**Question:** How many resources are there in each selected source class?

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT ?type (COUNT(DISTINCT ?resource) AS ?total)
WHERE {
  VALUES ?type {
    sg:Eolienne
    sg:PanneauSolaire
    sg:Batterie
  }
  ?resource a ?type .
}
GROUP BY ?type
ORDER BY DESC(?total)
```

### 12. Calculate average production by source type

**Question:** What is the average capacity for wind turbines and solar panels?

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT ?type (AVG(?capacity) AS ?averageCapacity)
WHERE {
  VALUES ?type {
    sg:Eolienne
    sg:PanneauSolaire
  }
  ?resource a ?type ;
            sg:capaciteProduction ?capacity .
}
GROUP BY ?type
```

This aggregate can also be asked in `/ask` using the natural-language example in section 3. Use the SPARQL console here to inspect and explain the actual aggregate query.

### 13. Find types with more than three resources

**Question:** Which selected classes have more than three individuals?

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT ?type (COUNT(DISTINCT ?resource) AS ?total)
WHERE {
  VALUES ?type {
    sg:Eolienne
    sg:PanneauSolaire
    sg:Batterie
    sg:LigneTransport
  }
  ?resource a ?type .
}
GROUP BY ?type
HAVING(COUNT(DISTINCT ?resource) > 3)
ORDER BY DESC(?total)
```

### 14. Find resources with a known capacity but no recorded efficiency

**Question:** Which energy sources have production capacity but no rendement value?

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT ?source ?capacity
WHERE {
  ?source a sg:SourceEnergie ;
          sg:capaciteProduction ?capacity .
  FILTER NOT EXISTS { ?source sg:rendement ?efficiency . }
}
ORDER BY DESC(?capacity)
```

## 7. SPARQL question bank: advanced

### 15. Compare each source with the global average capacity

**Question:** Which energy sources have higher capacity than the average across all energy sources?

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT ?source ?capacity
WHERE {
  ?source a sg:SourceEnergie ;
          sg:capaciteProduction ?capacity .
  {
    SELECT (AVG(?allCapacity) AS ?average)
    WHERE {
      ?anySource a sg:SourceEnergie ;
                 sg:capaciteProduction ?allCapacity .
    }
  }
  FILTER(?capacity > ?average)
}
ORDER BY DESC(?capacity)
```

### 16. Find buildings supplied by sources above a threshold

**Question:** Which buildings receive energy from a source whose production capacity is at least 500?

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT DISTINCT ?building ?source ?capacity
WHERE {
  ?source a sg:SourceEnergie ;
          sg:produitEnergie ?building ;
          sg:capaciteProduction ?capacity .
  FILTER(?capacity >= 500)
}
ORDER BY DESC(?capacity)
```

### 17. Find lines either managed by an operator or above a voltage threshold

**Question:** List lines that have a manager or a voltage greater than 30, and show whichever values exist.

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT DISTINCT ?line ?manager ?voltage
WHERE {
  ?line a sg:LigneTransport .
  OPTIONAL { ?line sg:gerePar ?manager . }
  OPTIONAL { ?line sg:tensionLigne ?voltage . }
  FILTER(BOUND(?manager) || (?voltage > 30))
}
ORDER BY ?line
```

### 18. Find high-capacity sources that do not connect to a high-voltage line

**Question:** Which sources above 500 are not connected to any high-voltage line?

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT ?source ?capacity
WHERE {
  ?source a sg:SourceEnergie ;
          sg:capaciteProduction ?capacity .
  FILTER(?capacity > 500)
  FILTER NOT EXISTS {
    ?source sg:estConnecteA ?line .
    ?line a sg:HauteTension .
  }
}
ORDER BY DESC(?capacity)
```

### 19. Inspect a resource's direct outgoing facts

**Question:** What facts are recorded directly about `Eolienne_Sfax1`?

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT ?predicate ?value
WHERE {
  sg:Eolienne_Sfax1 ?predicate ?value .
}
ORDER BY ?predicate
```

### 20. Find resources connected through a line to a building

**Question:** Which sources connect to a line that transports energy to a building?

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT DISTINCT ?source ?line ?building
WHERE {
  ?source a sg:SourceEnergie ;
          sg:estConnecteA ?line .
  ?line a sg:LigneTransport ;
        sg:transporteVers ?building .
}
ORDER BY ?source
```

If a query returns no rows, that can mean the data contains no matching triples. Check the property/class spelling and inspect the relevant resource with `GET /api/individuals/{item_id}` before assuming the query is invalid.

## 8. Safe SPARQL update exercise

Only run updates on an unused temporary identifier. The following example creates a resource, verifies it, changes its capacity, verifies again, and then deletes its outgoing statements.

### Create

Use `POST /api/sparql/update`:

```json
{
  "update": "PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>\nINSERT DATA { sg:Demo_API_Wind a sg:Eolienne ; sg:capaciteProduction 650 . }"
}
```

### Verify

Use `POST /api/sparql/query`:

```json
{
  "query": "PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>\nSELECT ?property ?value WHERE { sg:Demo_API_Wind ?property ?value }"
}
```

### Update

Use `POST /api/sparql/update`:

```json
{
  "update": "PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>\nDELETE { sg:Demo_API_Wind sg:capaciteProduction 650 }\nINSERT { sg:Demo_API_Wind sg:capaciteProduction 720 }\nWHERE { sg:Demo_API_Wind sg:capaciteProduction 650 }"
}
```

Run the verify query again and confirm that the capacity is `720`.

### Delete and verify cleanup

Use `POST /api/sparql/update`:

```json
{
  "update": "PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>\nDELETE WHERE { sg:Demo_API_Wind ?property ?value }"
}
```

Run the verify query one last time; it should return zero rows. This example creates no incoming links, so deleting its outgoing triples is sufficient. The API's individual DELETE route also removes incoming links.

## Important notes for the demonstration

- The NLP endpoint translates a limited set of French/English patterns into SPARQL; it is not an unrestricted AI assistant.
- `POST /api/sparql/query` is for query operations such as `SELECT` and `ASK`. Use `POST /api/sparql/update` for `INSERT`, `DELETE`, or other updates.
- Updates are persistent in `backend/data/working_graph.ttl`; do not test destructive queries on real project resources.
- The ontology and dataset are authoritative for names and relationships. If a complex query returns no results, explain the result and verify the data rather than changing the query to claim a result that is not present.




/////////////////////
Open the Administration · CRUD & SPARQL page.
Click + Nouvelle ressource.
Enter a unique local identifier, choose a class, and provide properties as JSON. For example:
Identifiant local: Panneau_Solaire_Demo
Classe: PanneauSolaire
Propriétés:



{
  "nom": "Panneau de démonstration",
  "capaciteProduction": 650,
  "rendement": 20.5
}
