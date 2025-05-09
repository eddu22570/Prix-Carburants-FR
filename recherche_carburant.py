# Auteur: eddu22570
# Nom du fichier: recherche_carburant.py
# version: v2.0
# date de création: 21/04/2025

# Importation des modules nécessaires
import requests # Pour effectuer des requêtes HTTP (téléchargement de fichiers, API)
import zipfile # Pour manipuler des fichiers ZIP
import io # Pour gérer des flux de données en mémoire
import xml.etree.ElementTree as ET # Pour parser le fichier XML
import unicodedata # Pour normaliser les chaînes de caractères (gestion des accents)
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from statistics import mean
from datetime import datetime

import requests
import zipfile
import io
import xml.etree.ElementTree as ET
import unicodedata
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from statistics import mean
from datetime import datetime

def normalize(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return text.upper()

selected_villes = []

def add_ville():
    ville = entry_ville.get().strip()
    if ville and ville not in selected_villes:
        selected_villes.append(ville)
        update_villes_listbox()
    entry_ville.delete(0, tk.END)
    listbox_suggestions.place_forget()

def remove_ville():
    selection = villes_listbox.curselection()
    if selection:
        ville = villes_listbox.get(selection[0])
        selected_villes.remove(ville)
        update_villes_listbox()

def update_villes_listbox():
    villes_listbox.delete(0, tk.END)
    for v in selected_villes:
        villes_listbox.insert(tk.END, v)

def get_commune_suggestions(event):
    query = entry_ville.get()
    if len(query) < 2:
        listbox_suggestions.place_forget()
        return
    url = f"https://geo.api.gouv.fr/communes?nom={query}&boost=population&limit=10"
    try:
        resp = requests.get(url, timeout=3)
        communes = resp.json()
        listbox_suggestions.delete(0, tk.END)
        for c in communes:
            listbox_suggestions.insert(tk.END, c['nom'])
        if communes:
            x = entry_ville.winfo_rootx() - root_win.winfo_rootx()
            y = entry_ville.winfo_rooty() - root_win.winfo_rooty() + entry_ville.winfo_height()
            listbox_suggestions.place(x=x, y=y)
        else:
            listbox_suggestions.place_forget()
    except Exception:
        listbox_suggestions.place_forget()

def select_commune(event):
    selection = listbox_suggestions.curselection()
    if selection:
        entry_ville.delete(0, tk.END)
        entry_ville.insert(0, listbox_suggestions.get(selection[0]))
        listbox_suggestions.place_forget()

def tout_cocher():
    for var in carburant_vars.values():
        var.set(True)

def tout_decocher():
    for var in carburant_vars.values():
        var.set(False)

def station_ouverte(station):
    """Retourne True si la station est ouverte maintenant selon ses horaires, False sinon (ou si inconnu)."""
    horaire = station.find('horaire')
    if horaire is None:
        return True  # Si pas d'info, on considère ouverte
    now = datetime.now()
    jour_semaine = ['lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche'][now.weekday()]
    for periode in horaire.findall('jour'):
        if periode.attrib.get('nom', '').lower() == jour_semaine:
            for tranche in periode.findall('horaire'):
                debut = tranche.attrib.get('ouverture')
                fin = tranche.attrib.get('fermeture')
                if debut and fin:
                    try:
                        h_deb, m_deb = map(int, debut.split(':'))
                        h_fin, m_fin = map(int, fin.split(':'))
                        t_deb = now.replace(hour=h_deb, minute=m_deb, second=0, microsecond=0)
                        t_fin = now.replace(hour=h_fin, minute=m_fin, second=0, microsecond=0)
                        if t_deb <= now <= t_fin:
                            return True
                    except Exception:
                        continue
    return False

def chercher():
    thread = threading.Thread(target=do_search)
    thread.start()

def clear_treeview(tree):
    for item in tree.get_children():
        tree.delete(item)

def do_search():
    carburants_voulus = {carb for carb, var in carburant_vars.items() if var.get()}
    dept_critere = entry_dept.get().strip()
    villes = [normalize(v) for v in selected_villes]
    cp_critere = entry_cp.get().strip()

    if not villes and not cp_critere and not dept_critere:
        messagebox.showerror("Erreur", "Veuillez saisir au moins une ville, un code postal ou un département.")
        return
    if not carburants_voulus:
        messagebox.showerror("Erreur", "Veuillez sélectionner au moins un carburant.")
        return

    btn_chercher.config(state=tk.DISABLED)
    lbl_attente.config(text="Recherche en cours, merci de patienter...")
    clear_treeview(treeview)
    label_tableau.config(text="")
    ruptures_frame.pack_forget()
    for widget in ruptures_frame.winfo_children():
        widget.destroy()

    try:
        url = "https://donnees.roulez-eco.fr/opendata/instantane"
        response = requests.get(url)
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            with z.open(z.namelist()[0]) as xmlfile:
                tree = ET.parse(xmlfile)
                root = tree.getroot()
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du téléchargement ou du traitement des données : {e}")
        btn_chercher.config(state=tk.NORMAL)
        lbl_attente.config(text="")
        return

    ruptures_dict = {}  # zone -> carburant -> liste ruptures
    table_rows = []

    # --- Département ---
    if dept_critere:
        label_tableau.config(text=f"Département {dept_critere} : Top 10 stations les moins chères (par carburant)")
        for carb in carburants_voulus:
            stations = []
            ruptures = []
            prix_liste = []
            for station in root.findall('pdv'):
                if var_ouvertes.get() and not station_ouverte(station):
                    continue
                cp_station = station.attrib.get('cp', '')
                ville_xml = station.find('ville')
                adresse = station.find('adresse').text if station.find('adresse') is not None else ''
                nom_station = f"{adresse}, {cp_station} {ville_xml.text if ville_xml is not None else ''}"
                if cp_station.startswith(dept_critere):
                    for prix in station.findall('prix'):
                        nom_carburant = prix.attrib.get('nom')
                        rupture = prix.attrib.get('rupture', 'false').lower() == 'true'
                        maj = prix.attrib.get('maj')
                        if nom_carburant and nom_carburant.upper() == carb:
                            if rupture:
                                ruptures.append({
                                    'station': nom_station,
                                    'maj': maj
                                })
                            elif 'valeur' in prix.attrib:
                                valeur = float(prix.attrib.get('valeur'))
                                stations.append({
                                    'prix': valeur,
                                    'station': nom_station,
                                    'maj': maj
                                })
                                prix_liste.append(valeur)
            if prix_liste:
                prix_moyen = mean(prix_liste)
            else:
                prix_moyen = None

            if prix_moyen is not None and stations:
                stations.sort(key=lambda x: x['prix'])
                for i, info in enumerate(stations[:10], 1):
                    ecart = info['prix'] - prix_moyen
                    signe = "+" if ecart > 0 else ""
                    if ecart < -0.01:
                        tag = 'avantageux'
                    elif ecart > 0.01:
                        tag = 'desavantageux'
                    else:
                        tag = 'neutre'
                    table_rows.append((
                        "Département " + dept_critere,
                        carb,
                        i,
                        info['station'],
                        str(info['prix']),
                        str(info['maj']),
                        f"{signe}{round(ecart, 3)}" if prix_moyen is not None else "",
                        str(prix_moyen),
                        tag
                    ))
            else:
                table_rows.append((
                    "Département " + dept_critere,
                    carb,
                    "",
                    "Aucune donnée disponible",
                    "",
                    "",
                    "",
                    "",
                    'neutre'
                ))
            if ruptures:
                ruptures_dict.setdefault("Département " + dept_critere, {}).setdefault(carb, []).extend(ruptures)

    # --- Communes ---
    for commune in villes:
        stations = []
        ruptures = []
        prix_liste = []
        for station in root.findall('pdv'):
            if var_ouvertes.get() and not station_ouverte(station):
                continue
            ville_xml = station.find('ville')
            cp_station = station.attrib.get('cp', '')
            adresse = station.find('adresse').text if station.find('adresse') is not None else ''
            nom_station = f"{adresse}, {cp_station} {ville_xml.text if ville_xml is not None else ''}"
            if ville_xml is not None and normalize(ville_xml.text) == commune:
                for prix in station.findall('prix'):
                    nom_carburant = prix.attrib.get('nom')
                    rupture = prix.attrib.get('rupture', 'false').lower() == 'true'
                    maj = prix.attrib.get('maj')
                    if nom_carburant and nom_carburant.upper() in carburants_voulus:
                        if rupture:
                            ruptures.append({'carb': nom_carburant.upper(), 'station': nom_station, 'maj': maj})
                        elif 'valeur' in prix.attrib and nom_carburant.upper() in carburants_voulus:
                            valeur = float(prix.attrib.get('valeur'))
                            stations.append({
                                'carb': nom_carburant.upper(),
                                'prix': valeur,
                                'station': nom_station,
                                'maj': maj
                            })
                            prix_liste.append(valeur)
        if prix_liste:
            prix_moyen = mean(prix_liste)
        else:
            prix_moyen = None
        for carb in carburants_voulus:
            filtered = [s for s in stations if s['carb'] == carb]
            if filtered:
                filtered.sort(key=lambda x: x['prix'])
                info = filtered[0]
                ecart = info['prix'] - prix_moyen if prix_moyen is not None else 0
                signe = "+" if ecart > 0 else ""
                if ecart < -0.01:
                    tag = 'avantageux'
                elif ecart > 0.01:
                    tag = 'desavantageux'
                else:
                    tag = 'neutre'
                table_rows.append((
                    commune.title(),
                    carb,
                    1,
                    info['station'],
                    str(info['prix']),
                    str(info['maj']),
                    f"{signe}{round(ecart, 3)}" if prix_moyen is not None else "",
                    str(prix_moyen) if prix_moyen is not None else "",
                    tag
                ))
            else:
                table_rows.append((
                    commune.title(),
                    carb,
                    "",
                    "Aucune donnée disponible",
                    "",
                    "",
                    "",
                    "",
                    'neutre'
                ))
        for r in ruptures:
            ruptures_dict.setdefault(commune.title(), {}).setdefault(r['carb'], []).append({'station': r['station'], 'maj': r['maj']})

    # --- Code postal ---
    if cp_critere:
        stations = []
        ruptures = []
        prix_liste = []
        for station in root.findall('pdv'):
            if var_ouvertes.get() and not station_ouverte(station):
                continue
            cp_station = station.attrib.get('cp', '')
            ville_xml = station.find('ville')
            adresse = station.find('adresse').text if station.find('adresse') is not None else ''
            nom_station = f"{adresse}, {cp_station} {ville_xml.text if ville_xml is not None else ''}"
            if cp_station == cp_critere:
                for prix in station.findall('prix'):
                    nom_carburant = prix.attrib.get('nom')
                    rupture = prix.attrib.get('rupture', 'false').lower() == 'true'
                    maj = prix.attrib.get('maj')
                    if nom_carburant and nom_carburant.upper() in carburants_voulus:
                        if rupture:
                            ruptures.append({'carb': nom_carburant.upper(), 'station': nom_station, 'maj': maj})
                        elif 'valeur' in prix.attrib and nom_carburant.upper() in carburants_voulus:
                            valeur = float(prix.attrib.get('valeur'))
                            stations.append({
                                'carb': nom_carburant.upper(),
                                'prix': valeur,
                                'station': nom_station,
                                'maj': maj
                            })
                            prix_liste.append(valeur)
        if prix_liste:
            prix_moyen = mean(prix_liste)
        else:
            prix_moyen = None
        for carb in carburants_voulus:
            filtered = [s for s in stations if s['carb'] == carb]
            if filtered:
                filtered.sort(key=lambda x: x['prix'])
                info = filtered[0]
                ecart = info['prix'] - prix_moyen if prix_moyen is not None else 0
                signe = "+" if ecart > 0 else ""
                if ecart < -0.01:
                    tag = 'avantageux'
                elif ecart > 0.01:
                    tag = 'desavantageux'
                else:
                    tag = 'neutre'
                table_rows.append((
                    "CP " + cp_critere,
                    carb,
                    1,
                    info['station'],
                    str(info['prix']),
                    str(info['maj']),
                    f"{signe}{round(ecart, 3)}" if prix_moyen is not None else "",
                    str(prix_moyen) if prix_moyen is not None else "",
                    tag
                ))
            else:
                table_rows.append((
                    "CP " + cp_critere,
                    carb,
                    "",
                    "Aucune donnée disponible",
                    "",
                    "",
                    "",
                    "",
                    'neutre'
                ))
        for r in ruptures:
            ruptures_dict.setdefault("CP " + cp_critere, {}).setdefault(r['carb'], []).append({'station': r['station'], 'maj': r['maj']})

    # --- Affichage dans le tableau ---
    if table_rows:
        label_tableau.config(text="Résultats carburant par zone")
        for row in table_rows:
            treeview.insert(
                "",
                "end",
                values=row[:-1],
                tags=(row[-1],)
            )
    else:
        label_tableau.config(text="Aucun résultat trouvé.")

    # --- Ruptures ---
    if ruptures_dict:
        ruptures_frame.pack(fill="x", padx=10, pady=5)
        for zone, ruptures_carb in ruptures_dict.items():
            for carb, ruptures in ruptures_carb.items():
                lbl = tk.Label(ruptures_frame, text=f"{zone} : Stations EN RUPTURE pour {carb} :", fg="#FF9900", font=("Arial", 10, "bold"))
                lbl.pack(anchor="w")
                for info in ruptures:
                    l = tk.Label(ruptures_frame, text=f"  {info['station']} - EN RUPTURE (depuis le {info['maj']})", fg="#FF9900")
                    l.pack(anchor="w")

    btn_chercher.config(state=tk.NORMAL)
    lbl_attente.config(text="")

# --- Interface graphique ---
root_win = tk.Tk()
root_win.title("Stations-service les moins chères")

main_frame = tk.Frame(root_win)
main_frame.pack(padx=10, pady=10)

criteria_frame = ttk.LabelFrame(main_frame, text="Critères de recherche")
criteria_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

tk.Label(criteria_frame, text="Ville :").grid(row=0, column=0, sticky="w")
entry_ville = tk.Entry(criteria_frame, width=50)
entry_ville.grid(row=0, column=1, padx=5, pady=5)
entry_ville.bind("<KeyRelease>", get_commune_suggestions)
entry_ville.tooltip = tk.Label(criteria_frame, text="Commencez à taper pour voir les suggestions.", fg="grey", font=("Arial", 8))
entry_ville.tooltip.grid(row=0, column=3, sticky="w")

listbox_suggestions = tk.Listbox(root_win, width=48, height=7)
listbox_suggestions.bind("<<ListboxSelect>>", select_commune)

btn_add_ville = tk.Button(criteria_frame, text="Ajouter la ville", command=add_ville)
btn_add_ville.grid(row=0, column=2, padx=5, pady=5)

tk.Label(criteria_frame, text="Villes sélectionnées :").grid(row=1, column=0, sticky="nw")
villes_listbox = tk.Listbox(criteria_frame, width=48, height=4)
villes_listbox.grid(row=1, column=1, padx=5, pady=5, sticky="w", columnspan=2)

btns_ville_frame = tk.Frame(criteria_frame)
btns_ville_frame.grid(row=2, column=1, sticky="w", pady=2)
btn_remove_ville = tk.Button(btns_ville_frame, text="Retirer la ville", command=remove_ville)
btn_remove_ville.pack(side="left", padx=2)

tk.Label(criteria_frame, text="Code postal :").grid(row=3, column=0, sticky="w")
entry_cp = tk.Entry(criteria_frame, width=10)
entry_cp.grid(row=3, column=1, sticky="w", padx=5, pady=5)

tk.Label(criteria_frame, text="Département :").grid(row=4, column=0, sticky="w")
entry_dept = tk.Entry(criteria_frame, width=5)
entry_dept.grid(row=4, column=1, sticky="w", padx=5, pady=5)

tk.Label(criteria_frame, text="Carburants :").grid(row=5, column=0, sticky="nw", pady=(10,0))
carburants_possibles = ["SP95", "E10", "GPLc", "GAZOLE", "SP98", "E85"]
carburant_vars = {}
carburants_frame = tk.Frame(criteria_frame)
carburants_frame.grid(row=5, column=1, sticky="w", pady=(10,0))

for i, carb in enumerate(carburants_possibles):
    var = tk.BooleanVar()
    carburant_vars[carb.upper()] = var
    cb = tk.Checkbutton(carburants_frame, text=carb, variable=var)
    cb.grid(row=i//3, column=i%3, sticky="w", padx=5)

btns_carb_frame = tk.Frame(criteria_frame)
btns_carb_frame.grid(row=6, column=1, sticky="w")
btn_tout_cocher = tk.Button(btns_carb_frame, text="Tout cocher", command=tout_cocher)
btn_tout_cocher.pack(side="left", padx=2)
btn_tout_decocher = tk.Button(btns_carb_frame, text="Tout décocher", command=tout_decocher)
btn_tout_decocher.pack(side="left", padx=2)

var_ouvertes = tk.BooleanVar()
cb_ouvertes = tk.Checkbutton(criteria_frame, text="Afficher uniquement les stations ouvertes maintenant", variable=var_ouvertes)
cb_ouvertes.grid(row=7, column=1, sticky="w", pady=(5,0))

btn_chercher = tk.Button(
    criteria_frame,
    text="Chercher",
    command=chercher,
    bg="#FFD700",           # Jaune
    fg="black",             # Texte noir
    activebackground="#FFC300", # Jaune foncé au clic
    activeforeground="black",
    font=("Arial", 12, "bold")
)
btn_chercher.grid(row=8, column=0, columnspan=3, pady=10)
lbl_attente = tk.Label(criteria_frame, text="", fg="blue")
lbl_attente.grid(row=9, column=0, columnspan=3)

ttk.Separator(main_frame, orient="horizontal").grid(row=1, column=0, sticky="ew", pady=10)

label_tableau = tk.Label(main_frame, text="", font=("Arial", 12, "bold"))
label_tableau.grid(row=2, column=0, sticky="w", padx=5)
treeview = ttk.Treeview(main_frame, columns=("Zone", "Carburant", "Rang", "Station", "Prix", "Maj", "Écart", "Moyenne"), show="headings", height=15)
treeview.grid(row=3, column=0, padx=5, pady=2, sticky="ew")
treeview.heading("Zone", text="Zone")
treeview.heading("Carburant", text="Carburant")
treeview.heading("Rang", text="Rang")
treeview.heading("Station", text="Station")
treeview.heading("Prix", text="Prix (c€/L)")
treeview.heading("Maj", text="Maj")
treeview.heading("Écart", text="Écart au moyen (c€/L)")
treeview.heading("Moyenne", text="Moyenne (c€/L)")
treeview.column("Zone", width=110, anchor="center")
treeview.column("Carburant", width=80, anchor="center")
treeview.column("Rang", width=40, anchor="center")
treeview.column("Station", width=320)
treeview.column("Prix", width=80, anchor="e")
treeview.column("Maj", width=80, anchor="center")
treeview.column("Écart", width=110, anchor="e")
treeview.column("Moyenne", width=110, anchor="e")
treeview.tag_configure('avantageux', foreground='green')
treeview.tag_configure('desavantageux', foreground='red')
treeview.tag_configure('neutre', foreground='black')

ruptures_frame = tk.Frame(main_frame)

root_win.mainloop()
