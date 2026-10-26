# Semantic Smart Grid — project overview

## Purpose

This project is a web demonstration of a Tunisian smart electricity grid. It shows how to represent and query grid data using Semantic Web technologies: equipment, classes, properties, and relationships are stored in an RDF graph instead of as isolated records.

The application lets users inspect and visualize the data, run SPARQL queries, and ask questions in French or English. NLP processing runs locally and is based on rules and lexicons; it does not call an LLM service.

## What we built

- An RDF ontology describing the electricity-grid domain.
- A Turtle demonstration dataset containing individuals and their properties.
- A Python/FastAPI REST API that reads and updates the graph with RDFLib.
- An Angular interface with a dashboard, NLP question page, individual explorer, graph visualization, schematic map, and administration page.
- A French/English translator to SPARQL supporting selected searches, numeric filters, and guided CRUD operations.
- A SPARQL console, a catalog of predefined queries, and a demonstration reasoner.
- Backend tests and scripts for startup and validation.

## Technologies and architecture

```text
Browser
   │
   ▼
Angular ── HTTP requests /api ──► FastAPI
                                      │
                     ┌────────────────┴───────────────┐
                     ▼                                ▼
                  RDFLib                       NLTK translator
                     │                                │
                     └────────── SPARQL ◄────────────┘
                                      │
                                      ▼
                    RDF ontology + Turtle data
```

- **Frontend:** Angular and TypeScript. Pages are available through the navigation; the shared `ApiService` centralizes HTTP calls.
- **Backend:** FastAPI exposes data and operations through JSON REST endpoints.
- **Semantic data:** RDFLib loads the RDF/XML ontology, then the initial dataset and the Turtle working graph.
- **Queries:** RDFLib executes SPARQL queries against the current graph.
- **NLP:** NLTK provides tokenization and stemming. Language markers, bilingual lexicons, and rules extract intent and criteria, then select an allowed SPARQL template.

## How a request works

### Browsing and exploration

1. An Angular page calls an `/api` endpoint through `ApiService`.
2. FastAPI loads the current RDF graph with `load_graph()`.
3. The backend calculates or retrieves the requested statistics, classes, individuals, properties, or relationships.
4. FastAPI returns JSON and Angular updates the screen.

Ontology classes and properties are distinguished from grid individuals so that statistics and visualizations focus on domain resources and equipment.

### Natural-language questions

1. The user submits a question in French or English.
2. The translator normalizes and tokenizes the words, estimates the language, and applies the matching NLTK stemmer.
3. Rules recognize domain concepts (such as an equipment class), cities, metrics, comparators, and numbers.
4. The translator builds a query from known SPARQL templates, and RDFLib executes it.
5. The API returns the results, generated query, and analysis details such as recognized tokens and entities.

For CREATE, UPDATE, and DELETE, the first request produces a preview without changing the graph. The user must confirm; DELETE also requires a browser confirmation. On confirmation, the backend translates and validates the request again. Unsupported wording produces an explicit error instead of invented results.

### Updating data

CRUD operations and SPARQL updates modify the graph in memory and then save the resulting graph to the Turtle working file. On a later read, the backend reloads the ontology, initial data, and working file.

## Pages and features

| Page | Purpose |
|---|---|
| Home | Statistics calculated from the RDF graph |
| Ask the grid | Translate French/English questions into SPARQL and show results |
| Explorer | Search and filter individuals, inspect their properties |
| Graph | Visualize individuals and RDF relationships |
| Map | Schematic grouping of resources by city |
| Administration | CRUD, SPARQL queries, and run the reasoner |

The map infers cities from identifiers and places them on a schematic outline; these are not actual GPS coordinates. The reasoner applies targeted numeric rules and is not a complete OWL inference engine.

## Data and persistence

The main data sources are:

- `ontology/Web_Semantique_corrige.rdf`: ontology definition.
- `backend/data/smartgrid_seed.ttl`: initial demonstration data.
- `backend/data/working_graph.ttl`: persistent changes made in the application.

The working graph supplements the initial sources. To return to the original dataset, stop the application and explicitly delete `backend/data/working_graph.ttl`.

## Run and validate

On Windows, double-click `Start Smart Grid.bat` in the repository root. The launcher starts the API and frontend, then opens the application in a browser. The API uses port 8002 by default; its interactive documentation is available at `http://127.0.0.1:8002/docs`. No account is required for the demonstration.

Developer checks from the repository root:

```powershell
python -m pytest backend/tests/test_backend.py -q
Set-Location frontend
npm run build
```

## Useful repository structure

- `frontend/src/app/pages/`: Angular pages.
- `frontend/src/app/services/api.service.ts`: shared HTTP client.
- `backend/app/main.py`: FastAPI routes.
- `backend/app/ontology_store.py`: graph loading, saving, and reading.
- `backend/app/sparql_service.py`: SPARQL execution.
- `backend/app/nlp_service.py`: language analysis and query translation.
- `backend/tests/`: backend tests.
- `scripts/` and `Start Smart Grid.bat`: startup, setup, and validation.

## Demonstrator limitations

The translator has a defined grammar and vocabulary; it does not understand every paraphrase or general request. Its NLP confidence score is heuristic, not a calibrated probability. Administration operations are not protected by authentication: this project is intended for local demonstration, not production deployment.

For the NLP pipeline details, see [NLP_TOOLS.md](./NLP_TOOLS.md). The [application guide](./APP_GUIDE.md) describes the screens and demonstration walkthroughs.
