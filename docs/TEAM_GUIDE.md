# Répartition de la démonstration par membre

Remplacez les noms `Étudiant 1` à `Étudiant 5` par les noms réels du groupe avant la remise.

| Membre | Critères de la grille | Partie à présenter | Preuve à montrer |
|---|---|---|---|
| Étudiant 1 | Individuals · valeur ajoutée / reasoner | Ontologie RDF, individus, Explorer, raisonneur | Ouvrir un individu, présenter ses triplets, lancer le raisonneur et montrer les types inférés. |
| Étudiant 2 | Requêtes SPARQL / CRUD | Console SPARQL, catalogue et API | Exécuter SELECT, FILTER/recherche, puis CREATE/UPDATE/DELETE et vérifier les résultats. |
| Étudiant 3 | NLP/TALN /4 · saisie vocale | `nlp_service.py`, NLTK, page Questionner et API | Montrer tokens/racines, entités/métriques extraites, le SPARQL généré et exécuté; démontrer le CRUD en langage naturel avec aperçu et confirmation. Dicter si le navigateur le permet. |
| Étudiant 4 | Interfaces graphiques /3 · carte | Accueil, Explorer, Graphe et Carte | Présenter le design, filtrer/rechercher dans les individus et visualiser les relations et les regroupements par ville. |
| Étudiant 5 | Communication frontend/backend /3 · scénario /2 | Angular, FastAPI, Swagger et persistance RDF | Montrer les appels `/api`, tester `/docs` et expliquer le fichier Turtle de travail. |

## Préparation

- Lancer `Start Smart Grid.bat` et laisser l’accueil ouvert.
- Aucune connexion n’est nécessaire. L’administration, les opérations CRUD/SPARQL et le raisonneur sont directement accessibles pour cette application pédagogique.
- Pour le cycle SPARQL, utiliser `sg:Demo_Etudiant2` et supprimer l’individu temporaire après la présentation.
- Pour le CRUD en langage naturel, utiliser une ressource de démonstration séparée comme `Demo_Eolienne`; vérifier l’aperçu et confirmer les mutations sur la page Questionner.
- Pour la dictée, utiliser un navigateur compatible avec la Web Speech API et accepter l’accès au microphone; sinon saisir la question au clavier.

## Questions probables

### Pourquoi RDF et SPARQL ?

RDF représente les individus par des triplets sujet–prédicat–objet. SPARQL sélectionne des ressources selon leurs types, propriétés, relations et valeurs.

### Comment la question devient-elle une requête ?

Le pipeline local utilise NLTK (`TweetTokenizer` et `SnowballStemmer`), des lexiques métier français/anglais, l’extraction des caractéristiques et des gabarits SPARQL contrôlés, puis RDFLib exécute la requête. Aucune API de LLM n’est utilisée.

### La carte donne-t-elle une position GPS ?

La carte utilise une silhouette simplifiée de la Tunisie et place approximativement les villes. Les données ne contiennent pas les coordonnées GPS de chaque équipement : la ville est déduite de l’identifiant, ce n’est pas une localisation de précision.

### Comment les changements sont-ils sauvegardés ?

Les modifications CRUD et SPARQL sont enregistrées dans `backend/data/working_graph.ttl`.
