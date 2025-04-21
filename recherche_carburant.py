# Auteur: eddu22570
# Nom du fichier: recherche_carburant.py
# version: v1.0
# date de création: 21/04/2025


# Importation des modules nécessaires
import requests # Pour effectuer des requêtes HTTP (téléchargement de fichiers, API)
import zipfile # Pour manipuler des fichiers ZIP
import io # Pour gérer des flux de données en mémoire
import xml.etree.ElementTree as ET # Pour parser le fichier XML
import unicodedata # Pour normaliser les chaînes de caractères (gestion des accents)
import time # Pour ajouter des pauses (respect de l'API OSM)

# Fonction de normalisation des chaînes (suppression des accents et passage en majuscules)
def normalize(text):
    if not text:
        return ""
    # Décomposition Unicode pour séparer les accents
    text = unicodedata.normalize('NFD', text)
    # Suppression des caractères de type "marque d'accent"
    text = ''.join([c for c in text if unicodedata.category(c) != 'Mn'])   
    return text.upper()

# Fonction pour récupérer l'enseigne de la station via OpenStreetMap (Overpass API)
def get_osm_brand(lat, lon):
    overpass_url = "https://overpass-api.de/api/interpreter"
    # Requête Overpass pour trouver une station-service dans un rayon de 100m autour des coordonnées
    query = f"""
    [out:json][timeout:10];
    (
      node["amenity"="fuel"](around:100,{lat},{lon});
      way["amenity"="fuel"](around:100,{lat},{lon});
      relation["amenity"="fuel"](around:100,{lat},{lon});
    );
    out center tags 1;
    """
    try:
        # Envoi de la requête à l'API Overpass
        resp = requests.post(overpass_url, data={'data': query}, timeout=20)
        data = resp.json()
        # Parcours des résultats pour trouver le tag 'brand', sinon 'operator', sinon 'name'
        for element in data['elements']:
            tags = element.get('tags', {})
            return tags.get('brand') or tags.get('operator') or tags.get('name')
    except Exception as e:
        return None  # En cas d'erreur (réseau, parsing...), retourne None
    return None

url = "https://donnees.roulez-eco.fr/opendata/instantane" # URL du fichier open data des prix des carburants
communes_recherchees = ["Loudéac", "Pontivy", "Saint-Brieuc"] # liste des communes recherchées
carburants_voulus = {"GPLc", "E10"} # types de carburants recherchés

response = requests.get(url)
with zipfile.ZipFile(io.BytesIO(response.content)) as z:
    # Ouverture du fichier XML à l'intérieur du ZIP
    with z.open(z.namelist()[0]) as xmlfile:
        tree = ET.parse(xmlfile)
        root = tree.getroot()


# Pour chaque commune recherchée
for commune in communes_recherchees:
    # Initialisation d'un dictionnaire pour stocker la station la moins chère par carburant
    moins_cheres = {carb: {'prix': float('inf'), 'station': None, 'maj': None, 'lat': None, 'lon': None} for carb in carburants_voulus}
    # Parcours de toutes les stations du fichier XML
    for station in root.findall('pdv'):
        ville = station.find('ville')
        # Vérification que la station est bien dans la commune recherchée (avec normalisation)
        if ville is not None and normalize(ville.text) == normalize(commune):
            # Récupération de l'adresse et du code postal
            adresse = station.find('adresse').text if station.find('adresse') is not None else ''
            cp = station.attrib.get('cp', '')
            nom_station = f"{adresse}, {cp} {ville.text}"
            # Récupération et conversion des coordonnées (lat/lon en degrés décimaux)
            lat = station.attrib.get('lat')
            lon = station.attrib.get('lon')
            if lat and lon:
                try:
                    lat = float(lat) / 100000
                    lon = float(lon) / 100000
                except:
                    lat = lon = None
            else:
                lat = lon = None
            # Parcours des prix proposés par la station
            for prix in station.findall('prix'):
                nom_carburant = prix.attrib.get('nom')
                # Si le carburant est recherché
                if nom_carburant in carburants_voulus:
                    valeur = float(prix.attrib.get('valeur'))
                    maj = prix.attrib.get('maj')
                    # Si c'est le prix le plus bas trouvé pour ce carburant, on stocke les infos
                    if valeur < moins_cheres[nom_carburant]['prix']:
                        moins_cheres[nom_carburant] = {
                            'prix': valeur,
                            'station': nom_station,
                            'maj': maj,
                            'lat': lat,
                            'lon': lon
                        }
    # Affichage des résultats pour la commune
    print(f"--- {commune} ---")
    for carb in carburants_voulus:
        info = moins_cheres[carb]
        if info['station'] is not None:
            brand = None
            # Si les coordonnées sont présentes, on tente de récupérer l'enseigne via OSM
            if info['lat'] and info['lon']:
                brand = get_osm_brand(info['lat'], info['lon'])
                time.sleep(1)  # Respect Overpass API usage policy
            print(f"Station la moins chère pour {carb} :")
            print(f"  {info['station']} - {info['prix']} c€/L (maj: {info['maj']})")
            print(f"  Enseigne : {brand if brand else 'Non trouvée'}")
        else:
            print(f"Aucune station avec {carb} trouvée à {commune}")
    print('-' * 40)
