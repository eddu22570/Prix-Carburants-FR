# Prix-Carburants-FR

# Recherche des stations-service les moins chères par carburant et commune

Ce script Python permet d'identifier, pour une ou plusieurs communes françaises, la station-service proposant le prix le plus bas pour certains carburants (ex : GPLc, E10) à partir des données open data officielles du gouvernement français (https://www.prix-carburants.gouv.fr/).  
Il enrichit également les résultats avec l’enseigne de la station via OpenStreetMap lorsque cette information est disponible.

---

## Fonctionnalités

- Téléchargement automatique des données officielles des prix des carburants (prix-carburants.gouv.fr)  
- Recherche de la station la moins chère par carburant et par commune  
- Affichage de l’adresse, du prix, de la date de mise à jour  
- Recherche de l’enseigne via l’API Overpass d’OpenStreetMap  
- Gestion des accents et de la casse dans les noms de communes  

---

## Prérequis

- Python 3.7 ou supérieur  
- Modules Python nécessaires :  
  - `requests`  
  - `unicodedata`  

### Installation des dépendances

pip install requests


---

## Utilisation

1. **Cloner le dépôt** ou copier le script dans un fichier, par exemple `recherche_carburant.py`.

2. **Modifier les paramètres** dans le script selon vos besoins :  
   - `communes_recherchees` : liste des communes à analyser (ex. `["Loudéac", "Pontivy"]`)  
   - `carburants_voulus` : types de carburants à rechercher (ex. `{"GPLc", "E10"}`)
  Types de carburants disponibles dans la base de données prix-carburants.gouv.fr:
   - GPLc
   - Gazole
   - E85
   - E10
   - SP95
   - SP98

3. **Exécuter le script** :

python recherche_carburant.py

---

## Exemple de sortie

![image](https://github.com/user-attachments/assets/aacb23ff-abdd-4c7c-a402-0cf00992c963)

![image](https://github.com/user-attachments/assets/e5c6c866-fa7e-458e-81b7-973f2fb40a36)

---

## Fonctionnement détaillé

- Téléchargement et extraction du fichier XML des prix des carburants depuis le site officiel.  
- Filtrage des stations par commune (avec gestion des accents et casse).  
- Identification de la station la moins chère pour chaque carburant spécifié.  
- Recherche de l’enseigne de la station via une requête à l’API Overpass d’OpenStreetMap, basée sur les coordonnées GPS.  

---

## Limitations

- L’enseigne n’est pas toujours disponible, dépendant de la couverture et de la qualité des données OpenStreetMap.  
- Le script respecte la limite d’une requête par seconde vers l’API Overpass pour éviter le blocage.  
- Les prix sont exprimés en centimes d’euros par litre (c€/L).  
- En cas d’égalité des prix, seul la première station trouvée est retournée.  

---

## Contribution

Les contributions sont les bienvenues !  
N’hésitez pas à ouvrir une issue ou une pull request pour proposer des améliorations ou signaler des problèmes.

---

## Licence

Ce projet est sous licence MIT.  
Les données carburants sont sous licence ouverte Etalab.

---

*Script développé pour faciliter l’accès aux données carburants officielles et enrichir l’information avec des données géographiques libres.*
