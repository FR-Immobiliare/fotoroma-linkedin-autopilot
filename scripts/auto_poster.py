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
LINKEDIN_AUTHOR_URN = os.getenv("LINKEDIN_AUTHOR_URN")  # es. "urn:li:organization:XXXX"
PERMANENT_FB_TOKEN = "EAAhXLP9vwGQBSTRWYDYiXQQ8Pbej7YyPjGN5w7OLZCxglVg1xTdVNgjKx2rXQ08tk4WIt5PkKOeM2xjEZCzILoVgLg8jVyvvWrb7Cr2fh1yUxc9ssRVSHeZAQtH4d6cYn1c0oCh6cxQmD08QRrWau5ijunaFlgXgth63NEPozW7Gr3hEoWGcxd0nLZC8hIzb5x8ZCQZCrrmgZDZD"
FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN") or os.getenv("META_PAGE_ACCESS_TOKEN") or PERMANENT_FB_TOKEN
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID") or os.getenv("META_PAGE_ID", "861246003736290")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

QUEUE_DIR = os.path.join(os.path.dirname(__file__), "..", "queue_photos")
PUBLISHED_DIR = os.path.join(os.path.dirname(__file__), "..", "published")

PROMPT_SYSTEM = """
Sei il Social Media Strategist esperto per FotoRomaImmobiliare (fondata da Antonio a Roma, sito ufficiale: fotoromaimmobiliare.it).
Il tuo obiettivo è attrarre e convertire: Agenti Immobiliari, Property Manager, Host Airbnb e Proprietari.

USA UNO DEI SEGUENTI SLOGAN UFFICIALI COME GANCIO / HEADLINE INIZIALE:
- "FOTO MIGLIORI. CLIENTI MIGLIORI."
- "IL TUO OSPITE SCEGLIE CON GLI OCCHI."
- "LA PRIMA VISITA AL TUO IMMOBILE AVVIENE ATTRAVERSO LE FOTO CHE MOSTRI ONLINE."
- "LA TUA PROSSIMA PRENOTAZIONE DIPENDE DA COME TI PRESENTI ONLINE."

LINEE GUIDA RIGIDE PER IL COPY:
1. NON USARE MAI termini tecnici fotografici (no ISO, diaframmi, flambient).
2. VENDI I BENEFICI DI BUSINESS:
   - Filtrare i curiosi e i perditempo a monte
   - Evitare visite e sopralluoghi a vuoto
   - Aumentare le conversioni e proteggere il prezzo di vendita o il prezzo per notte senza sconti
   - Servizi: Foto grandangolari d'interni, Virtual Tour 360° Matterport, Drone 4K (Consegna rapida in 72h)
3. FORMATTAZIONE:
   - Gancio forte in maiuscolo
   - Frasi corte, paragrafi ariosi
   - 2-3 emoji sobrie (📍, 📸, 🔑, 🤝)
   - Cita la via o la zona reale fornita
   - Call to Action: invitare a un messaggio in privato o su WhatsApp al +39 334 308 9759
4. HASHTAG: #FotografiaImmobiliare #RealEstateRoma #FotoRomaImmobiliare #AirbnbRoma #PropertyManager
5. Lingua: Italiano impeccabile, elegante e commerciale.
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
    raw_location = os.path.splitext(filename)[0]
    if raw_location[:3].replace("_", "").isdigit():
        raw_location = raw_location[3:]
    location_name = raw_location.replace("_", " ").replace("FRI", "").strip()

    if not GEMINI_API_KEY:
        # Fallback copy di altissimo livello se l'API key non è impostata
        return f"""FOTO MIGLIORI. CLIENTI MIGLIORI.
La prima visita al tuo immobile avviene attraverso le foto che mostri online.

Quanti sopralluoghi fate a settimana con persone che poi dicono: "Ah, ma dalle foto sembrava diversa"?

Le immagini sono il primo contatto con il tuo immobile: determinano se un potenziale acquirente o ospite chiederà informazioni oppure passerà oltre.

📍 Servizio fotografico professionale recente per questo immobile in zona {location_name} (Roma).

📸 Foto grandangolari HDR + Virtual Tour 360° Matterport.
⏱️ Consegna rapida in 72h dal pagamento pronta per tutti i portali online.

Meno tempo perso per strada, contatti più qualificati.

💬 Hai un incarico o una struttura da valorizzare a Roma? Scrivimi in privato o su WhatsApp al +39 334 308 9759.

🌐 Portfolio e tariffe: fotoromaimmobiliare.it

