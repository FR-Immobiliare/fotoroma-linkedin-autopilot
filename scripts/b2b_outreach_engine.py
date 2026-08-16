#!/usr/bin/env python3
"""
FotoRomaImmobiliare — B2B Personalized Outreach Engine
Genera email e messaggi iper-personalizzati tramite AI per ciascuna agenzia e gestisce l'invio controllato.
"""

import os
import sys
import csv
import json
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Configurazione Secrets
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")  # Tua email es. antonio@fotoroma18.it o gmail
SMTP_PASS = os.getenv("SMTP_PASS")  # App password
SENDER_NAME = "Antonio Picariello | FotoRomaImmobiliare"

CONTACTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "enriched_contacts.csv")
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "contacted_log.csv")

def get_already_contacted():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        return set(row[0] for row in reader if row)

def log_contact(email, agency_name, status):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([email, agency_name, datetime.now().isoformat(), status])

def generate_personalized_copy(agency_name, zone, city, category):
    """
    Genera copy personalizzato ad altissima conversione focalizzato su:
    - Filtrare i curiosi a monte
    - Zero sopralluoghi a vuoto
    - Consegna in 72h dal pagamento
    """
    is_pm = "property" in category.lower() or "affitti" in category.lower()

    if is_pm:
        subject = f"Presentazione annunci per gli immobili in gestione a {city}"
        body = f"""Buongiorno Team di {agency_name},

seguo con interesse la vostra selezione di immobili per affitti brevi e medi a {city}{f' (in particolare zona {zone})' if zone else ''}.

Come sapete, sugli annunci Airbnb e Booking gli ospiti decidono in 3 secondi: foto luminose e curate nei minimi dettagli permettono di proteggere il prezzo per notte anche in bassa stagione ed evitare contestazioni al check-in.

Realizziamo servizi fotografici professionali dedicati agli affitti brevi:
• Foto ad alta definizione ottimizzate per portali OTA
• Consegna rapida in 72 ore dal pagamento
• Servizio Basic a partire da 80 €

Se avete un nuovo immobile in onboarding a {city}, mi farebbe piacere collaborare su una prima prova senza impegno.

Potete visionare i nostri lavori su: https://fotoromaimmobiliare.it
O scrivermi direttamente su WhatsApp al: +39 334 308 9759

Un cordiale saluto,
Antonio Picariello
FotoRomaImmobiliare"""
    else:
        subject = f"Qualificazione contatti e visite per gli annunci a {zone if zone else city}"
        body = f"""Buongiorno Team di {agency_name},

vi scrivo perché seguo da vicino il mercato immobiliare di {city}{f' e in particolare le vostre proposte in zona {zone}' if zone else ''}.

Il problema più frequente che riscontro parlando con i colleghi agenti è il tempo perso in sopralluoghi con 'curiosi' o persone che dal vivo restano deluse perché le foto dell'annuncio non erano chiare o fedeli.

Una fotografia professionale e trasparente serve a fare l'esatto opposto: FILTRARE a monte. Chi vi contatta ha già capito la luce e gli spazi reali e viene in visita con l'intenzione di fare una proposta seria.

I nostri servizi per le agenzie di compravendita:
• Servizio Fotografico Full (foto illimitate a 150 €)
• Virtual Tour Matterport 360° per acquirenti qualificati e fuori sede
• Video Reportage 4K
• Consegna garantita in 72 ore dal pagamento

Se avete un incarico in zona da lanciare o sbloccare, mi farebbe piacere fare una prima collaborazione.

Trovate il nostro portfolio su: https://fotoromaimmobiliare.it
WhatsApp diretto: +39 334 308 9759

Buon lavoro,
Antonio Picariello
Fondatore FotoRomaImmobiliare"""

    return subject, body

def send_outreach_batch(max_emails=10):
    already_contacted = get_already_contacted()

    if not os.path.exists(CONTACTS_FILE):
        print(f"File contatti {CONTACTS_FILE} non trovato. Esegui prima contact_enricher.py.")
        return

    with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
        contacts = list(csv.DictReader(f))

    to_send = [c for c in contacts if c.get("email") and c.get("email") not in already_contacted]
    print(f"Trovati {len(to_send)} contatti pronti all'invio (invio max {max_emails} per sessione).")

    if not SMTP_USER or not SMTP_PASS:
        print("\n[MODALITÀ ANTEPRIMA]: Credenziali SMTP non configurate. Mostro esempio di email generata:")
        if to_send:
            subj, body = generate_personalized_copy(to_send[0]["name"], to_send[0]["zone"], to_send[0]["city"], to_send[0]["category"])
            print(f"\n📧 DESTINATARIO: {to_send[0]['email']} ({to_send[0]['name']})")
            print(f"📌 OGGETTO: {subj}")
            print(f"📝 TESTO:\n{body}\n")
        return

    # Invio reale con SMTP
    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)

        for c in to_send[:max_emails]:
            email = c["email"]
            name = c["name"]
            zone = c["zone"]
            city = c["city"]
            cat = c["category"]

            subj, body = generate_personalized_copy(name, zone, city, cat)

            msg = MIMEMultipart()
            msg["From"] = f"{SENDER_NAME} <{SMTP_USER}>"
            msg["To"] = email
            msg["Subject"] = subj
            msg.attach(MIMEText(body, "plain", "utf-8"))

            server.sendmail(SMTP_USER, [email], msg.as_string())
            print(f"✅ Inviata email a: {email} ({name})")
            log_contact(email, name, "SENT")

        server.quit()
        print(f"\nBatch di {len(to_send[:max_emails])} email inviato con successo!")
    except Exception as e:
        print(f"Errore durante l'invio SMTP: {e}")

if __name__ == "__main__":
    send_outreach_batch(max_emails=5)
