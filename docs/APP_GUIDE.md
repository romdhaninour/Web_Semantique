# Guide de présentation — Smart Grid Sémantique

## 1. Présentation du projet

Smart Grid Sémantique est une application web locale de démonstration qui représente des éléments d’un réseau électrique sous forme de données RDF. Elle permet de consulter des statistiques, d’explorer les individus et leurs propriétés, d’interroger le graphe avec SPARQL et d’effectuer quelques opérations d’administration.

Le projet met en pratique le Web sémantique : les ressources du domaine sont représentées par des identifiants, des classes et des propriétés RDF plutôt que par de simples lignes isolées dans une table.

### État des données de la démo

Le jeu de données courant contient **65 individus de la grille** et **19 classes d’ontologie**. La page d’accueil calcule également la capacité totale et la consommation annuelle à partir des valeurs présentes dans le graphe. Ces nombres décrivent le jeu de données local et peuvent évoluer lorsque des individus sont ajoutés ou supprimés.

## 2. Parcours dans l’application

### Accueil

Le tableau de bord résume le graphe : nombre d’individus, nombre de classes, capacité totale en kW et consommation annuelle en kWh. Il présente aussi quelques classes et leurs effectifs pour donner une vue d’ensemble des données disponibles.

### Questionner la grille

La page de questions transforme le texte saisi en requête SPARQL, l’exécute sur le graphe RDF et affiche l’analyse linguistique, le SPARQL produit et les résultats.

Le pipeline local s’appuie explicitement sur **NLTK**, sans API LLM ni modèle/corpus distant :

1. `TweetTokenizer` normalise la phrase et la découpe en tokens.
2. `SnowballStemmer` (français ou anglais) réduit les mots à leur racine; les marqueurs linguistiques estiment la langue.
3. Un lexique bilingue relie les expressions métier aux classes de l’ontologie et extrait entités, villes, métriques, opérateurs de comparaison et valeurs numériques.
4. Des gabarits SPARQL limités aux classes, propriétés et villes autorisées construisent une requête exécutable. L’utilisateur ne fournit jamais directement le SPARQL de cette fonctionnalité.
5. RDFLib exécute le SPARQL sur le graphe actif; l’API renvoie la requête, les caractéristiques extraites et les résultats.

Exemples pris en charge : « Quelles éoliennes produisent plus de 500 kW ? », « Which batteries have storage capacity at least 100 kWh? », « Liste les bâtiments industriels » et « Quelles éoliennes à Sfax ? ». Les comparaisons numériques couvrent supérieur, inférieur, inclusif et égal. Une question non reconnue produit une erreur explicite `422` et des conseils au lieu d’inventer des résultats.

La page prend aussi en charge une grammaire CRUD limitée : lecture d’un identifiant (« Lis la ressource Demo_Eolienne »), création avec classe/identifiant (« Crée une éolienne nommée Demo_Eolienne avec une capacité de production de 650 kW »), modification d’une propriété numérique (« Modifie la capacité de production de Demo_Eolienne à 720 kW ») et suppression (« Supprime la ressource Demo_Eolienne »). Pour CREATE/UPDATE/DELETE, l’interface présente d’abord le SPARQL sans l’exécuter; il faut le confirmer, avec une confirmation supplémentaire pour DELETE. La revalidation et la traduction ont lieu côté serveur lors de l’exécution. La suppression enlève également les relations entrantes vers la ressource. Pour revenir à l’état initial après la démonstration, supprimer le graphe de travail selon les consignes de la section Persistance.

Ce module est un traducteur NLP bilingue construit avec tokenisation, racinisation, lexiques et extraction de caractéristiques; il n’est pas un modèle génératif ni un système de compréhension générale. Les propriétés modifiables par question sont limitées aux métriques numériques reconnues par le lexique.

### Explorer les données

La page Explorer charge les individus depuis l’API. On peut filtrer par classe, rechercher par identifiant, type ou valeur de propriété, puis sélectionner un individu pour afficher ses types RDF et ses propriétés.

Les ressources affichées sont les individus du domaine, et non les classes, propriétés ou restrictions de l’ontologie.

### Graphe du réseau

La visualisation représente les individus comme des nœuds et les relations RDF entre deux individus comme des liens. La couleur dépend du type de ressource; un filtre permet d’afficher une classe particulière.

Les nœuds sont regroupés en familles (production, stockage, réseau, consommation, autres), avec filtre par classe et recherche d’identifiant. Cliquez sur un nœud pour consulter ses propriétés RDF, y compris les valeurs numériques; survolez un lien pour lire son nom. Après une modification faite sur une autre page, utilisez « Actualiser le graphe » pour recharger les données sauvegardées. Les positions sont disposées pour la visualisation et ne représentent pas des coordonnées physiques du réseau.

