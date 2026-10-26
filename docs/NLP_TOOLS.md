# Module NLP/TALN — traduction vers SPARQL

## Objectif

Convertir une question en français ou en anglais en une requête SPARQL exécutable sur le graphe RDF de l’application. Le module ne contacte aucun service de LLM et ne nécessite aucun modèle ou corpus à télécharger.

## Pipeline implémenté

1. **Tokenisation** — `nltk.tokenize.TweetTokenizer` sépare la question en mots/valeurs et ignore les signes de ponctuation non utiles.
2. **Normalisation** — normalisation Unicode, casse et accents pour rapprocher les variantes d’écriture.
3. **Détection de langue** — score de marqueurs français/anglais.
4. **Racinisation** — `nltk.stem.snowball.SnowballStemmer` (`french` ou `english`) pour faire correspondre les formes fléchies et les variantes d’expressions.
5. **Extraction des caractéristiques** — dictionnaires bilingues associent les expressions métier aux classes et propriétés autorisées; des règles extraient la ville, le nombre et le comparateur.
6. **Construction de SPARQL** — génération depuis des gabarits bornés, pas depuis du texte SPARQL fourni par l’utilisateur.
7. **Exécution et résultat** — `SparqlService`/RDFLib exécute la requête sur le graphe actuel. L’API renvoie la requête, les tokens, racines, entités, critères, le nombre de lignes et les résultats.
8. **CRUD guidé** — les verbes reconnus (créer, modifier, supprimer) sélectionnent des gabarits SPARQL Update bornés. L’identifiant et les propriétés sont contrôlés avant toute exécution. La première requête ne modifie rien : l’interface affiche le SPARQL et demande une confirmation explicite; une suppression exige aussi une confirmation navigateur. La lecture d’un identifiant précis produit un `SELECT`.

Le score de confiance présenté est un indicateur heuristique associé à la règle reconnue; il ne provient pas d’un modèle entraîné et ne représente pas une probabilité calibrée.

## Capacités couvertes

- Listes d’individus par classe : éoliennes, panneaux solaires, batteries, stations de pompage, bâtiments, lignes, compteurs, onduleurs et gestionnaires.
- Recherche de ressources par ville présente dans le jeu tunisien.
- Filtres numériques sur la capacité de production, la capacité de stockage et la consommation annuelle.
- Comparateurs `>`, `>=`, `<`, `<=` et `=`, exprimés en mots français/anglais ou par symbole.
- Classement décroissant selon une métrique comprise.
- Lecture d’une ressource par identifiant, création par classe et identifiant, modification des propriétés numériques autorisées, et suppression d’une ressource (y compris les liens entrants), avec prévisualisation et confirmation.
- Réponse HTTP `422` explicite lorsque la question est vide ou hors du lexique/capacités, sans inventer de résultats.

Exemples vérifiés par tests :

- « Quelles éoliennes produisent plus de 500 kW ? »
- « Which batteries have storage capacity at least 100 kWh? »
- « Quelles éoliennes à Sfax ? »
- « Éoliennes avec production >= 500 kW »
- « Crée une éolienne nommée Demo_Eolienne avec une capacité de production de 650 kW »
- « Modifie la capacité de production de Demo_Eolienne à 720 kW »
- « Supprime la ressource Demo_Eolienne »
- « Lis la ressource Demo_Eolienne »

La grammaire CRUD est volontairement limitée : création de ressources d’une classe reconnue, modification des propriétés numériques exposées par le lexique, et suppression/lecture par identifiant. Les mises à jour sont re-traduites et revalidées côté serveur au moment de la confirmation; aucun SPARQL arbitraire issu du texte utilisateur n’est exécuté par ce flux.

## Dépendance

La dépendance serveur est déclarée dans `backend/requirements.txt` : `nltk>=3.9.1`. Les outils utilisés (`TweetTokenizer` et `SnowballStemmer`) fonctionnent sans télécharger de modèles/corpus NLTK.

## Limites honnêtes

Le vocabulaire métier et les structures de question sont définis par des lexiques/règles; les paraphrases arbitraires, les raisonnements complexes et le dialogue général ne sont pas compris. Les tests fonctionnels démontrent les exemples pris en charge, ils ne constituent pas une mesure de précision statistique sur un corpus indépendant.
