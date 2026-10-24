# Scénarios et questions pour la démonstration

Ce guide propose un parcours reproductible pour montrer le fonctionnement de Smart Grid Sémantique. Les questions NLP ci-dessous ont été essayées avec le traducteur actuel. Le nombre de résultats peut changer après des opérations CRUD.

## Démarrage

1. À la racine du projet, lancer `Start Smart Grid.bat`.
2. Ouvrir l’application sur `http://127.0.0.1:4203`.
3. Vérifier que l’API répond sur `http://127.0.0.1:8002/api/health` et que Swagger est disponible sur `http://127.0.0.1:8002/docs`.
4. Préparer un identifiant temporaire inédit pour le scénario CRUD, par exemple `Demo_Prof_2026`. Ne pas réutiliser un identifiant déjà présent.
5. Pour les modifications de données, utiliser cette ressource temporaire puis la supprimer à la fin.

## Parcours express — 10 minutes

### 1. Présenter le graphe RDF

- Sur l’accueil, montrer les statistiques du graphe.
- Dans **Explorer**, filtrer par `Eolienne`, puis ouvrir `Eolienne_Sfax1`.
- Montrer ses types, ses propriétés et ses relations.
- Expliquer qu’un individu RDF est décrit par des triplets sujet–prédicat–objet.

### 2. Interroger en langage naturel

Ouvrir **Questionner la grille**, saisir une question ci-dessous, puis montrer les tokens, les racines, l’intention, les entités extraites, le SPARQL généré et les résultats.

| Question à saisir | Ce qu’elle démontre |
|---|---|
| `Liste les éoliennes` | Reconnaissance d’une classe et génération d’un SELECT |
| `Liste les panneaux solaires` | Une autre classe de l’ontologie |
| `Quels bâtiments industriels ?` | Classement d’individus par classe |
| `Liste les bâtiments tertiaires` | Reconnaissance d’une autre famille de bâtiments |
| `Quelles éoliennes à Sfax ?` | Recherche par ville |
| `Quels panneaux solaires à Sousse ?` | Combinaison classe + ville |
| `Quelles sources à Gabès ?` | Recherche d’une autre ville |
| `Quelles éoliennes produisent plus de 500 kW ?` | Extraction de métrique, comparateur `>` et valeur |
| `Quelles éoliennes avec production >= 500 kW ?` | Comparateur inclusif `>=` |
| `Quelles éoliennes avec production = 600 kW ?` | Comparateur d’égalité |
| `Quelles sources produisent moins de 600 kW ?` | Comparateur `<` |
| `Quelles batteries avec capacite stockage supérieure à 1000 kWh ?` | Capacité de stockage et filtre numérique |
| `Which batteries have storage capacity at least 100 kWh?` | Même pipeline avec une question en anglais |
| `Quelles sources ont une consommation annuelle supérieure à 10000 kWh ?` | Filtrage de la consommation annuelle |
| `Quelles éoliennes ont la plus grande production ?` | Classement par métrique |
| `Lis la ressource Eolienne_Sfax1` | Lecture par identifiant exact |

Ouvrir le panneau SPARQL pour montrer que la question n’est pas simplement affichée : le backend a construit et exécuté une requête sur le graphe.

### 3. Explorer la carte et le graphe

- Dans **Carte**, sélectionner Sfax ou Gabès et présenter les ressources reconnues pour la ville.
- Préciser que la carte utilise des positions approximatives de villes, pas des coordonnées GPS d’équipements.
- Dans **Graphe**, filtrer par `Eolienne`. Les nœuds reliés restent visibles avec les flèches.
- Cliquer sur un nœud pour mettre en évidence ses relations et consulter ses propriétés; survoler une flèche pour lire le nom de la relation.

### 4. Montrer les requêtes SPARQL

Dans **Administration · CRUD & SPARQL**, choisir un exemple de lecture :