### Carte

La carte regroupe les individus dont l’identifiant contient le nom d’une ville connue dans l’application. Cliquer sur un marqueur affiche les ressources détectées pour cette ville.

La carte présente une silhouette géographique simplifiée de la Tunisie et place approximativement les villes connues. Le jeu de données ne fournit pas de coordonnées GPS pour les équipements : leur ville est déduite de l’identifiant et les marqueurs regroupent les ressources associées à chaque ville. Il ne s’agit donc pas d’une localisation précise de chaque équipement.

### Administration · CRUD & SPARQL

Aucun compte ni connexion n’est nécessaire. L’interface d’administration est accessible depuis la navigation et permet de filtrer les individus par classe, créer une ressource, modifier ses propriétés, la supprimer, exécuter des requêtes SPARQL et lancer le raisonneur. Ces outils sont ouverts pour faciliter l’utilisation pédagogique de la démonstration.

La console SPARQL propose un éditeur, un mode lecture `SELECT`, un mode écriture et des exemples préchargés :

- recherche de ressources;
- filtrage avec `FILTER`, par exemple capacité supérieure à 500 kW;
- recherche textuelle avec `CONTAINS`;
- création avec `INSERT DATA`;
- modification avec `DELETE` + `INSERT` + `WHERE`;
- suppression avec `DELETE WHERE`.

Les requêtes de lecture n’écrivent pas dans le graphe. Les opérations d’écriture et le raisonneur sont disponibles sans connexion; les changements sont sauvegardés dans le graphe de travail.

La même page expose un bouton pour lancer le raisonneur. Les nouveaux types inférés sont enregistrés dans le graphe de travail et présentés dans l’interface.

## 3. Modèle sémantique et données

Le graphe utilise l’espace de noms :

```text
http://www.semanticweb.org/smartgrid-ontology#
```

Les ressources sont typées avec `rdf:type`. Par exemple, un individu peut être de type `Eolienne` et `SourceEnergie`. Les propriétés représentent les valeurs littérales, telles que la capacité de production, ou les relations vers d’autres ressources, telles que la connexion d’un équipement.

Le backend charge et fusionne les sources suivantes :

1. `ontology/Web_Semantique_corrige.rdf` — définition de l’ontologie;
2. `backend/data/smartgrid_seed.ttl` — jeu de données de départ;
3. `backend/data/working_graph.ttl` — modifications créées pendant l’utilisation, lorsqu’il existe.

Le fichier de travail est une surcharge persistante; il ne remplace pas les fichiers de l’ontologie et du jeu de départ. Les modifications sont écrites au format Turtle. Pour revenir aux seules données de départ, arrêter l’application puis supprimer explicitement `backend/data/working_graph.ttl`.

## 4. Architecture et circulation des requêtes

```text
Navigateur
  └── Interface Angular (frontend/)
        └── /api/* via le proxy Angular
              └── API FastAPI (backend/app/main.py)
                    ├── RDFLib : chargement, lecture et écriture du graphe
                    ├── Ontologie RDF + données Turtle
                    └── Service SPARQL et catalogue de requêtes
```

### Interface

L’interface est une application Angular autonome organisée autour d’un shell de navigation et de pages dédiées. Le service partagé `ApiService` regroupe les appels HTTP aux routes `/api`. En développement, le proxy Angular redirige ces routes vers l’API locale sur le port 8002; ainsi, l’interface n’a pas à coder le port de l’API dans chaque composant.

### API et graphe

FastAPI expose les données et les opérations utilisées par l’interface. RDFLib lit les fichiers RDF/Turtle, exécute les requêtes SPARQL et sérialise le graphe modifié. Les individus de la grille sont distingués des ressources de schéma afin que les statistiques, l’explorateur et le graphe ne comptent pas les classes et propriétés comme des équipements.

Le backend possède également une interface graphique technique Swagger UI, disponible sur `/docs` de l’API. Elle liste les routes, décrit leurs entrées et permet de les tester. L’application Angular reste l’interface principale destinée à l’utilisateur; Swagger sert à l’inspection et aux démonstrations techniques de l’API.

Les routes principales sont :

