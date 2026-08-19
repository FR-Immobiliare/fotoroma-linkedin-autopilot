#!/usr/bin/env python3
"""
FotoRomaImmobiliare — LinkedIn Autopilot Engine
Genera copy orientato ai benefici tramite AI e pubblica su LinkedIn con allegato fotografico.
"""

import os
import sys
import json
import glob
import shutil
import base64
import urllib.request
import urllib.parse
from datetime import datetime

# Carica automaticamente .env se presente (senza dipendenze esterne)
env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_file):
    try:
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except Exception:
        pass

# Environment Secrets
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_AUTHOR_URN = os.getenv("LINKEDIN_AUTHOR_URN")  # es. "urn:li:person:XXXX" o "urn:li:organization:XXXX"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


QUEUE_DIR = os.path.join(os.path.dirname(__file__), "..", "queue_photos")
PUBLISHED_DIR = os.path.join(os.path.dirname(__file__), "..", "published")

PROMPT_SYSTEM = """
Sei il Social Media Strategist esperto per FotoRomaImmobiliare (fondata da Antonio Picariello a Roma).
Il tuo obiettivo su LinkedIn è attrarre e convertire: Agenti Immobiliari, Property Manager, Host Airbnb e Costruttori.

LINEE GUIDA RIGIDE PER IL COPY:
1. NON USARE MAI termini tecnici come 'Flambient', ISO, tempi di scatto o tecnicismi fotografici.
2. VENDI I BENEFICI DI BUSINESS: spiegare come una foto luminosa e fedele aiuti a:
   - Filtrare a monte i 'turisti immobiliari' e i curiosi
   - Evitare appuntamenti e sopralluoghi a vuoto
   - Evitare che il cliente resti deluso al sopralluogo dal vivo
   - Accelerare le vendite/affitti e proteggere il valore dell'immobile senza sconti
3. FORMATTAZIONE:
   - Hook iniziale forte (prima riga senza convenevoli, niente 'buongiorno a tutti')
   - Frasi corte, paragrafi ariosi
   - Usa 2-3 emoji sobrie (📍, 📈, 🏠, 🤝)
   - Cita la zona/indirizzo reale fornito
   - Call to Action sobria finale: invitare a un messaggio in privato o su WhatsApp per un parere sul proprio portfolio annunci.
4. HASHTAG: Aggiungi 3-4 hashtag alla fine (es. #FotografiaImmobiliare #RealEstateRoma #FotoRomaImmobiliare #AgenziaImmobiliare).
5. Lingua: Italiano perfetto, professionale ma diretto.
"""

def get_next_photo():
    os.makedirs(QUEUE_DIR, exist_ok=True)
    os.makedirs(PUBLISHED_DIR, exist_ok=True)
    photos = sorted(glob.glob(os.path.join(QUEUE_DIR, "*.*")))
    if not photos:
        return None
    return photos[0]

