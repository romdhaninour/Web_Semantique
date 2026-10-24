from pathlib import Path

root = Path(__file__).resolve().parent
out = root / 'smartgrid_seed.ttl'

lines = [
    '@prefix sg: <http://www.semanticweb.org/smartgrid-ontology#> .',
    '@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .',
    '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .',
    '@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .',
    '',
    '# Core classes',
    'sg:SourceGrandeCapacite a owl:Class .',
    'sg:GrosConsommateur a owl:Class .',
    '',
    '# Required individuals',
]

# Standard mandatory individuals
mandatory = {
    'PanneauSolaire_ESPRIT1': ('sg:PanneauSolaire', 50.0, 18.5, 'sg:BatimentESPRIT', 'sg:Onduleur_SMA1', 'sg:LigneHT_Tunis_Sfax'),
    'Eolienne_Bizerte1': ('sg:Eolienne', 300.0, 32.0, 'sg:BatimentResidentiel1', 'sg:Onduleur_SMA1', 'sg:LigneHT_Tunis_Sfax'),
    'Eolienne_Sfax1': ('sg:Eolienne', 600.0, 35.0, 'sg:BatimentIndustriel1', 'sg:Onduleur_SMA1', 'sg:LigneHT_Tunis_Sfax'),
    'Batterie_Lithium1': ('sg:Batterie', 100.0, None, 'sg:PanneauSolaire_ESPRIT1', None, None),
    'StationPompage_Zaghouan1': ('sg:StationPompage', 5000.0, None, 'sg:Eolienne_Bizerte1', None, None),
    'BatimentESPRIT': ('sg:Tertiaire', 8000.0, 'Campus ESPRIT', 'sg:Compteur_ESPRIT1', None, None),
    'BatimentResidentiel1': ('sg:Residentiel', 4500.0, 'Résidence El Manar', 'sg:Compteur_Residentiel1', None, None),
    'BatimentIndustriel1': ('sg:Industriel', 25000.0, 'Usine Sfax', 'sg:Compteur_Industriel1', None, None),
    'LigneHT_Tunis_Sfax': ('sg:HauteTension', 225.0, 270.0, 'sg:GestionnaireReseau_STEG', None, 'sg:BatimentIndustriel1'),
    'LigneMT_Ariana1': ('sg:MoyenneTension', 30.0, 15.0, 'sg:GestionnaireReseau_STEG', None, 'sg:BatimentResidentiel1'),
    'Compteur_ESPRIT1': ('sg:Compteur', None, None, None, None, None),
    'Compteur_Residentiel1': ('sg:Compteur', None, None, None, None, None),
    'Compteur_Industriel1': ('sg:Compteur', None, None, None, None, None),
    'Onduleur_SMA1': ('sg:Onduleur', None, None, None, None, None),
    'GestionnaireReseau_STEG': ('sg:GestionnaireReseau', None, None, None, None, None),
}

for name, values in mandatory.items():
    kind, *rest = values
    lines.append(f'sg:{name} a {kind} .')
    if kind.startswith('sg:PanneauSolaire') or kind.startswith('sg:Eolienne'):
        lines.append(f'sg:{name} sg:capaciteProduction {rest[0]} .')
        lines.append(f'sg:{name} sg:rendement {rest[1]} .')
    elif kind.startswith('sg:Batterie') or kind.startswith('sg:StationPompage'):
        lines.append(f'sg:{name} sg:capaciteStockage {rest[0]} .')
    elif kind.startswith('sg:Batiment'):
        lines.append(f'sg:{name} sg:consommationAnnuelle {rest[0]} .')
        lines.append(f'sg:{name} sg:nomBatiment "{rest[1]}" .')
    elif kind.startswith('sg:Ligne'):
        lines.append(f'sg:{name} sg:tensionLigne {rest[0]} .')
        lines.append(f'sg:{name} sg:longueurLigne {rest[1]} .')

# add relation triples for mandatory individuals
base_relations = [
    ('PanneauSolaire_ESPRIT1', 'sg:produitEnergie', 'BatimentESPRIT'),
    ('Eolienne_Bizerte1', 'sg:produitEnergie', 'BatimentResidentiel1'),
    ('Eolienne_Sfax1', 'sg:produitEnergie', 'BatimentIndustriel1'),
    ('Batterie_Lithium1', 'sg:stockeEnergie', 'PanneauSolaire_ESPRIT1'),
    ('StationPompage_Zaghouan1', 'sg:stockeEnergie', 'Eolienne_Bizerte1'),
    ('PanneauSolaire_ESPRIT1', 'sg:estConnecteA', 'LigneHT_Tunis_Sfax'),
    ('Eolienne_Bizerte1', 'sg:estConnecteA', 'LigneHT_Tunis_Sfax'),
    ('Eolienne_Sfax1', 'sg:estConnecteA', 'LigneHT_Tunis_Sfax'),
    ('LigneHT_Tunis_Sfax', 'sg:transporteVers', 'BatimentESPRIT'),
    ('LigneHT_Tunis_Sfax', 'sg:transporteVers', 'BatimentIndustriel1'),
    ('LigneMT_Ariana1', 'sg:transporteVers', 'BatimentResidentiel1'),
    ('LigneHT_Tunis_Sfax', 'sg:gerePar', 'GestionnaireReseau_STEG'),
    ('LigneMT_Ariana1', 'sg:gerePar', 'GestionnaireReseau_STEG'),
    ('BatimentESPRIT', 'sg:possedeCompteur', 'Compteur_ESPRIT1'),
    ('BatimentResidentiel1', 'sg:possedeCompteur', 'Compteur_Residentiel1'),
    ('BatimentIndustriel1', 'sg:possedeCompteur', 'Compteur_Industriel1'),
    ('PanneauSolaire_ESPRIT1', 'sg:utiliseOnduleur', 'Onduleur_SMA1'),
    ('Eolienne_Bizerte1', 'sg:utiliseOnduleur', 'Onduleur_SMA1'),
    ('Eolienne_Sfax1', 'sg:utiliseOnduleur', 'Onduleur_SMA1'),
]
for subject, predicate, obj in base_relations:
    lines.append(f'sg:{subject} {predicate} sg:{obj} .')

