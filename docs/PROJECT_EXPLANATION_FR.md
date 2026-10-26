# Smart Grid Sémantique — présentation du projet

## Objectif

Ce projet est une application web de démonstration d’un réseau électrique intelligent tunisien. Il montre comment représenter et interroger des données de réseau à l’aide du Web sémantique : équipements, classes, propriétés et relations sont stockés dans un graphe RDF, plutôt que dans des enregistrements isolés.

L’application permet de consulter ces données, de les visualiser, de lancer des requêtes SPARQL et de poser des questions en français ou en anglais. Le traitement NLP est local et fondé sur des règles et des lexiques : il ne fait appel à aucun service LLM.

## Ce qui a été réalisé

- Une ontologie RDF décrivant le domaine du réseau électrique.
- Un jeu de données Turtle de démonstration, avec des individus et leurs propriétés.
- Une API REST Python/FastAPI qui lit et modifie le graphe avec RDFLib.
- Une interface Angular avec tableau de bord, questionnement NLP, exploration des individus, visualisation du graphe, carte schématique et administration.
- Un traducteur français/anglais vers SPARQL qui prend en charge certaines recherches, filtres numériques et opérations CRUD guidées.
- Une console SPARQL, un catalogue de requêtes prédéfinies et un raisonneur démonstratif.
- Des tests backend et des scripts de lancement et de vérification.

## Technologies et architecture

```text
Navigateur
   │
   ▼
Angular ── requêtes HTTP /api ──► FastAPI
                                      │
                     ┌────────────────┴───────────────┐
                     ▼                                ▼
                  RDFLib                     Traducteur NLTK
                     │                                │
                     └────────── SPARQL ◄────────────┘
                                      │
                                      ▼
                Ontologie RDF + données Turtle
```

- **Frontend :** Angular et TypeScript. Les pages sont accessibles depuis la navigation; le service partagé `ApiService` centralise les appels HTTP.
- **Backend :** FastAPI expose les données et les opérations sous forme de routes REST JSON.
- **Données sémantiques :** RDFLib charge l’ontologie RDF/XML, puis les données initiales et le graphe de travail Turtle.
- **Requêtes :** RDFLib exécute les requêtes SPARQL sur le graphe courant.
- **NLP :** NLTK fournit la tokenisation et la racinisation. Des marqueurs linguistiques, lexiques bilingues et règles extraient l’intention et les critères, puis sélectionnent un gabarit SPARQL autorisé.

## Comment fonctionne une demande

### Consultation et exploration

1. Une page Angular appelle une route `/api` via `ApiService`.
2. FastAPI charge le graphe RDF courant avec `load_graph()`.
3. Le backend calcule les statistiques, classes, individus, propriétés ou relations demandés.
4. FastAPI renvoie les résultats en JSON et Angular met à jour l’écran.

Les classes et propriétés de l’ontologie sont distinguées des individus du réseau afin que les statistiques et les visualisations portent sur les équipements et les ressources du domaine.

### Question en langage naturel

1. L’utilisateur envoie une question en français ou en anglais.
2. Le traducteur normalise et découpe les mots, estime la langue et applique le stemmer NLTK correspondant.
3. Les règles reconnaissent les concepts métier (par exemple une classe d’équipement), les villes, les métriques, les comparateurs et les nombres.
4. Le traducteur construit une requête à partir de gabarits SPARQL connus, puis RDFLib l’exécute.
5. L’API renvoie les résultats, la requête générée et des informations d’analyse comme les tokens et les entités reconnues.

Pour CREATE, UPDATE et DELETE, la première requête produit un aperçu sans mutation. L’utilisateur doit confirmer; DELETE demande également une confirmation navigateur. Lors de la confirmation, le backend retraduit et revalide la demande. Une formulation non prise en charge renvoie une erreur explicite au lieu de résultats inventés.

### Modification des données

Les opérations CRUD et les mises à jour SPARQL modifient le graphe en mémoire, puis sauvegardent le graphe obtenu dans le fichier de travail Turtle. À la prochaine lecture, le backend recharge l’ontologie, les données initiales et ce fichier de travail.

## Pages et fonctionnalités

| Page | Rôle |
|---|---|
| Accueil | Statistiques calculées à partir du graphe RDF |
| Questionner la grille | Traduction de questions FR/EN en SPARQL et affichage des résultats |
| Explorer | Recherche et filtrage des individus, consultation de leurs propriétés |
| Graphe | Visualisation des individus et relations RDF |
| Carte | Regroupement schématique des ressources par ville |
| Administration | CRUD, requêtes SPARQL et lancement du raisonneur |

La carte déduit les villes depuis les identifiants et les affiche sur une silhouette schématique; ce ne sont pas des coordonnées GPS réelles. Le raisonneur applique des règles numériques ciblées et ne constitue pas un moteur complet d’inférence OWL.

## Données et persistance

Les principales sources sont :

- `ontology/Web_Semantique_corrige.rdf` : définition de l’ontologie.
- `backend/data/smartgrid_seed.ttl` : données initiales de démonstration.
- `backend/data/working_graph.ttl` : modifications persistantes effectuées dans l’application.

Le graphe de travail complète les sources initiales. Pour retrouver les données de départ, arrêtez l’application puis supprimez explicitement `backend/data/working_graph.ttl`.

## Lancer et vérifier

Sous Windows, double-cliquez sur `Start Smart Grid.bat` à la racine du dépôt. Le lanceur démarre l’API et l’interface, puis ouvre l’application dans le navigateur. L’API écoute par défaut sur le port 8002; sa documentation interactive est disponible à `http://127.0.0.1:8002/docs`. Aucun compte n’est requis pour la démonstration.

Vérifications développeur depuis la racine :

```powershell
python -m pytest backend/tests/test_backend.py -q
Set-Location frontend
npm run build
```

## Structure utile du dépôt

- `frontend/src/app/pages/` : pages Angular.
- `frontend/src/app/services/api.service.ts` : client HTTP partagé.
- `backend/app/main.py` : routes FastAPI.
- `backend/app/ontology_store.py` : chargement, sauvegarde et lecture du graphe.
- `backend/app/sparql_service.py` : exécution SPARQL.
- `backend/app/nlp_service.py` : analyse linguistique et traduction en requêtes.
- `backend/tests/` : tests backend.
- `scripts/` et `Start Smart Grid.bat` : lancement, configuration et vérifications.

## Limites du démonstrateur

Le traducteur comprend une grammaire et un vocabulaire définis; il ne comprend pas toutes les paraphrases ni les demandes générales. Le score de confiance NLP est heuristique, pas une probabilité calibrée. L’accès aux opérations d’administration n’est pas protégé par authentification : le projet est destiné à une démonstration locale, pas à un déploiement de production.

Pour le détail du pipeline NLP, consulter [NLP_TOOLS.md](./NLP_TOOLS.md). Le [guide de l’application](./APP_GUIDE.md) décrit les écrans et les parcours de démonstration.
