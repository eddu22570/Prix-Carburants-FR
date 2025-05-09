# Prix-Carburants-FR-V2

# Recherche des stations-service les moins chères par carburant et commune

[![Licence MIT](https://img.shields.io/badge/Licence-MIT-green.svg)](LICENSE)

Ce script Python permet d'identifier, pour une ou plusieurs communes françaises, la station-service proposant le prix le plus bas pour certains carburants (ex : GPLc, E10) à partir des données open data officielles du gouvernement français (https://www.prix-carburants.gouv.fr/).  
Il enrichit également les résultats avec l’enseigne de la station via OpenStreetMap lorsque cette information est disponible.

---

## Fonctionnalités

Téléchargement automatique des données officielles (mise à jour toutes les 10 minutes) depuis le site gouvernemental.

Recherche multi-critères :
  - Par ville (avec suggestions automatiques), code postal ou département.
  - Sélection multiple de carburants (SP95, E10, GPLc, Gazole, SP98, E85).
  - Option pour n’afficher que les stations actuellement ouvertes.

Affichage des résultats :
  - Top 10 des stations les moins chères par carburant et zone.
  - Adresse, prix, date de mise à jour, horaires, et statut d’ouverture.
  - Moyenne des prix et écart par rapport à la moyenne.
  - Signalement des stations en rupture de carburant.

Interface conviviale :
  - Suggestions automatiques de communes (API gouvernementale).
  - Sélection/ajout/retrait de villes, boutons pour tout cocher/décocher.
  - Tableau de résultats interactif.

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

1. **Cloner le dépôt** ou copier le script dans un fichier, par exemple `recherche_carburantv2.py`.

2. **Modifier les paramètres** dans le script selon vos besoins :    
### Types de carburants reconnus par le script
- **Gazole**
- **SP95**
- **SP98**
- **E10** (SP95-E10)
- **E85** (Superéthanol)
- **GPLc** (GPL carburant)

3. **Exécuter le script** :

python recherche_carburantv2.py

---

## Exemple de sortie

![image](https://github.com/user-attachments/assets/29559c7d-758c-45c4-8845-26c38c39c9eb)

![image](https://github.com/user-attachments/assets/6eedd98b-c839-4c85-85e0-c60c2435f939)

---

## Fonctionnement détaillé

- Téléchargement et extraction du fichier XML des prix des carburants depuis le site officiel
- Filtrage des stations par commune, code postal ou département (gestion des accents et de la casse).
- Identification des stations les moins chères pour chaque carburant spécifié.
- Affichage enrichi : adresse, prix, date de mise à jour, horaires, statut d’ouverture, ruptures de stock.
- Calculs statistiques : moyenne des prix, écart par rapport à la moyenne, classement des stations.

---

## Limitations

- Le nom de l’enseigne de la station n’est pas fourni dans les données officielles
- Les prix sont exprimés en euros par litre.
- En cas d’égalité des prix, toutes les stations correspondantes sont affichées.
- Les données sont dépendantes de la qualité et de la fréquence de mise à jour du flux gouvernemental.

---

## Contribution

Les contributions sont les bienvenues !  
N’hésitez pas à ouvrir une issue ou une pull request pour proposer des améliorations ou signaler des problèmes.

---

## Licence

Ce projet est sous licence MIT.  
Les données carburants sont sous licence ouverte Etalab.

---

*Script développé pour faciliter l’accès aux données carburants officielles et permettre à chacun d’optimiser ses dépenses de carburant grâce à une interface simple et puissante.*