# Additional realistic Tunisian individuals (60+ total)
source_names = [
    ('PanneauSolaire_Bizerte1', 520.0, 20.0), ('PanneauSolaire_Kebili1', 470.0, 19.2), ('PanneauSolaire_Tozeur1', 610.0, 20.8),
    ('PanneauSolaire_Gabes1', 495.0, 19.1), ('PanneauSolaire_Sousse1', 720.0, 21.1), ('PanneauSolaire_Nabeul1', 800.0, 21.5),
    ('PanneauSolaire_Ariana1', 540.0, 20.5), ('Eolienne_Kebili1', 510.0, 34.0), ('Eolienne_Gabes1', 670.0, 36.0), ('Eolienne_Sousse1', 580.0, 33.5),
    ('Eolienne_Tozeur1', 610.0, 34.8), ('Eolienne_Nabeul1', 720.0, 35.5), ('Eolienne_Ariana1', 490.0, 32.4), ('Eolienne_Monastir1', 760.0, 36.5)
]
for name, capacity, eff in source_names:
    kind = 'sg:PanneauSolaire' if 'Panneau' in name else 'sg:Eolienne'
    lines.append(f'sg:{name} a {kind} .')
    lines.append(f'sg:{name} sg:capaciteProduction {capacity} .')
    lines.append(f'sg:{name} sg:rendement {eff} .')
    lines.append(f'sg:{name} sg:utiliseOnduleur sg:Onduleur_SMA1 .')

storage_names = [
    ('Batterie_Gabes1', 1500.0), ('Batterie_Sousse1', 1800.0), ('Batterie_Tozeur1', 2100.0), ('StationPompage_Kebili1', 6000.0),
    ('StationPompage_Gabes1', 7000.0), ('StationPompage_Sousse1', 6000.0)
]
for name, cap in storage_names:
    kind = 'sg:Batterie' if 'Batterie' in name else 'sg:StationPompage'
    lines.append(f'sg:{name} a {kind} .')
    lines.append(f'sg:{name} sg:capaciteStockage {cap} .')

buildings = [
    ('BatimentKebili1', 'sg:Residentiel', 6800.0, 'Résidence Kebili'), ('BatimentGabes1', 'sg:Industriel', 19000.0, 'Usine Gabes'),
    ('BatimentTozeur1', 'sg:Tertiaire', 12000.0, 'Centre Tozeur'), ('BatimentSousse1', 'sg:Tertiaire', 9800.0, 'Campus Sousse'),
    ('BatimentNabeul1', 'sg:Residentiel', 5200.0, 'Cité Nabeul'), ('BatimentAriana1', 'sg:Tertiaire', 14000.0, 'Campus Ariana'),
    ('BatimentMonastir1', 'sg:Industriel', 28000.0, 'Zone Industrielle Monastir'), ('BatimentKairouan1', 'sg:Residentiel', 4300.0, 'Résidence Kairouan')
]
for name, kind, cons, label in buildings:
    lines.append(f'sg:{name} a {kind} .')
    lines.append(f'sg:{name} sg:consommationAnnuelle {cons} .')
    lines.append(f'sg:{name} sg:nomBatiment "{label}" .')
    meter = f'Compteur_{name}'
    lines.append(f'sg:{meter} a sg:Compteur .')
    lines.append(f'sg:{name} sg:possedeCompteur sg:{meter} .')

lines += [
    'sg:Compteur_BatimentKebili1 a sg:Compteur .',
    'sg:Compteur_BatimentGabes1 a sg:Compteur .',
    'sg:Compteur_BatimentTozeur1 a sg:Compteur .',
    'sg:Compteur_BatimentSousse1 a sg:Compteur .',
    'sg:Compteur_BatimentNabeul1 a sg:Compteur .',
    'sg:Compteur_BatimentAriana1 a sg:Compteur .',
    'sg:Compteur_BatimentMonastir1 a sg:Compteur .',
    'sg:Compteur_BatimentKairouan1 a sg:Compteur .',
]