| Route | Rôle |
|---|---|
| `GET /api/health` | Vérifier que l’API et les fichiers de données sont accessibles |
| `GET /api/stats` | Calculer les indicateurs de la page d’accueil |
| `GET /api/classes` | Lister les classes et leurs individus |
| `GET /api/individuals` | Lister les individus et leurs propriétés |
| `GET /api/classes/{nom}/individuals` | Filtrer les individus par classe |
| `GET /api/graph` | Préparer les nœuds et relations de la visualisation |
| `POST /api/nlp/ask` | Transformer une question reconnue en résultats SPARQL |
| `POST /api/sparql/query` | Exécuter une requête SPARQL de lecture |
| `POST /api/individuals` | Créer un individu |
| `PUT /api/individuals/{id}` | Mettre à jour les propriétés d’un individu |
| `DELETE /api/individuals/{id}` | Supprimer un individu |
| `POST /api/sparql/update` | Exécuter une mise à jour SPARQL |
| `POST /api/reasoner/run` | Appliquer les règles de classification du démonstrateur |

La documentation interactive de FastAPI est disponible à `/docs` sur le port de l’API, par exemple `http://127.0.0.1:8002/docs`.

## 5. Choix de conception

- **RDF pour le domaine** : les classes et relations explicites permettent de parcourir des connexions entre équipements et d’interroger le modèle avec SPARQL.
- **Turtle pour les données modifiables** : les ajouts de la démo restent dans un fichier distinct de l’ontologie source.
- **API dédiée** : le frontend ne charge pas directement les fichiers RDF et passe par des réponses JSON.
- **Accès direct à la démonstration** : aucun compte ne bloque l’exploration, les écritures CRUD ou la console SPARQL.
- **Composants Angular autonomes** : chaque écran possède son interface et sa logique de page, tandis que le client API est partagé.
- **Fonctions compréhensibles en démonstration** : filtres, recherche, détails d’individu, requête SPARQL et visualisations rendent le graphe inspectable sans client RDF séparé.
- **Limites visibles plutôt que cachées** : la carte est annoncée comme schématique, le graphe est limité pour la lisibilité et le traitement NLP est présenté comme un prototype.

## 6. Démarrer et présenter l’application

Sous Windows, double-cliquer sur `Start Smart Grid.bat` à la racine du projet. Le lanceur vérifie les dépendances, démarre l’API et le serveur Angular, puis ouvre l’adresse locale dans le navigateur. Il cherche un port frontend libre entre 4200 et 4299 si le port habituel est occupé.

Pour une présentation, le parcours conseillé est :

1. montrer les indicateurs de l’accueil;
2. poser la question d’exemple dans « Questionner la grille »;
3. rechercher un individu et ouvrir ses propriétés dans Explorer;
4. montrer les nœuds/liens du graphe et les regroupements de la carte;
5. ouvrir Administration et tester les exemples SELECT, FILTER, recherche, INSERT, UPDATE et DELETE;
6. vérifier le fonctionnement du graphe, du NLP et des opérations CRUD.

Les journaux du lanceur sont écrits dans `%TEMP%\smart-grid-demo`.

Les rôles de présentation et les scénarios détaillés pour cinq membres sont dans [TEAM_GUIDE.md](./TEAM_GUIDE.md) et [SCENARIO.md](./SCENARIO.md). Les noms `Étudiant 1` à `Étudiant 5` sont des placeholders à remplacer par les noms du groupe.
Le détail des étapes et bibliothèques du traducteur NLP se trouve dans [NLP_TOOLS.md](./NLP_TOOLS.md).

## 7. Vérifications

Depuis la racine du projet :

```powershell
python -m pytest backend/tests/test_backend.py -q
Set-Location frontend
npm run build
```

Les tests backend couvrent notamment la disponibilité de l’API, les statistiques, le catalogue SPARQL, les traductions NLP FR/EN, les comparateurs, les filtres exécutés, les questions non reconnues, le contenu du graphe et le cycle CRUD sans authentification.

## 8. Limites et évolutions possibles

- Le traducteur NLP est limité à son lexique et aux types de requêtes décrits dans [NLP_TOOLS.md](./NLP_TOOLS.md); il ne comprend pas des formulations arbitraires.
- La carte déduit une ville depuis l’identifiant et utilise une disposition schématique, faute de coordonnées dans les données.
- La visualisation du graphe n’affiche qu’un sous-ensemble de nœuds et de liens.
- Le raisonneur applique des règles numériques ciblées; ce n’est pas un moteur complet d’inférence OWL.
- L’application n’est pas configurée comme un service de production; elle vise un lancement et une présentation locale.

Ces points donnent des pistes d’évolution : enrichir le corpus et les paraphrases couvertes par le pipeline NLP, ajouter une validation des formes RDF (SHACL) et proposer une distribution de l’application adaptée à un déploiement.
