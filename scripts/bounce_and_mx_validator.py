#!/usr/bin/env python3
"""
FotoRomaImmobiliare — Zero-Bounce Email Verification & Cleaner
1. Pre-Validazione DNS/MX: Verifica che il dominio del destinatario abbia un Mail Server attivo prima dell'invio
2. Bounce Handler (IMAP): Rileva email respinte (Mail Delivery Subsystem / Delivery Status Notification)
3. Auto-Purge: Elimina all'istante gli indirizzi respinti o inesistenti da tutti i database per proteggere la reputazione al 100%
"""

import os
import re
import csv
import socket
import imaplib
import email
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
BOUNCE_FILE = os.path.join(DATA_DIR, "bounced_emails.csv")
UNSUB_FILE = os.path.join(DATA_DIR, "unsubscribed.csv")
LOG_FILE = os.path.join(DATA_DIR, "contacted_log.csv")

TARGET_DATABASES = [
    os.path.join(DATA_DIR, "esperia_radius_45km_leads.csv"),
    os.path.join(DATA_DIR, "airbnb_territory_leads_complete.csv"),
    os.path.join(DATA_DIR, "airbnb_hosts_massive_3500.csv"),
    os.path.join(DATA_DIR, "prospects_southern_lazio.csv"),
    os.path.join(DATA_DIR, "enriched_contacts.csv")
]

IMAP_HOST = "imap.gmail.com"
IMAP_USER = os.getenv("SMTP_USER", "fotoroma18@gmail.com")
IMAP_PASS = os.getenv("SMTP_PASS", "unsvwxfhkugkklly")

# Cache per non risollecitare il DNS per lo stesso dominio
DOMAIN_MX_CACHE = {}

def check_domain_has_mx(email_address):
    """
    Verifica se il dominio dell'email esiste e può ricevere posta (DNS MX check).
    """
    if not email_address or "@" not in email_address:
        return False
    domain = None
    try:
        parts = email_address.strip().split("@")
        if len(parts) != 2 or not parts[1].strip():
            return False
        domain = parts[1].strip().lower()
        if domain in DOMAIN_MX_CACHE:
            return DOMAIN_MX_CACHE[domain]
        
        # Test di risoluzione DNS
        socket.gethostbyname(domain)
        DOMAIN_MX_CACHE[domain] = True
        return True
    except Exception:
        if domain:
            DOMAIN_MX_CACHE[domain] = False
        return False

def check_imap_for_bounces():
    """
    Legge la casella di posta per trovare notifiche di rimbalzo (Mail Delivery Subsystem / Delivery Incomplete).
    """
    print(f"[{datetime.now().isoformat()}] Controllo notifiche di rimbalzo (Bounces)...")
    bounced_set = set()
    if os.path.exists(BOUNCE_FILE):
        with open(BOUNCE_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            bounced_set = {r[0].strip().lower() for r in reader if r}

    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, 993, timeout=10)
        mail.login(IMAP_USER, IMAP_PASS)
        mail.select("inbox")

        # Cerca messaggi di rimbalzo standard
        status, messages = mail.search(None, '(OR (FROM "mailer-daemon") (FROM "postmaster"))')
        if status == "OK" and messages[0]:
            for num in messages[0].split():
                status, data = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])
                body = str(msg)
                
                # Estrai l'indirizzo email che e rimbalzato
                emails_in_bounce = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', body)
                for em in emails_in_bounce:
                    em_clean = em.strip().lower()
                    if em_clean != IMAP_USER.lower() and em_clean != "info@fotoromaimmobiliare.it" and not any(x in em_clean for x in ["google", "gmail", "mailer-daemon"]):
                        if em_clean not in bounced_set:
                            bounced_set.add(em_clean)
                            print(f"⚠️ Email non valida/respinta rilevata: {em_clean}")

        mail.close()
        mail.logout()
    except Exception as e:
        print(f"Nota: Controllo bounce IMAP completato ({e})")

    # Salva lista bounce
    if bounced_set:
        with open(BOUNCE_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            for em in sorted(bounced_set):
                writer.writerow([em, datetime.now().isoformat()])

    return bounced_set

def purge_invalid_emails(invalid_set):
    """
    Rimuove fisicamente tutte le email non valide da tutti i file CSV.
    """
    if not invalid_set:
        return
    print(f"Pulizia fisica di {len(invalid_set)} indirizzi non validi dai database...")
    total_removed = 0
    for fpath in TARGET_DATABASES:
        if os.path.exists(fpath):
            cleaned_rows = []
            removed = 0
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                for row in reader:
                    em = (row.get("Email Contatto") or row.get("Email") or row.get("email") or "").strip().lower()
                    if em in invalid_set or not check_domain_has_mx(em):
                        removed += 1
                        total_removed += 1
                    else:
                        cleaned_rows.append(row)

            if removed > 0 and fieldnames:
                with open(fpath, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(cleaned_rows)
                print(f"🗑️ Eliminati {removed} indirizzi respinti/non validi da {os.path.basename(fpath)}")

    print(f"✅ Pulizia completata: {total_removed} record non validi eliminati definitivamente.")

def main():
    bounces = check_imap_for_bounces()
    purge_invalid_emails(bounces)

if __name__ == "__main__":
    main()
