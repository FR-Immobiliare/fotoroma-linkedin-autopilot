#!/usr/bin/env python3
"""
FotoRomaImmobiliare — Contact Scraper & Enricher
Visita i siti web delle agenzie/property manager nel CSV ed estrae email e WhatsApp di contatto.
"""

import os
import re
import csv
import json
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

INPUT_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "prospects_raw.csv")
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "enriched_contacts.csv")

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
IGNORE_EMAILS = {"wixpress.com", "example.com", "domain.com", "sentry.io", "png", "jpg", "jpeg", "webp"}

def extract_contacts_from_url(url):
    if not url or not url.startswith("http"):
        return {"email": "", "phone": ""}
    
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    emails_found = set()

    # Prova homepage e /contatti
    urls_to_check = [url]
    parsed = urllib.parse.urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    urls_to_check.append(urllib.parse.urljoin(base_url, "/contatti"))
    urls_to_check.append(urllib.parse.urljoin(base_url, "/contact"))

    for target in urls_to_check:
        try:
            req = urllib.request.Request(target, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                content_type = resp.headers.get("Content-Type", "")
                if "text/html" not in content_type:
                    continue
                html = resp.read().decode("utf-8", errors="ignore")
                
                # Cerca email mailto o testo
                matches = EMAIL_REGEX.findall(html)
                for m in matches:
                    clean_email = m.strip().lower()
                    domain = clean_email.split("@")[-1]
                    if not any(ign in domain for ign in IGNORE_EMAILS) and len(clean_email) <= 50:
                        emails_found.add(clean_email)
        except Exception:
            continue

    chosen_email = list(emails_found)[0] if emails_found else ""
    return {"email": chosen_email}

def enrich_database(limit=50):
    if not os.path.exists(INPUT_CSV):
        print(f"File {INPUT_CSV} non trovato.")
        return

    with open(INPUT_CSV, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Caricati {len(rows)} record dal database raw.")
    enriched_rows = []

    # Processa i primi record o quelli non ancora arricchiti
    for idx, row in enumerate(rows[:limit]):
        name = row.get("Nome Filiale / Struttura") or row.get("Nome Filiale / Agenzia") or ""
        city = row.get("Città") or ""
        zone = row.get("Quartiere / Micro-Zona") or row.get("Quartiere / Zona") or ""
        website = row.get("Sito Web") or ""
        linkedin = row.get("Ricerca LinkedIn") or ""
        category = row.get("Tipologia / Categoria") or "Agenzia Immobiliare"

        print(f"[{idx+1}/{limit}] Scansione contatti per: {name} ({website})...")
        contacts = extract_contacts_from_url(website) if website else {"email": ""}
        
        enriched_rows.append({
            "name": name,
            "category": category,
            "city": city,
            "zone": zone,
            "website": website,
            "email": contacts.get("email", ""),
            "linkedin_query": linkedin
        })

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    fieldnames = ["name", "category", "city", "zone", "website", "email", "linkedin_query"]
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched_rows)

    print(f"\n✅ Arricchimento completato! Salvato in {OUTPUT_CSV}")

if __name__ == "__main__":
    enrich_database(limit=30)
