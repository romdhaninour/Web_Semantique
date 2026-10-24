from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BASE_DIR.parent
ONTOLOGY_FILE = ROOT_DIR / 'ontology' / 'Web_Semantique_corrige.rdf'
SEED_FILE = BASE_DIR / 'data' / 'smartgrid_seed.ttl'
WORKING_FILE = BASE_DIR / 'data' / 'working_graph.ttl'
