# Guide de validation du projet selon la grille

Ce guide transforme la grille d’évaluation du cours de Web Sémantique en vérifications concrètes pour l’application Smart Grid. Il répartit les démonstrations entre cinq membres et précise les preuves à montrer au validateur.

## Critères de la grille

| Critère | Points | Responsable principal |
|---|---:|---|
| Requêtes SPARQL | 4 | Étudiant 2 |
| Individus | 2 | Étudiant 1 |
| Scénario | 2 | Étudiant 5, avec toute l’équipe |
| API IA | 4 | Étudiant 3 |
| Interfaces graphiques | 3 | Étudiant 4 |
| Communication BE et FE | 3 | Étudiant 5 |
| Valeur ajoutée | 2 | Étudiant 1 |
| **Total** | **20** | |

Les responsables sont les présentateurs principaux, pas les seuls à devoir comprendre leur partie. Remplacez « Étudiant 1 » à « Étudiant 5 » par les noms du groupe avant la présentation.

## 1. Préparer une validation propre

1. Depuis la racine du dépôt, lancez `Start Smart Grid.bat`.
2. Attendez l’ouverture de l’interface, puis vérifiez que l’accueil affiche les statistiques.
3. Ouvrez `http://127.0.0.1:8002/api/health` : le statut doit être `ok` et les sources de données doivent être présentes.
4. Ouvrez `http://127.0.0.1:8002/api/validation/checks`. Les indicateurs `individuals_ok`, `classes_ok`, `catalog_ok` et `overall` doivent être `true`.
5. Gardez `http://127.0.0.1:8002/docs` ouvert pour les démonstrations directes de l’API.
6. Vérifiez que `Eolienne_Sfax1` est visible dans **Explorer**.
7. Choisissez un identifiant temporaire inédit pour les tests CRUD, par exemple `Demo_Groupe_2026`. Ne réutilisez pas une ressource existante.

L’endpoint de validation vérifie notamment qu’il y a au moins 60 individus, 19 classes et 20 requêtes dans le catalogue. Il complète les démonstrations, mais ne remplace pas les preuves demandées par la grille.

## 2. Démonstration et validation par membre

### Étudiant 1 — Individus (2 pts) et valeur ajoutée (2 pts)

**À valider et à montrer**

1. Dans l’ontologie `ontology/Web_Semantique_corrige.rdf`, montrer des classes du domaine et une relation, par exemple `estConnecteA`, avec son domaine et son range.
2. Montrer une propriété de données, par exemple `capaciteProduction`.
3. Dans **Explorer**, sélectionner `Eolienne_Sfax1`. Expliquer son type, ses valeurs et, si disponibles, ses relations avec d’autres ressources.
4. Dans **Administration**, exécuter le raisonneur et montrer les classifications ajoutées. Une règle de démonstration classe les sources de production de capacité supérieure à 500 comme `SourceGrandeCapacite`.

**Preuves pour le validateur**

- Un individu concret, son type et ses propriétés RDF.
- Une relation RDF entre ressources, si elle existe pour l’individu choisi.
- Une classification ajoutée par le raisonneur.

**À préciser :** le raisonneur est une fonctionnalité ciblée par règles numériques, pas un moteur complet d’inférence OWL.

### Étudiant 2 — Requêtes SPARQL (4 pts)

Dans **Administration · CRUD & SPARQL**, montrer des lectures, un filtre et des modifications vérifiées :

1. Exécuter un `SELECT` qui retourne des ressources du graphe.
2. Montrer un `FILTER`, par exemple les sources dont la capacité dépasse 500.
3. Effectuer une recherche textuelle, par exemple sur `sfax`.
4. Créer une ressource temporaire :

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
INSERT DATA {
  sg:Demo_Groupe_2026 a sg:Eolienne ;
    sg:capaciteProduction 650 .
}
```

5. Vérifier la création avec un `SELECT` :

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT ?property ?value
WHERE { sg:Demo_Groupe_2026 ?property ?value }
```

6. Modifier la capacité de `650` à `720` avec `DELETE` / `INSERT`, puis relancer le `SELECT` pour vérifier la nouvelle valeur :

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
DELETE { sg:Demo_Groupe_2026 sg:capaciteProduction 650 }
INSERT { sg:Demo_Groupe_2026 sg:capaciteProduction 720 }
WHERE { sg:Demo_Groupe_2026 sg:capaciteProduction 650 }
```

7. Supprimer la ressource temporaire et vérifier qu’elle ne retourne plus de résultat :

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
DELETE WHERE { sg:Demo_Groupe_2026 ?property ?value }
```

**Preuves pour le validateur**

- Afficher les requêtes exécutées et leurs résultats.
- Vérifier chaque mutation par une lecture après l’écriture.
- Montrer que la ressource de démonstration a bien été supprimée.

Ne lancez pas l’UPDATE avant l’INSERT : le `WHERE` doit retrouver la valeur `650`. Cet exemple n’ajoute pas de relation entrante vers la ressource.

### Étudiant 3 — API IA (4 pts)