def generate_copy_with_ai(photo_path):
    filename = os.path.basename(photo_path)
    # Estrai il nome del luogo dal file (es. 01_Campo_de_Fiori_19.jpg -> Campo de Fiori 19)
    raw_location = os.path.splitext(filename)[0]
    if raw_location[:3].replace("_", "").isdigit():
        raw_location = raw_location[3:]
    location_name = raw_location.replace("_", " ")

    if not GEMINI_API_KEY:
        # Fallback copy di altissimo livello se l'API key non è ancora impostata
        return f"""Quanti sopralluoghi fate a settimana con persone che dal vivo dicono: "Ah, ma dalle foto sembrava diversa"?

Le foto scure o ingannevoli creano due problemi per chi vende o affitta:
1. Portano decine di curiosi e perditempo in visita.
2. Creano delusione appena si varca la soglia d'ingresso.

📍 Servizio fotografico professionale recente per questo immobile in zona {location_name} (Roma).

Mostrare gli spazi con la luce giusta e la corretta proporzione serve a filtrare a monte i contatti: chi vi chiama ha già compreso l'immobile e viene al sopralluogo pronto a fare una proposta seria.

Meno tempo perso per strada, trattative più qualificate.

📩 Hai un incarico o un immobile da valorizzare a Roma? Scrivimi in privato o su WhatsApp (+39 334 308 9759).

#FotografiaImmobiliare #RealEstateRoma #FotoRomaImmobiliare #ImmobiliareRoma"""

    # Chiamata API Gemini
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    with open(photo_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    mime_type = "image/jpeg" if photo_path.lower().endswith((".jpg", ".jpeg")) else "image/png"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{PROMPT_SYSTEM}\n\nIndirizzo/Location dello shooting: {location_name}. Scrivi il post LinkedIn perfetto per accompagnare questa foto."},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": img_b64
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 800
        }
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"Errore chiamata Gemini: {e}")
        return f"Servizio fotografico professionale per immobile a Roma ({location_name}). Foto ad alta definizione per qualificare le visite ed evitare perdite di tempo sui portali.\n\n#FotografiaImmobiliare #FotoRomaImmobiliare"

def upload_image_to_linkedin(photo_path, author_urn, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    # Step 1: Register Upload
    register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    register_body = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": author_urn,
            "supportedUploadMechanism": ["SYNCHRONOUS_UPLOAD"]
        }
    }

    req = urllib.request.Request(register_url, data=json.dumps(register_body).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req) as resp:
        reg_data = json.loads(resp.read().decode("utf-8"))

    upload_url = reg_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset_urn = reg_data["value"]["asset"]

    # Step 2: Binary Upload
    with open(photo_path, "rb") as f:
        img_bytes = f.read()

    upload_req = urllib.request.Request(upload_url, data=img_bytes, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"}, method="POST")
    with urllib.request.urlopen(upload_req) as resp:
        pass

    return asset_urn

def publish_linkedin_post(text, asset_urn, author_urn, token):
    post_url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    post_body = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "IMAGE",
                "media": [
                    {
                        "status": "READY",
                        "media": asset_urn,
                        "title": {
                            "text": "FotoRomaImmobiliare"
                        }
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    req = urllib.request.Request(post_url, data=json.dumps(post_body).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res.get("id")

def main():
    print(f"[{datetime.now().isoformat()}] Avvio FotoRomaImmobiliare LinkedIn Autopilot...")
    
    photo = get_next_photo()
    if not photo:
        print("Coda foto vuota! Inserisci nuove immagini in queue_photos/.")
        sys.exit(0)

    print(f"Foto selezionata per la pubblicazione: {os.path.basename(photo)}")
    
    # Genera il copy con AI
    post_text = generate_copy_with_ai(photo)
    print("\n--- TESTO GENERATO DALL'AI ---")
    print(post_text)
    print("------------------------------\n")

    if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_AUTHOR_URN:
        print("ATTENZIONE: LINKEDIN_ACCESS_TOKEN o LINKEDIN_AUTHOR_URN mancanti.")
        print("Test locale completato con successo (generazione AI e selezione immagine OK).")
        sys.exit(0)

    # Upload su LinkedIn
    print("Caricamento immagine su LinkedIn...")
    asset_urn = upload_image_to_linkedin(photo, LINKEDIN_AUTHOR_URN, LINKEDIN_ACCESS_TOKEN)
    print(f"Asset registrato: {asset_urn}")

    print("Pubblicazione post su LinkedIn...")
    post_id = publish_linkedin_post(post_text, asset_urn, LINKEDIN_AUTHOR_URN, LINKEDIN_ACCESS_TOKEN)
    print(f"✅ Post pubblicato con successo! Post ID: {post_id}")

    # Archiviazione foto pubblicata
    dest_path = os.path.join(PUBLISHED_DIR, os.path.basename(photo))
    shutil.move(photo, dest_path)
    print(f"Foto spostata in archivio: {dest_path}")

if __name__ == "__main__":
    main()
