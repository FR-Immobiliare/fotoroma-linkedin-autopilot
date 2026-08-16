#!/usr/bin/env python3
"""
FotoRomaImmobiliare — AI Market Trends & Editorial Agent
Analizza i trend globali e locali di Real Estate Marketing e genera contenuti educativi / strategici.
"""

import os
import sys
import json
import base64
import random
import urllib.request
import urllib.parse
from datetime import datetime

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_AUTHOR_URN = os.getenv("LINKEDIN_AUTHOR_URN")

QUEUE_DIR = os.path.join(os.path.dirname(__file__), "..", "queue_photos")
PUBLISHED_DIR = os.path.join(os.path.dirname(__file__), "..", "published")

# 5 Pilastri Editoriali per ruotare i contenuti
EDITORIAL_PILLARS = [
    {
        "type": "CASE_STUDY_BEFORE_AFTER",
        "theme": "Come una presentazione fedele e luminosa evita sopralluoghi a vuoto ed elimina i curiosi",
        "audience": "Agenti Immobiliari di Compravendita"
    },
    {
        "type": "GLOBAL_TREND_PROPTECH",
        "theme": "Trend globale Real Estate: l'impatto dei Virtual Tour 360 e del visual storytelling per vendere ad acquirenti stranieri (USA/UK/Nord Europa) senza farli viaggiare",
        "audience": "Property Manager di lusso e Agenzie Roma Centro"
    },
    {
        "type": "AIRBNB_REVENUE_OPTIMIZATION",
        "theme": "Come gli annunci Airbnb con foto professionali aumentano il tasso di conversione e il prezzo medio per notte senza resistenze",
        "audience": "Host e Property Manager di Affitti Brevi"
    },
    {
        "type": "MISTAKES_TO_AVOID",
        "theme": "I 3 errori che fanno perdere trattative alle agenzie: foto grandangolari deformate, foto buie da smartphone e annunci poco trasparenti",
        "audience": "Titolari di Agenzia e Broker"
    },
    {
        "type": "CONSTRUCTION_DEVELOPMENT",
        "theme": "Perché i costruttori e architetti devono documentare gli immobili finiti con foto e video prima della consegna",
        "audience": "Costruttori, Architetti e Interior Designer"
    }
]

PROMPT_SYSTEM = """
Sei il Social Media Strategist e Copywriter B2B di livello mondiale per FotoRomaImmobiliare (fondata da Antonio Picariello a Roma).
Scrivi post per LinkedIn capaci di generare autorevolezza, engagement e richieste di preventivo da parte di:
- Titolari di Agenzia Immobiliare (Roma, Napoli, Firenze)
- Property Manager e Gestori di Affitti Brevi
- Host Airbnb professionali
- Costruttori e Architetti

REGOLE TASSATIVE:
1. NON PARLARE MAI DI TECNICISMI FOTOGRAFICI (Niente parole come Flambient, ISO, focali, sensori).
2. PARLA SOLO DI BUSINESS E BENEFICI:
   - Filtrare i curiosi e perditempo a monte
   - Evitare appuntamenti a vuoto e delusioni al sopralluogo dal vivo
   - Ridurre i tempi di vendita / affitto
   - Aumentare il valore percepito senza subire ribassi sul prezzo
3. STRUTTURA DEL POST:
   - Gancio (Hook) potente nelle prime 2 righe (senza saluti generici)
   - Sviluppo logico con dati, riflessioni pratiche o aneddoti
   - Frasi corte e spaziose (massima leggibilità da mobile)
   - Emoji sobrie e professionali (📍, 📈, 🏠, 🤝, 💡)
   - Call to Action finale discreta (invito a mandare un messaggio o commentare)
   - 3-4 hashtag pertinenti alla fine.
"""

def generate_trend_post():
    pillar = random.choice(EDITORIAL_PILLARS)
    topic = pillar["theme"]
    target = pillar["audience"]

    if not GEMINI_API_KEY:
        # Template editoriale fallback avanzato
        return f"""Quanti appuntamenti perde un'agenzia ogni mese con persone che dal vivo dicono: "Ah, ma dalle foto sembrava un'altra cosa"?

L'errore più comune negli annunci immobiliari è pensare che le foto servano solo a "fare tanti click".

In realtà, una presentazione visiva curata e trasparente serve a fare l'esatto opposto: FILTRARE.

1. Elimina chi cerca qualcosa di diverso prima che vi faccia perdere 1 ora di sopralluogo.
2. Evita delusioni e obiezioni sul prezzo appena si varca la soglia.
3. Porta in visita solo acquirenti che hanno già compreso l'immobile e sono pronti a fare una proposta.

Meno visite a vuoto, trattative più veloci e venditori soddisfatti.

Voi come gestite la qualifica dei contatti prima di fissare i sopralluoghi?

#FotografiaImmobiliare #RealEstateRoma #FotoRomaImmobiliare #AgenziaImmobiliare"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"{PROMPT_SYSTEM}\n\nArgomento del post di oggi: {topic}\nTarget prioritario: {target}\n\nScrivi il post LinkedIn in italiano perfetto."
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.75, "maxOutputTokens": 800}
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"Errore chiamata Gemini: {e}")
        return generate_trend_post()  # fallback

if __name__ == "__main__":
    print(f"[{datetime.now().isoformat()}] Generazione post basato su Trend Globali e Benefici Clienti...")
    post = generate_trend_post()
    print("\n--- TESTO GENERATO ---")
    print(post)
    print("----------------------\n")