- **Recherche — toutes les sources** : montre un `SELECT`.
- **Filtrage — capacité > 500 kW** : montre `FILTER` et le tri des valeurs.
- **Recherche — identifiant contient « sfax »** : montre une recherche textuelle avec `CONTAINS`.

Montrer ensuite que les exemples d’écriture sont des opérations SPARQL Update et qu’elles modifient les données persistées.

## Scénario CRUD en langage naturel — démonstration complète

Utiliser un identifiant temporaire qui n’existe pas encore, par exemple `Demo_Prof_2026`. Effectuer ces étapes dans **Questionner la grille** :

1. Saisir `Crée une éolienne nommée Demo_Prof_2026 avec une capacité de production de 650 kW`.
2. Montrer la requête `INSERT DATA` générée. À cette étape, rien n’est encore écrit dans le graphe.
3. Cliquer **Confirmer création** et montrer la ressource créée et ses propriétés.
4. Saisir `Lis la ressource Demo_Prof_2026` pour vérifier son contenu.
5. Saisir `Modifie la capacité de production de Demo_Prof_2026 à 720 kW`. Montrer le SPARQL `DELETE` + `INSERT` + `WHERE` avant de confirmer.
6. Confirmer la modification, puis relire la ressource pour vérifier la nouvelle valeur.
7. Saisir `Supprime la ressource Demo_Prof_2026`. Montrer le SPARQL de suppression.
8. Confirmer dans l’application puis dans la boîte de dialogue de suppression.
9. Rechercher de nouveau l’identifiant dans **Explorer** ou **Graphe** : il doit avoir disparu.

La page Administration permet aussi de montrer le CRUD avec formulaires, en plus du CRUD demandé en langage naturel. Les écritures sont conservées dans `backend/data/working_graph.ttl`.

## Scénario pour cinq personnes

| Personne | Partie | Démonstration conseillée |
|---|---|---|
| 1 | Modèle RDF | Explorer `Eolienne_Sfax1`, ses classes, ses propriétés et ses relations |
| 2 | SPARQL | Exécuter les exemples SELECT, filtre numérique et recherche `sfax`; présenter CREATE/UPDATE/DELETE |
| 3 | NLP/TALN | Poser une question en français puis en anglais; montrer analyse NLTK, SPARQL généré et résultats |
| 4 | Interfaces et visualisations | Présenter accueil, Explorer, Graphe (filtre + voisins) et Carte de Tunisie |
| 5 | CRUD et intégration | Réaliser le cycle CRUD NLP, vérifier la persistance, présenter `/docs` et `/api/health` |

## Questions de secours

Si une question ne correspond pas à la grammaire du traducteur, utiliser une formulation de la liste ci-dessus. Le module est un traducteur à lexiques et règles, pas un assistant conversationnel général. Une formulation inconnue doit produire un message d’erreur explicite plutôt qu’un résultat inventé.

Exemple de test négatif à montrer si le professeur demande les limites : `Quel temps fera-t-il demain ?`. Expliquer que cette question ne concerne pas le vocabulaire Smart Grid et qu’elle est rejetée sans créer de requête métier.

## Nettoyage et état initial

- Toujours terminer le scénario CRUD en supprimant l’individu temporaire.
- Les modifications confirmées sont enregistrées dans `backend/data/working_graph.ttl`; supprimer cette surcharge uniquement si vous voulez revenir aux fichiers de départ et qu’aucune donnée de démonstration ne doit être conservée.
- Ne pas supprimer les fichiers sources de l’ontologie ni `backend/data/smartgrid_seed.ttl`.

## Explication courte du module NLP

« Le backend utilise NLTK `TweetTokenizer` et `SnowballStemmer`, des lexiques français/anglais et des règles d’extraction. Il produit du SPARQL depuis des gabarits contrôlés, puis RDFLib exécute la requête. Pour CREATE, UPDATE et DELETE, l’interface affiche d’abord la requête et attend une confirmation. Aucune API de LLM n’est utilisée. »
