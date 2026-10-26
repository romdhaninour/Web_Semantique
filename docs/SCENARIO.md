# Scénarios de présentation — cinq membres

Ce déroulé répartit la démonstration selon les critères visibles sur la grille : **Requêtes SPARQL (4 pts), Individus (2 pts), Scénario (2 pts), API IA (4 pts), Interfaces graphiques (3 pts), Communication BE/FE (3 pts), Valeur ajoutée (2 pts)**. Les noms sont à remplacer par ceux du groupe.

Chaque membre présente une partie différente, avec une action à réaliser dans l’application et une preuve à montrer. Les questions NLP sont saisies au clavier.

## Répartition des critères

| Membre | Critères principalement démontrés | Preuve principale |
|---|---|---|
| Étudiant 1 | Individus (2 pts) · Valeur ajoutée (2 pts) | Individu RDF, propriétés et relations; classification du raisonneur |
| Étudiant 2 | Requêtes SPARQL (4 pts) | SELECT, FILTER, INSERT, UPDATE, DELETE et vérification des résultats |
| Étudiant 3 | API IA (4 pts) | API NLP locale, outils NLTK, SPARQL produit et résultats |
| Étudiant 4 | Interfaces graphiques (3 pts) | Dashboard, Explorer, Graphe et Carte |
| Étudiant 5 | Communication BE/FE (3 pts) · Scénario (2 pts) | Appel Angular → FastAPI → RDF et conclusion du parcours complet |

## Préparation commune

1. Lancer `Start Smart Grid.bat` et attendre l’ouverture de l’application.
2. Vérifier que l’accueil affiche les statistiques et que l’API répond à `http://127.0.0.1:8002/api/health`.
3. Garder Swagger ouvert dans un onglet : `http://127.0.0.1:8002/docs`.
4. Vérifier que `Eolienne_Sfax1` existe dans les données initiales.
5. Pour le CRUD, choisir un identifiant inédit, par exemple `Demo_Groupe_2026`. Utiliser le même identifiant pendant toute la démonstration, puis supprimer l’individu temporaire.
6. Remplacer « Étudiant 1 » à « Étudiant 5 » par les noms du groupe.

Durée suggérée : environ 10 à 15 minutes au total, soit 2 à 3 minutes par personne.

---

## Étudiant 1 — Ontologie, individus et valeur ajoutée

**Critères visés : Individus (2 pts) et Valeur ajoutée (2 pts).**

### Actions à réaliser

1. Ouvrir le fichier `ontology/Web_Semantique_corrige.rdf` et présenter brièvement les classes du réseau.
2. Montrer au moins un exemple d’`ObjectProperty`, par exemple `estConnecteA`, avec son domaine et son range.
3. Montrer une `DatatypeProperty`, par exemple `capaciteProduction`, avec son domaine et son type numérique.
4. Dans **Explorer**, filtrer la classe `Eolienne` et sélectionner `Eolienne_Sfax1`.
5. Relier l’individu à ses types, sa capacité de production et ses relations RDF.
6. Dans **Administration**, lancer le raisonneur et présenter les types qui ont été ajoutés.

### À expliquer

> « L’ontologie définit les classes et les propriétés du domaine. Un individu est décrit par des triplets RDF : sujet, prédicat et objet. Par exemple, `Eolienne_Sfax1` est une éolienne, possède une capacité de production et peut être reliée à une ligne de transport. Le raisonneur du projet ajoute des classifications selon des seuils numériques; c’est une valeur ajoutée démontrable, mais ce n’est pas un moteur OWL général. »

### Preuves pour l’évaluation

- Une ressource du domaine réellement présente dans le graphe.
- Une propriété de données et une relation entre ressources.
- Une classification supplémentaire visible après l’exécution du raisonneur.

---

## Étudiant 2 — Requêtes SPARQL et CRUD

**Critère visé : Requêtes SPARQL (4 pts).**

### Actions à réaliser

Dans **Administration · CRUD & SPARQL**, montrer une lecture, un filtre, une recherche et le cycle CRUD. Les exemples prédéfinis peuvent être utilisés pour SELECT/FILTER/recherche. Pour le CRUD, remplacer `Demo_Etudiant2` par l’identifiant inédit retenu par le groupe.

