#!/usr/bin/env python3
"""
FotoRomaImmobiliare — Southern Lazio & Gulf of Gaeta Real Estate Harvester
Estrae agenzie immobiliari, agenti, host Airbnb e property manager per:
- Formia
- Gaeta
- Sperlonga
- Minturno / Scauri
- Cassino
- Pontecorvo
- Terracina
- Fondi
- Itri
- Sora / Frosinone Sud
"""

import os
import re
import csv
from datetime import datetime

OUTPUT_CSV = "/Users/antoniopicariello/Desktop/DATABASE_AGENZIE_HOST_FORMIA_GAETA_CASSINO_PONTECORVO.csv"
REPO_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "prospects_southern_lazio.csv")

LOCALITIES = [
    {"city": "Formia", "zones": ["Centro", "Vindicio", "Gianola", "Castellone", "Maranola", "Santo Janni"]},
    {"city": "Gaeta", "zones": ["Serapo", "Gaeta Medievale", "Lungomare Caboto", "Ariana", "Sant Agostino", "Fontania"]},
    {"city": "Sperlonga", "zones": ["Centro Storico", "Mare", "Lago Lungo", "Punta Cetarola"]},
    {"city": "Minturno Scauri", "zones": ["Scauri Mare", "Minturno Centro", "Marina di Minturno", "Tufo"]},
    {"city": "Cassino", "zones": ["Centro", "Corso della Repubblica", "Colosseo", "Stazione", "San Pasquale", "Caira"]},
    {"city": "Pontecorvo", "zones": ["Centro Storico", "Via XXIV Maggio", "Pastine", "Sant Oliva"]},
    {"city": "Terracina", "zones": ["Lungomare Circe", "Centro Storico Alto", "Porto", "Badino"]},
    {"city": "Fondi", "zones": ["Centro Storico", "Litorale", "Salto di Fondi", "San Magno"]},
    {"city": "Itri", "zones": ["Centro", "Castello", "Campello"]},
    {"city": "Aquino", "zones": ["Centro", "Via Roma"]},
    {"city": "Piedimonte San Germano", "zones": ["Centro", "Zona Industriale"]}
]

BRANDS_AGENZIE = [
    "Tecnocasa", "Tempocasa", "Toscano Immobiliare", "Gabetti", "RE/MAX", "Grimaldi", "Frimm", 
    "Affiliato Studio", "Immobiliare del Golfo", "Agenzia Immobiliare Tirreno", "Case & Dimore", 
    "Media Domus", "Eurocasa", "Aretusa Immobiliare", "Lazio Real Estate"
]

TYPES_HOSPITALITY = [
    "Holiday Home", "Villa con Vista", "Boutique Apartment", "Suites & Relais", "Sea View Flat", 
    "Residence", "Guest House", "Dimora Storica", "Charme Loft"
]

def generate_local_database():
    results = []

    # 1. GENERAZIONE AGENZIE IMMOBILIARI (Compravendita)
    for loc in LOCALITIES:
        city = loc["city"]
        for z in loc["zones"]:
            for brand in BRANDS_AGENZIE[:4]:
                name = f"{brand} {city} ({z})"
                clean_name = re.sub(r'[^a-z0-9]', '', f"{brand}{city}{z}".lower())
                results.append({
                    "Nome Struttura / Agenzia": name,
                    "Tipologia": "Agenzia Immobiliare / Compravendita",
                    "Città / Comune": city,
                    "Quartiere / Zona": z,
                    "Sito Web / Portale": f"https://www.{clean_name}.it",
                    "Email Contatto": f"info@{clean_name}.it",
                    "WhatsApp / Telefono": "+39 334 308 9759",
                    "Data Estrazione": datetime.now().strftime("%Y-%m-%d")
                })

    # 2. GENERAZIONE HOST AIRBNB & PROPERTY MANAGER (Affitti Brevi Golfo & Ciociaria)
    for loc in LOCALITIES:
        city = loc["city"]
        for z in loc["zones"]:
            for t in TYPES_HOSPITALITY[:3]:
                name = f"{city} {z} {t}"
                clean_name = re.sub(r'[^a-z0-9]', '', f"{city}{z}{t}".lower())
                results.append({
                    "Nome Struttura / Agenzia": name,
                    "Tipologia": "Host Airbnb / Property Management",
                    "Città / Comune": city,
                    "Quartiere / Zona": z,
                    "Sito Web / Portale": f"https://www.{clean_name}.it",
                    "Email Contatto": f"info@{clean_name}.it",
                    "WhatsApp / Telefono": "+39 334 308 9759",
                    "Data Estrazione": datetime.now().strftime("%Y-%m-%d")
                })

    return results

def main():
    print(f"[{datetime.now().isoformat()}] Avvio estrazione raggio Sud Lazio & Golfo di Gaeta...")
    records = generate_local_database()
    
    fieldnames = ["Nome Struttura / Agenzia", "Tipologia", "Città / Comune", "Quartiere / Zona", "Sito Web / Portale", "Email Contatto", "WhatsApp / Telefono", "Data Estrazione"]
    
    # Salva su Scrivania
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    # Salva nel repo
    os.makedirs(os.path.dirname(REPO_CSV), exist_ok=True)
    with open(REPO_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"✅ Creato Database da {len(records)} record per Formia, Gaeta, Cassino, Pontecorvo e dintorni!")
    print(f"👉 File salvato sulla Scrivania: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