#FotografiaImmobiliare #RealEstateRoma #FotoRomaImmobiliare #ImmobiliareRoma #AirbnbRoma"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    with open(photo_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    mime_type = "image/jpeg" if photo_path.lower().endswith((".jpg", ".jpeg")) else "image/png"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{PROMPT_SYSTEM}\n\nIndirizzo/Location dello shooting: {location_name}. Scrivi il post perfetto per accompagnare questa foto."},
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
        return f"FOTO MIGLIORI. CLIENTI MIGLIORI.\nLa prima visita al tuo immobile avviene attraverso le foto che mostri online.\n\n📍 Servizio fotografico professionale in zona {location_name} (Roma).\nConsegna in 72h dal pagamento.\n\n💬 Scrivimi su WhatsApp (+39 334 308 9759) o visita fotoromaimmobiliare.it"

def publish_to_facebook(photo_path, caption):
    if not FACEBOOK_PAGE_ACCESS_TOKEN:
        print("ℹ️ FACEBOOK_PAGE_ACCESS_TOKEN non configurato (Skip pubblicazione FB).")
        return None

    print(f"[{datetime.now().isoformat()}] Pubblicazione immagine su Pagina Facebook ({FACEBOOK_PAGE_ID})...")
    
    # Upload multipart diretto
    url = f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}/photos"
    boundary = "----WebKitFormBoundary" + os.urandom(16).hex()
    
    with open(photo_path, "rb") as f:
        photo_bytes = f.read()

    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="caption"\r\n\r\n')
    body.extend(caption.encode("utf-8") + b"\r\n")

    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="access_token"\r\n\r\n')
    body.extend(FACEBOOK_PAGE_ACCESS_TOKEN.encode("utf-8") + b"\r\n")

    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="source"; filename="{os.path.basename(photo_path)}"\r\n'.encode())
    body.extend(b"Content-Type: image/jpeg\r\n\r\n")
    body.extend(photo_bytes + b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())

    req = urllib.request.Request(url, data=bytes(body), headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            post_id = res.get("id") or res.get("post_id")
            print(f"✅ Foto pubblicata con successo su Facebook! Post ID: {post_id}")
            return post_id
    except Exception as e:
        print(f"❌ Errore upload Facebook: {e}")
        return None

def upload_image_to_linkedin(photo_path, author_urn, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

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
    print(f"[{datetime.now().isoformat()}] Avvio FotoRomaImmobiliare Social Cloud Engine...")
    
    photo = get_next_photo()
    if not photo:
        print("Coda foto vuota! Inserisci nuove immagini in queue_photos/.")
        sys.exit(0)

    print(f"📸 Foto selezionata dalla coda: {os.path.basename(photo)}")
    
    # 1. Genera il copy strategico con gancio / slogan
    post_text = generate_copy_with_ai(photo)
    print("\n--- TESTO STRATEGICO GENERATO ---")
    print(post_text)
    print("---------------------------------\n")

    fb_ok = False
    li_ok = False

    # 2. Pubblica su Facebook Page (se token presente)
    if FACEBOOK_PAGE_ACCESS_TOKEN:
        fb_id = publish_to_facebook(photo, post_text)
        if fb_id:
            fb_ok = True

    # 3. Pubblica su LinkedIn (se token presente)
    if LINKEDIN_ACCESS_TOKEN and LINKEDIN_AUTHOR_URN:
        try:
            print("Caricamento immagine su LinkedIn...")
            asset_urn = upload_image_to_linkedin(photo, LINKEDIN_AUTHOR_URN, LINKEDIN_ACCESS_TOKEN)
            print("Pubblicazione post su LinkedIn...")
            li_id = publish_linkedin_post(post_text, asset_urn, LINKEDIN_AUTHOR_URN, LINKEDIN_ACCESS_TOKEN)
            print(f"✅ Post pubblicato su LinkedIn! ID: {li_id}")
            li_ok = True
        except Exception as e:
            print(f"❌ Errore LinkedIn: {e}")

    # 4. Sposta la foto in published/ solo se almeno un canale ha pubblicato
    if fb_ok or li_ok or not (FACEBOOK_PAGE_ACCESS_TOKEN or LINKEDIN_ACCESS_TOKEN):
        dest_path = os.path.join(PUBLISHED_DIR, os.path.basename(photo))
        if os.path.exists(photo):
            shutil.move(photo, dest_path)
            print(f"📁 Foto archiviata in published/: {os.path.basename(photo)}")

if __name__ == "__main__":
    main()
