# Scénario de démonstration du groupe

Pour un catalogue plus complet de questions NLP, de parcours UI et d’étapes CRUD reproductibles, voir [DEMO_SCENARIOS.md](./DEMO_SCENARIOS.md).

## Objectif

Montrer un parcours sans compte : explorer l’ontologie et les données, interroger le graphe en SPARQL, traduire une question en langage naturel, puis vérifier que les écritures sont persistées.

## Préparation

1. Lancer `Start Smart Grid.bat`.
2. Vérifier les statistiques de l’accueil.
3. Ouvrir « Administration · CRUD & SPARQL »; aucune connexion n’est nécessaire.
4. Utiliser `sg:Demo_Etudiant2` pour les exemples CRUD, puis le supprimer à la fin.

## Déroulé — une personne par partie

### Étudiant 1 — Ontologie et individus

1. Ouvrir Explorer, filtrer par `Eolienne` et sélectionner un individu.
2. Montrer les types et propriétés RDF.
3. Dans Administration, lancer le raisonneur et présenter les classifications calculées.

**À dire :** « L’ontologie décrit les classes/propriétés; les équipements sont des individus RDF. Le raisonneur ajoute les types dérivés par les règles de seuil. »

### Étudiant 2 — SPARQL et CRUD

1. Exécuter le SELECT des sources.
2. Filtrer sur la capacité supérieure à 500 kW et rechercher un identifiant.
3. Charger CREATE pour créer `Demo_Etudiant2`.
4. Charger UPDATE pour changer sa capacité et vérifier avec SELECT.
5. Exécuter DELETE et vérifier que l’individu temporaire a disparu.

**À dire :** « La même console permet lecture, filtrage, recherche et écriture SPARQL. Les modifications sont sauvegardées dans le graphe de travail Turtle. »

### Étudiant 3 — NLP/TALN vers SPARQL

1. Ouvrir Questionner la grille et saisir « Quelles éoliennes produisent plus de 500 kW ? ».
2. Montrer les tokens/racines NLTK, l’entité extraite, la métrique et le comparateur.
3. Ouvrir « Voir la requête SPARQL générée et exécutée ».
4. Vérifier que les lignes affichées satisfont le filtre; essayer aussi « Which batteries have storage capacity at least 100 kWh? ».
5. Essayer la lecture de `Demo_Etudiant2`, puis préparer la création en langage naturel de `Demo_Eolienne`; vérifier le SPARQL et confirmer explicitement.
6. Modifier la capacité de `Demo_Eolienne`, vérifier l’aperçu avant confirmation, puis demander sa suppression et utiliser les deux confirmations; recréer/supprimer l’exemple au besoin.

**À dire :** « Le pipeline utilise NLTK TweetTokenizer et SnowballStemmer, un lexique bilingue métier, des extracteurs de caractéristiques et des gabarits SPARQL contrôlés. RDFLib exécute les requêtes de lecture et les mises à jour. Pour le CRUD, le SPARQL est prévisualisé et une confirmation est obligatoire; aucune API de LLM n’est appelée. »

### Étudiant 4 — Interfaces, graphe et carte

1. Présenter le dashboard et ses statistiques RDF.
2. Rechercher un individu, filtrer une classe et afficher sa fiche.
3. Montrer les nœuds/liens du graphe.
4. Choisir une ville sur la carte et expliquer son caractère schématique.

### Étudiant 5 — Intégration frontend/backend

1. Montrer que l’interface Angular consomme les routes `/api`.
2. Ouvrir `/docs`, par exemple `http://127.0.0.1:8002/docs`, puis exécuter `GET /api/health` ou `GET /api/stats`.
3. Montrer le graphe, les pages de données et la persistance RDF.
4. Expliquer les fichiers source RDF, seed Turtle et working Turtle.

## Questions à anticiper

- **Faut-il un compte ?** Non. Les pages et opérations sont ouvertes dans cette démonstration pédagogique.
- **L’IA comprend-elle toutes les phrases ?** Non. Le traducteur gère les classes, villes, métriques et comparateurs documentés; une question inconnue reçoit une erreur explicite.
- **La voix est-elle toujours disponible ?** Elle dépend du navigateur et de la permission microphone. La saisie texte reste disponible.
- **La carte donne-t-elle une position GPS ?** Non, les regroupements par ville sont schématiques.

## Nettoyage après la démonstration

Vérifier que `sg:Demo_Etudiant2` a été supprimé. Le fichier de travail Turtle conserve les changements démonstratifs voulus dans `backend/data/working_graph.ttl`.
