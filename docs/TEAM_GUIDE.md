# Répartition de la démonstration par membre

Remplacez les noms `Étudiant 1` à `Étudiant 5` par les noms réels du groupe avant la remise.

| Membre | Critères de la grille | Partie à présenter | Preuve à montrer |
|---|---|---|---|
| Étudiant 1 | Individus (2 pts) · Valeur ajoutée (2 pts) | Ontologie RDF, propriétés, individu et raisonneur | Montrer une ObjectProperty, une DatatypeProperty, les triplets d’un équipement puis une classification produite par le raisonneur. |
| Étudiant 2 | Requêtes SPARQL (4 pts) | Console SPARQL et CRUD | Exécuter SELECT, FILTER, recherche, CREATE, UPDATE et DELETE; vérifier chaque changement par une lecture. |
| Étudiant 3 | API IA (4 pts) | API NLP, NLTK et traduction en SPARQL | Appeler `POST /api/nlp/ask`, montrer outils NLTK, analyse, requête générée et résultats; préciser qu’aucune API LLM tierce n’est appelée. |
| Étudiant 4 | Interfaces graphiques (3 pts) | Accueil, Explorer, Graphe et Carte | Montrer un parcours interactif, la recherche/filtrage et les visualisations avec leur limite schématique. |
| Étudiant 5 | Communication BE/FE (3 pts) · Scénario (2 pts) | Angular, FastAPI, Swagger et persistance RDF | Relier un appel `/api` à sa réponse et à l’écran; conclure le scénario utilisateur complet et expliquer la persistance. |

## Préparation

- Lancer `Start Smart Grid.bat` et laisser l’accueil ouvert.
- Aucune connexion n’est nécessaire. L’administration, les opérations CRUD/SPARQL et le raisonneur sont directement accessibles pour cette application pédagogique.
- Pour le cycle SPARQL, choisir un identifiant inédit, le remplacer dans toutes les requêtes d’exemple et supprimer l’individu temporaire après la présentation.
- Si vous présentez aussi le CRUD en langage naturel, utiliser un identifiant temporaire distinct; vérifier l’aperçu puis confirmer les mutations sur la page Questionner.

Le déroulé détaillé, les paroles suggérées et les requêtes de démonstration sont dans [SCENARIO.md](./SCENARIO.md).

## Questions probables

### Pourquoi RDF et SPARQL ?

RDF représente les individus par des triplets sujet–prédicat–objet. SPARQL sélectionne des ressources selon leurs types, propriétés, relations et valeurs.

### Comment la question devient-elle une requête ?

Le pipeline local utilise NLTK (`TweetTokenizer` et `SnowballStemmer`), des lexiques métier français/anglais, l’extraction des caractéristiques et des gabarits SPARQL contrôlés, puis RDFLib exécute la requête. Aucune API de LLM n’est utilisée.

### La carte donne-t-elle une position GPS ?

La carte utilise une silhouette simplifiée de la Tunisie et place approximativement les villes. Les données ne contiennent pas les coordonnées GPS de chaque équipement : la ville est déduite de l’identifiant, ce n’est pas une localisation de précision.

### Comment les changements sont-ils sauvegardés ?

Les modifications CRUD et SPARQL sont enregistrées dans `backend/data/working_graph.ttl`.
