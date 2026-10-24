# Web_Semantique

Application **Smart Grid Sémantique** — démonstrateur Web sémantique pour le réseau énergétique tunisien.

L’application web représente le réseau électrique avec une ontologie RDF. Elle réunit l’exploration des individus, les visualisations, une console SPARQL avec CRUD/recherche/filtrage et un traducteur NLP/TALN français-anglais vers SPARQL basé sur NLTK. **Aucune connexion ni API de LLM n’est requise.**

## Documentation

- [Guide de l’application](docs/APP_GUIDE.md) — écrans, architecture et données.
- [Répartition selon la grille](docs/TEAM_GUIDE.md) — rôles de présentation pour les cinq membres.
- [Scénario de démonstration](docs/SCENARIO.md) — parcours détaillé en groupe.
- [Questions et scénarios de démonstration](docs/DEMO_SCENARIOS.md) — questions testées, parcours des écrans et CRUD NLP.
- [Outils NLP/TALN](docs/NLP_TOOLS.md) — pipeline NLTK, traductions et limites.

Remplacez les noms `Étudiant 1` à `Étudiant 5` par ceux du groupe avant la remise.

## Lancement sous Windows

Double-cliquez sur **Start Smart Grid.bat** à la racine. Le lanceur démarre l’API FastAPI et l’interface Angular, puis ouvre l’application. Le port frontend est choisi automatiquement s’il est occupé.

Aucun compte n’est nécessaire. L’API est aussi accessible dans Swagger sur `/docs` (port 8002 par défaut). Les journaux du lanceur sont dans `%TEMP%\smart-grid-demo`.

## Parcours

1. **Accueil** — statistiques calculées sur le graphe RDF.
2. **Questionner la grille** — traduire une question naturelle en SPARQL avec NLTK, exécuter le SPARQL et consulter la requête produite et les résultats.
3. **Explorer** — chercher des individus, filtrer par classe et afficher les propriétés.
4. **Graphe et Carte** — visualiser les relations et les regroupements schématiques par ville.
5. **Administration · CRUD & SPARQL** — créer, consulter, modifier et supprimer les individus; exécuter les requêtes SPARQL, filtres et recherches; lancer le raisonneur.

Les modifications RDF sont enregistrées dans `backend/data/working_graph.ttl`.

## Vérifications développeur

Depuis la racine :

```powershell
python -m pytest backend/tests/test_backend.py -q
Set-Location frontend
npm run build
```