lines += [
    'sg:BatimentKebili1 sg:possedeCompteur sg:Compteur_BatimentKebili1 .',
    'sg:BatimentGabes1 sg:possedeCompteur sg:Compteur_BatimentGabes1 .',
    'sg:BatimentTozeur1 sg:possedeCompteur sg:Compteur_BatimentTozeur1 .',
    'sg:BatimentSousse1 sg:possedeCompteur sg:Compteur_BatimentSousse1 .',
    'sg:BatimentNabeul1 sg:possedeCompteur sg:Compteur_BatimentNabeul1 .',
    'sg:BatimentAriana1 sg:possedeCompteur sg:Compteur_BatimentAriana1 .',
    'sg:BatimentMonastir1 sg:possedeCompteur sg:Compteur_BatimentMonastir1 .',
    'sg:BatimentKairouan1 sg:possedeCompteur sg:Compteur_BatimentKairouan1 .',
]

lines += [
    'sg:BatimentESPRIT sg:produitEnergie sg:PanneauSolaire_ESPRIT1 .',
    'sg:BatimentResidentiel1 sg:produitEnergie sg:Eolienne_Bizerte1 .',
    'sg:BatimentIndustriel1 sg:produitEnergie sg:Eolienne_Sfax1 .',
    'sg:BatimentGabes1 sg:produitEnergie sg:PanneauSolaire_Sousse1 .',
    'sg:BatimentTozeur1 sg:produitEnergie sg:PanneauSolaire_Tozeur1 .',
    'sg:BatimentAriana1 sg:produitEnergie sg:PanneauSolaire_Ariana1 .',
]

for source, cap, _ in source_names:
    lines.append(f'sg:{source} a sg:SourceEnergie .')

for source in [
    'PanneauSolaire_Bizerte1', 'PanneauSolaire_Kebili1', 'PanneauSolaire_Tozeur1', 'PanneauSolaire_Gabes1', 'PanneauSolaire_Sousse1',
    'PanneauSolaire_Nabeul1', 'PanneauSolaire_Ariana1', 'Eolienne_Kebili1', 'Eolienne_Gabes1', 'Eolienne_Sousse1', 'Eolienne_Tozeur1',
    'Eolienne_Nabeul1', 'Eolienne_Ariana1', 'Eolienne_Monastir1'
]:
    if 'Panneau' in source:
        lines.append(f'sg:{source} sg:estConnecteA sg:LigneHT_Tunis_Sfax .')
    else:
        lines.append(f'sg:{source} sg:estConnecteA sg:LigneMT_Ariana1 .')

lines += [
    'sg:LigneHT_Tunis_Sfax sg:transporteVers sg:BatimentKebili1 .',
    'sg:LigneHT_Tunis_Sfax sg:transporteVers sg:BatimentGabes1 .',
    'sg:LigneHT_Tunis_Sfax sg:transporteVers sg:BatimentTozeur1 .',
    'sg:LigneMT_Ariana1 sg:transporteVers sg:BatimentAriana1 .',
    'sg:LigneMT_Ariana1 sg:transporteVers sg:BatimentNabeul1 .',
    'sg:LigneHT_Tunis_Sfax sg:gerePar sg:GestionnaireReseau_STEG .',
    'sg:LigneMT_Ariana1 sg:gerePar sg:GestionnaireReseau_STEG .',
    'sg:Onduleur_SMA1 a sg:Onduleur .',
    'sg:GestionnaireReseau_STEG a sg:GestionnaireReseau .',
]

# Multi-line, explicit high-level labels to create many entities for stats
for name in ['Batterie_Gabes1', 'Batterie_Sousse1', 'Batterie_Tozeur1', 'StationPompage_Kebili1', 'StationPompage_Gabes1', 'StationPompage_Sousse1', 'BatimentKebili1', 'BatimentGabes1', 'BatimentTozeur1', 'BatimentSousse1', 'BatimentNabeul1', 'BatimentAriana1', 'BatimentMonastir1', 'BatimentKairouan1']:
    lines.append(f'sg:{name} a sg:SourceEnergie .')

# Lines and managers
for i in range(1, 8):
    line = f'LigneHT_Tunis_{i}'
    lines.append(f'sg:{line} a sg:HauteTension .')
    lines.append(f'sg:{line} sg:tensionLigne {220 + i} .')
    lines.append(f'sg:{line} sg:longueurLigne {120 + i * 35} .')
    lines.append(f'sg:{line} sg:gerePar sg:GestionnaireReseau_STEG .')

for i in range(1, 9):
    line = f'LigneMT_Ariana{i}'
    lines.append(f'sg:{line} a sg:MoyenneTension .')
    lines.append(f'sg:{line} sg:tensionLigne {30 + i} .')
    lines.append(f'sg:{line} sg:longueurLigne {12 + i * 4} .')
    lines.append(f'sg:{line} sg:gerePar sg:GestionnaireReseau_STEG .')

# final line to ensure file ends cleanly
lines.append('')
out.write_text('\n'.join(lines), encoding='utf-8')
print(f'Wrote {out} with {len(lines)} lines')