1. Exécuter un `SELECT` listant les sources d’énergie.
2. Exécuter un `FILTER` sur la capacité supérieure à 500 kW.
3. Exécuter une recherche textuelle par ville ou identifiant, par exemple `sfax`.
4. Dans le mode écriture, créer l’individu temporaire :

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
INSERT DATA {
  sg:Demo_Groupe_2026 a sg:Eolienne ;
    sg:capaciteProduction 650 .
}
```

5. Vérifier sa création et la valeur avec un `SELECT` :

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
SELECT ?property ?value
WHERE { sg:Demo_Groupe_2026 ?property ?value }
```

6. Modifier sa capacité :

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
DELETE { sg:Demo_Groupe_2026 sg:capaciteProduction 650 }
INSERT { sg:Demo_Groupe_2026 sg:capaciteProduction 720 }
WHERE { sg:Demo_Groupe_2026 sg:capaciteProduction 650 }
```

7. Relancer le `SELECT` précédent pour vérifier que la capacité vaut maintenant `720`, puis supprimer toutes les propriétés sortantes de l’individu temporaire :

```sparql
PREFIX sg: <http://www.semanticweb.org/smartgrid-ontology#>
DELETE WHERE { sg:Demo_Groupe_2026 ?property ?value }
```

8. Relancer le `SELECT` précédent : il ne doit plus retourner de ligne pour cet identifiant.

**Important :** si un identifiant différent est choisi, remplacer `Demo_Groupe_2026` dans chacune des requêtes. Ne pas lancer l’UPDATE avant l’INSERT : le `WHERE` doit retrouver la valeur `650`. La séquence DELETE ci-dessus convient parce que cet exemple ne crée aucune relation entrante vers l’individu.

### À expliquer

> « SPARQL permet de sélectionner les ressources, de les filtrer et de modifier les triplets RDF. Après l’écriture, le graphe est sauvegardé dans le fichier de travail Turtle. Nous vérifions chaque opération avec une requête de lecture. »

### Preuves pour l’évaluation

- Résultats de SELECT et de FILTER.
- Recherche par texte.
- Succès de CREATE, UPDATE, DELETE confirmé par les lectures après écriture.

---

## Étudiant 3 — API IA / NLP vers SPARQL

**Critère visé : API IA (4 pts).**

### Actions à réaliser

1. Dans Swagger, ouvrir `POST /api/nlp/ask`.
2. Envoyer cette requête JSON :

```json
{
  "question": "Quelles éoliennes produisent plus de 500 kW ?",
  "confirm": false
}
```

3. Montrer dans la réponse la langue, l’intention, les tokens, les racines, les entités, la métrique et le comparateur.
4. Montrer le SPARQL généré et les lignes effectivement renvoyées par l’API.
5. Refaire le test avec une question anglaise, par exemple : `Which batteries have storage capacity at least 100 kWh?`.
6. Si le temps le permet, essayer une question non prise en charge et expliquer la réponse explicite plutôt que d’afficher des résultats inventés.
7. Localiser le code dans `backend/app/nlp_service.py` et la route dans `backend/app/main.py`.

### À expliquer

> « L’API IA de notre grille est l’API NLP développée dans le projet : `POST /api/nlp/ask`. Elle ne transmet pas la question à OpenAI ou Gemini. NLTK fournit `TweetTokenizer` pour séparer les mots et `SnowballStemmer` pour la racinisation française ou anglaise. Notre code ajoute la détection de langue, les lexiques bilingues, l’extraction des entités et des valeurs, puis construit une requête depuis des gabarits SPARQL. RDFLib exécute ensuite la requête sur notre graphe. »

Préciser que le module est un traducteur à règles et lexiques pour un vocabulaire pris en charge, pas un modèle génératif qui comprend toute formulation.

### Preuves pour l’évaluation

- Appel réel à l’endpoint NLP.
- SPARQL généré et exécuté, avec ses résultats.
- Outils NLP nommés explicitement : NLTK `TweetTokenizer` et `SnowballStemmer`.
- Absence d’appel à une API LLM tierce.

---

## Étudiant 4 — Interfaces graphiques

**Critère visé : Interfaces graphiques (3 pts).**

### Actions à réaliser

1. Présenter l’accueil : statistiques et familles d’équipements du graphe.
2. Ouvrir **Explorer**, filtrer par classe et rechercher `Eolienne_Sfax1`; ouvrir sa fiche.
3. Ouvrir **Graphe**, filtrer ou sélectionner une ressource et montrer ses voisins et relations.
4. Ouvrir **Carte**, sélectionner une ville et montrer les ressources regroupées.
5. Faire remarquer les éléments de navigation et l’adaptation du contenu aux différentes pages.

### À expliquer

> « Les écrans sont conçus autour des tâches de l’application : synthèse du réseau, exploration des ressources, visualisation des relations et regroupement par ville. Les visualisations s’appuient sur les données servies par le backend. La carte est schématique : la ville est déduite de l’identifiant et les positions ne sont pas des coordonnées GPS d’équipements. »

### Preuves pour l’évaluation

- Parcours cohérent entre plusieurs écrans.
- Recherche/filtrage et fiche de ressource réellement interactifs.
- Graphe et carte affichant les données de l’application, avec leurs limites expliquées.

---

## Étudiant 5 — Communication backend/frontend et scénario global

**Critères visés : Communication BE/FE (3 pts) et Scénario (2 pts).**

### Actions à réaliser

1. Présenter le parcours complet : dashboard → question naturelle → SPARQL/résultats → Explorer ou Graphe → vérification après CRUD.
2. Dans l’interface, montrer une donnée chargée (statistiques ou individus).
3. Ouvrir les outils réseau du navigateur ou `frontend/src/app/services/api.service.ts` pour montrer un appel Angular vers `/api`.
4. Dans Swagger, appeler `GET /api/stats` ou `GET /api/individuals` et comparer la réponse JSON à l’écran.
5. Expliquer le chemin de la donnée : Angular → API FastAPI → service RDFLib/SPARQL → graphe RDF → réponse JSON → interface.
6. Montrer les trois sources de données et la persistance : ontologie RDF/XML, seed Turtle et `backend/data/working_graph.ttl`.
7. Terminer en confirmant que la ressource temporaire du scénario SPARQL a été supprimée.

### À expliquer

> « Le frontend Angular n’ouvre pas directement les fichiers RDF : il appelle les routes FastAPI via `/api`. Le backend charge le graphe avec RDFLib, exécute la lecture ou la mise à jour, puis renvoie du JSON. Après une écriture, le graphe de travail Turtle permet de conserver la modification. »

### Preuves pour l’évaluation

- Un appel backend et sa représentation dans le frontend.
- Le parcours utilisateur complet, avec une transition logique entre les parties présentées par les membres.
- Une explication du rôle de l’API, du graphe et de la persistance.

---

## Questions possibles de l’évaluateur

### L’application utilise-t-elle une API d’intelligence artificielle externe ?

Non. L’application expose son propre endpoint NLP dans FastAPI. Il utilise NLTK, des règles, des lexiques français/anglais et des gabarits SPARQL; aucune API Gemini, OpenAI ou autre LLM n’est appelée.

### Le système comprend-il toutes les phrases ?

Non. Le traducteur prend en charge des classes, propriétés, villes et formes de comparaison définies. Une formulation non reconnue doit produire une erreur explicite.

### Le raisonneur est-il un moteur complet OWL ?

Non. Le raisonneur de démonstration applique des règles ciblées, notamment des seuils de production et de consommation, puis ajoute des types dérivés.

### Les marqueurs de la carte sont-ils des positions GPS exactes ?

Non. La carte est schématique et regroupe les ressources à partir d’une ville reconnue dans leur identifiant.

## Nettoyage après présentation

- Vérifier que l’individu temporaire utilisé pour CREATE/UPDATE/DELETE a été supprimé.
- Les écritures confirmées sont sauvegardées dans `backend/data/working_graph.ttl`.
- Pour revenir à la seule ontologie et aux données initiales, arrêter l’application puis supprimer explicitement le graphe de travail. Ne jamais supprimer l’ontologie ni `backend/data/smartgrid_seed.ttl`.