La fonctionnalité évaluée est le traitement de questions en langage naturel. Présentez-la fidèlement comme un traducteur local à règles et lexiques utilisant NLTK, et non comme un modèle génératif ou un service d’IA externe.

1. Dans Swagger (`/docs`), ouvrir `POST /api/nlp/ask`.
2. Tester cette question :

```json
{
  "question": "Quelles éoliennes produisent plus de 500 kW ?",
  "confirm": false
}
```

3. Dans la réponse, montrer la langue et l’intention détectées, les entités, la métrique, le comparateur, la requête SPARQL produite et les résultats.
4. Montrer les outils déclarés par le pipeline : NLTK `TweetTokenizer` et `SnowballStemmer`.
5. Tester une question anglaise prise en charge, par exemple : `Which batteries have storage capacity at least 100 kWh?`.
6. Expliquer qu’une formulation non reconnue doit être signalée explicitement. Les opérations d’écriture nécessitent une confirmation; ne confirmez une mutation que si vous utilisez un identifiant temporaire.

**Preuves pour le validateur**

- Un appel API réellement exécuté et sa réponse.
- Le lien visible entre la question, le SPARQL généré et les résultats.
- La distinction entre ce pipeline NLP local et une API LLM externe.

### Étudiant 4 — Interfaces graphiques (3 pts)

Présenter un parcours interactif plutôt qu’une suite de captures d’écran :

1. **Accueil** : montrer les statistiques provenant du graphe.
2. **Explorer** : filtrer une classe, chercher `Eolienne_Sfax1` et ouvrir sa fiche.
3. **Graphe** : sélectionner une ressource et présenter ses relations RDF.
4. **Carte** : sélectionner une ville et montrer les ressources regroupées.
5. Montrer que la navigation permet de passer entre ces écrans.

**Preuves pour le validateur**

- Les pages chargent les données du projet.
- La recherche, le filtrage ou la sélection actualise le contenu.
- Le graphe représente des relations et la carte regroupe les ressources.

**À préciser :** la carte est schématique; les positions ne sont pas des coordonnées GPS précises des équipements.

### Étudiant 5 — Communication backend/frontend (3 pts) et scénario (2 pts)

1. Dans l’interface, afficher les statistiques ou une liste de ressources.
2. Dans Swagger, appeler `GET /api/stats` ou `GET /api/individuals` et montrer que la réponse JSON correspond aux données affichées.
3. Expliquer le trajet d’une demande :

   `Angular → requête HTTP /api → FastAPI → RDFLib/SPARQL → graphe RDF → réponse JSON → interface Angular`

4. Présenter un scénario utilisateur complet et cohérent : consulter les statistiques, poser une question NLP, examiner les résultats dans **Explorer** ou **Graphe**, puis vérifier une opération SPARQL si le temps le permet.
5. Montrer où les données sont définies et enregistrées : l’ontologie RDF/XML, les données initiales Turtle et le graphe de travail `backend/data/working_graph.ttl`.
6. Conclure en vérifiant que les ressources temporaires créées pour la présentation ont été supprimées.

**Preuves pour le validateur**

- Une réponse API reliée à son affichage frontend.
- Une explication claire du rôle du backend et du graphe RDF.
- Un scénario qui relie plusieurs fonctionnalités et se termine par un état propre.

## 3. Vérifications techniques de l’équipe

Ces commandes vérifient le backend et le build frontend. À lancer depuis la racine du dépôt :

```powershell
python -m pytest backend/tests/test_backend.py -q
Set-Location frontend
npm run build
```

Les tests vérifient notamment les routes, les données, le CRUD, SPARQL, le raisonneur et des exemples de traduction NLP. Notez le résultat et signalez honnêtement toute erreur; ne présentez pas un test non exécuté comme réussi.

## 4. Ordre conseillé pour la présentation

| Ordre | Responsable | Partie | Durée indicative |
|---:|---|---|---:|
| 1 | Étudiant 1 | Ontologie, individu, raisonneur | 2 min |
| 2 | Étudiant 2 | SELECT, FILTER et CRUD SPARQL | 3 min |
| 3 | Étudiant 3 | Question naturelle, NLTK et SPARQL produit | 3 min |
| 4 | Étudiant 4 | Écrans, recherche et visualisations | 2 min |
| 5 | Étudiant 5 | Communication API, scénario complet et conclusion | 2 min |

Prévoyez quelques minutes de marge pour le démarrage et les transitions. Les membres doivent connaître le scénario global et pouvoir répondre aux questions sur le rôle de RDF, de SPARQL et de l’API.

## 5. Checklist finale

- [ ] Les cinq noms réels remplacent « Étudiant 1 » à « Étudiant 5 » dans les documents de présentation.
- [ ] L’application démarre et `/api/health` répond avec `ok`.
- [ ] `/api/validation/checks` retourne `overall: true`.
- [ ] Chaque membre a testé sa démonstration et sait quelle preuve montrer.
- [ ] Les questions NLP choisies ont été essayées à l’avance.
- [ ] Les requêtes CRUD utilisent un identifiant temporaire inédit.
- [ ] Les ressources temporaires sont supprimées après les tests.
- [ ] Les tests backend et le build frontend ont été lancés; leurs résultats sont connus.
