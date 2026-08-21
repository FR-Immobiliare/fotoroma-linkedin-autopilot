#!/usr/bin/env python3
"""
FotoRomaImmobiliare — B2B Smart Outreach Engine
- Link secondario sotto il bottone WhatsApp: RIMANDA A PREZZI E TARIFFE UFFICIALI (fotoromaimmobiliare.it/prezzi-fotografo-immobiliare-roma)
- Disiscrizione automatica 1-Click
"""

import os
import sys
import csv
import time
import random
import base64
import smtplib
import urllib.parse
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "fotoroma18@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS", "unsvwxfhkugkklly")
SENDER_DISPLAY = "FotoRomaImmobiliare"
SENDER_EMAIL = "info@fotoromaimmobiliare.it"

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CONTACTS_FILES = [
    os.path.join(DATA_DIR, "airbnb_hosts_massive_3500.csv"),
    os.path.join(DATA_DIR, "prospects_southern_lazio.csv"),
    os.path.join(DATA_DIR, "enriched_contacts.csv")
]
LOG_FILE = os.path.join(DATA_DIR, "contacted_log.csv")
UNSUBSCRIBE_FILE = os.path.join(DATA_DIR, "unsubscribed.csv")

LOGO_URL = "https://raw.githubusercontent.com/FR-Immobiliare/fotoroma-linkedin-autopilot/main/data/logo_fotoroma_perfect_green.png"
HERO_URL = "https://raw.githubusercontent.com/FR-Immobiliare/fotoroma-linkedin-autopilot/main/data/hero_email_master.jpg"

def load_unsubscribed():
    if not os.path.exists(UNSUBSCRIBE_FILE):
        return set()
    with open(UNSUBSCRIBE_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        return {rows[0].strip().lower() for rows in reader if rows}

def load_already_contacted():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        return {rows[0].strip().lower() for rows in reader if rows}

def build_html_template(target_type, name, zone, city, recipient_email):
    is_pm = "AIRBNB" in target_type.upper() or "HOST" in target_type.upper() or "PROPERTY" in target_type.upper()
    category_code = "AIRBNB_HOST_PM" if is_pm else "AGENZIE_IMMOBILIARI"
    
    hero_img = HERO_URL
    subject = "IL TUO OSPITE SCEGLIE CON GLI OCCHI"
    headline = "FOTO MIGLIORI. CLIENTI MIGLIORI."
    subheadline = "La tua prossima prenotazione dipende da come ti presenti online."
    presentazione = "Sono Antonio, fotografo e titolare di <span style=\"color: #D4D6C8; text-decoration: none !important; border: none !important;\">FotoRomaImmobiliare&#8203;.it</span>.<br>Realizzo fotografie professionali, Virtual Tour e video per strutture ricettive e immobili destinati agli affitti brevi."
    intro_slogan = "Prima di prenotare, il tuo ospite guarda il tuo annuncio."
    intro_body = "Le immagini sono il primo contatto con il tuo immobile: possono determinare se continuerà a guardare, chiederà informazioni oppure passerà alla struttura successiva."
    
    points = [
        ("FOTOGRAFIA D'INTERNI PER AIRBNB — 80 € / 150 €", "Scatti professionali pensati per presentare al meglio gli ambienti sulle piattaforme di prenotazione."),
        ("VIRTUAL TOUR 360° MATTERPORT — 290 €", "Un'esperienza immersiva per permettere al potenziale ospite di esplorare gli ambienti prima di prenotare."),
        ("VIDEO REPORTAGE 4K & DRONE", "Walkthrough e riprese aeree per strutture di pregio e contenuti promozionali."),
        ("CONSEGNA RAPIDA IN 72H DAL PAGAMENTO", "File pronti per Airbnb, Booking, Vrbo e per i tuoi canali online.")
    ]
    whatsapp_msg = f"Ciao,%20ti%20contatto%20dall%27email%20di%20FotoRomaImmobiliare.it,%20vorrei%20informazioni%20per%20un%20servizio%20fotografico"

    items_html = ""
    for i, (title, desc) in enumerate(points):
        mb = "12px" if i < len(points) - 1 else "0"
        items_html += f"""
        <div style="background-color: #35373D !important; border: 1px solid #4D5059; border-radius: 14px; padding: 14px 16px; margin-bottom: {mb}; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
          <p style="margin: 0 0 5px 0; color: #88C253 !important; font-size: 13px; font-weight: 700; text-align: center; text-transform: uppercase; letter-spacing: 0.4px; line-height: 1.35; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;">
            {title}
          </p>
          <p style="margin: 0; color: #B5B7AB !important; font-size: 12.5px; line-height: 1.6; text-align: center; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;">
            {desc}
          </p>
        </div>
        """

    auto_unsub_url = f"https://www.fotoromaimmobiliare.it/disiscrizione?email={urllib.parse.quote(recipient_email)}"
    prezzi_url = "https://www.fotoromaimmobiliare.it/prezzi-fotografo-immobiliare-roma"
    tracking_pixel_url = f"https://www.fotoromaimmobiliare.it/assets/logo.png?trk={urllib.parse.quote(recipient_email)}&cat={category_code}&t={int(time.time())}"

    html = f"""<!DOCTYPE html>
<html lang="it" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="light dark">
  <meta name="supported-color-schemes" content="light dark">
  <meta name="format-detection" content="telephone=no, date=no, address=no, email=no, url=no">
  <title>FotoRomaImmobiliare</title>
  <style>
    :root {{
      color-scheme: light dark;
      supported-color-schemes: light dark;
    }}
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    body, table, td, p, a, h1, span {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }}
    @media only screen and (max-width: 520px) {{
      .wrapper-table {{ width: 100% !important; border-radius: 0 !important; }}
      .content-cell {{ padding: 24px 18px !important; }}
      .headline-text {{ font-size: 17px !important; }}
      .subheadline-text {{ font-size: 13px !important; }}
      .intro-text {{ font-size: 12px !important; }}
      .cta-btn {{ display: block !important; width: 100% !important; box-sizing: border-box !important; padding: 13px 14px !important; font-size: 13.5px !important; }}
    }}
  </style>
</head>
<body bgcolor="#3A3C42" style="margin: 0; padding: 18px 0; background-color: #3A3C42 !important; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #F7F8E2 !important; -webkit-font-smoothing: antialiased;">
  
  <table class="wrapper-table" align="center" border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="#43464D" style="max-width: 570px; background-color: #43464D !important; border-radius: 20px; overflow: hidden; margin: 0 auto; border: 1px solid #585C66; box-shadow: 0 16px 36px rgba(0,0,0,0.5);">
    
    <!-- HEADER BRAND -->
    <tr>
      <td align="center" bgcolor="#2F3136" style="padding: 20px 18px 15px 18px; background-color: #2F3136 !important; border-bottom: 1px solid #4D5059; text-align: center;">
        <img src="{LOGO_URL}" alt="FotoRomaImmobiliare" style="height: 76px; max-height: 76px; width: auto; display: block; margin: 0 auto 5px auto;" />
        <p style="margin: 0; color: #F7F8E2 !important; font-size: 10.5px; letter-spacing: 2px; text-transform: uppercase; font-weight: 700; text-align: center;">FOTO • VIDEO • VIRTUAL TOUR PER IMMOBILI</p>
      </td>
    </tr>

    <!-- HERO IMAGE -->
    <tr>
      <td bgcolor="#43464D" style="padding: 0; background-color: #43464D !important;">
        <img src="{hero_img}" alt="FotoRomaImmobiliare" style="width: 100%; max-height: 235px; object-fit: cover; display: block;" />
      </td>
    </tr>

    <!-- CONTENUTO PRINCIPALE (100% CENTRATO) -->
    <tr>
      <td class="content-cell" align="center" bgcolor="#43464D" style="padding: 30px 28px 26px 28px; background-color: #43464D !important; text-align: center;">
        
        <!-- HEADLINE (CENTRATA) -->
        <h1 class="headline-text" style="margin: 0 0 10px 0; color: #88C253 !important; font-size: 19px; font-weight: 800; line-height: 1.3; text-transform: uppercase; letter-spacing: 0.5px; text-align: center;">
          {headline}
        </h1>

        <!-- SUBHEADLINE (CENTRATA) -->
        <p class="subheadline-text" style="margin: 0 0 18px 0; color: #F7F8E2 !important; font-size: 14px; font-weight: 700; line-height: 1.45; text-align: center;">
          {subheadline}
        </p>

        <!-- BREVISSIMA PRESENTAZIONE (CENTRATA) -->
        <p style="margin: 0 0 20px 0; color: #D4D6C8 !important; font-size: 12.5px; line-height: 1.65; text-align: center;">
          {presentazione}
        </p>
        
        <!-- SLOGAN & INTRODUZIONE COMMERCIALE (CENTRATA) -->
        <p class="slogan-text" style="margin: 0 0 10px 0; color: #F7F8E2 !important; font-size: 14.5px; font-weight: 700; line-height: 1.4; text-align: center; letter-spacing: -0.01em;">
          {intro_slogan}
        </p>
        <p class="intro-text" style="margin: 0 0 26px 0; color: #B5B7AB !important; font-size: 12.5px; line-height: 1.7; text-align: center;">
          {intro_body}
        </p>

        <!-- SCHEDE SERVIZI -->
        <div style="margin-bottom: 28px; text-align: center;">
          {items_html}
        </div>

        <!-- CTA WHATSAPP (PILL OUTLINE STYLE - TESTO CHIARO & BORDO VERDE PULITO) -->
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%">
          <tr>
            <td align="center" style="padding-bottom: 14px; text-align: center;">
              <a class="cta-btn" href="https://wa.me/393343089759?text={whatsapp_msg}" target="_blank" style="display: inline-block; background-color: rgba(53, 55, 61, 0.4); border: 1.5px solid #88C253; color: #F7F8E2 !important; font-weight: 600; font-size: 14px; text-decoration: none; padding: 13px 38px; border-radius: 9999px; text-align: center; letter-spacing: 0.2px;">
                Scrivimi
              </a>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding-bottom: 8px; text-align: center;">
              <p style="margin: 0; color: #B5B7AB !important; font-size: 12px; text-align: center;">Oppure chiama: <strong style="color: #F7F8E2 !important;">+39 334 308 9759</strong></p>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding-bottom: 22px; text-align: center;">
              <a href="{prezzi_url}" target="_blank" style="color: #B5B7AB !important; font-size: 11px; text-decoration: underline; text-align: center;">
                Consulta il listino prezzi ufficiale su fotoromaimmobiliare.it
              </a>
            </td>
          </tr>
        </table>

        <!-- CHIUSURA -->
        <div style="border-top: 1px solid #585C66; padding-top: 16px; margin-top: 6px; text-align: center;">
          <p style="margin: 0; text-align: center; color: #F7F8E2 !important; font-size: 12.5px; font-weight: 700; line-height: 1.45; text-transform: uppercase; letter-spacing: 0.4px;">
            LA PRIMA VISITA AL TUO IMMOBILE AVVIENE ATTRAVERSO LE FOTO CHE MOSTRI ONLINE.
          </p>
        </div>

      </td>
    </tr>

    <!-- FOOTER ISTITUZIONALE -->
    <tr>
      <td align="center" bgcolor="#2F3136" style="padding: 20px 22px; background-color: #2F3136 !important; border-top: 1px solid #4D5059; color: #93968A !important; font-size: 10.5px; line-height: 1.55;">
        <p style="margin: 0 0 4px 0; font-weight: 600; color: #F7F8E2 !important;">FotoRomaImmobiliare • di Antonio Picariello</p>
        <p style="margin: 0 0 4px 0;">Via Filippo Cremonesi 8, 00155 Roma • P.IVA 15883601002 • Consegna in 72h dal pagamento</p>
        <p style="margin: 0 0 12px 0;">Fotografia d'interni, Video 4K, Drone e Virtual Tour 360° per compravendite e alloggi turistici.</p>
        
        <div style="border-top: 1px solid #43464D; padding-top: 9px; font-size: 9.5px; color: #7E8176 !important; text-align: center;">
          <p style="margin: 0 0 3px 0;">
            <em>Ricevi questa comunicazione informativa B2B in quanto la tua struttura o agenzia è presente su elenchi pubblici, portali di settore o registri di categoria.</em>
          </p>
          <p style="margin: 0;">
            Se non desideri più ricevere aggiornamenti o proposte, <a href="{auto_unsub_url}" target="_blank" style="color: #88C253 !important; text-decoration: underline;">clicca qui per disiscriverti automaticamente con 1 click</a>.
          </p>
        </div>
      </td>
    </tr>

  </table>

  <!-- TRACKING PIXEL INVISIBILE -->
  <img src="{tracking_pixel_url}" width="1" height="1" style="display:none; width:1px; height:1px; border:0;" alt="" />

</body>
</html>
"""
    return subject, html, category_code

def send_outreach_batch(max_emails=35):
    unsubscribed = load_unsubscribed()
    already_contacted = load_already_contacted()
    
    candidates = []
    for csv_file in CONTACTS_FILES:
        if not os.path.exists(csv_file):
            continue
        with open(csv_file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = (row.get("email") or row.get("Email") or "").strip().lower()
                if not email or "@" not in email:
                    continue
                if email in unsubscribed or email in already_contacted:
                    continue
                name = row.get("nome") or row.get("Nome") or row.get("name") or "Gentile Host / Agenzia"
                zone = row.get("zona") or row.get("Zona") or row.get("zone") or ""
                city = row.get("citta") or row.get("Citta") or row.get("city") or "Roma"
                target_type = row.get("categoria") or row.get("Categoria") or row.get("type") or "AIRBNB"
                
                # ESCLUSIONE RESTRITTIVA NAPOLI SU RICHIESTA UTENTE
                full_info = f"{city} {zone} {name} {target_type} {email}".lower()
                if "napoli" in full_info:
                    continue

                candidates.append({
                    "email": email,
                    "name": name,
                    "zone": zone,
                    "city": city,
                    "target_type": target_type
                })
    
    if not candidates:
        print("ℹ️ Nessun nuovo contatto da inviare (tutti già contattati o disiscritti).")
        return 0

    batch = candidates[:max_emails]
    print(f"🚀 Avvio invio batch di {len(batch)} email (su un totale di {len(candidates)} lead in coda)...")
    
    sent_count = 0
    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        
        for item in batch:
            email = item["email"]
            name = item["name"]
            zone = item["zone"]
            city = item["city"]
            target_type = item["target_type"]
            
            subject, html_content, category_code = build_html_template(target_type, name, zone, city, email)
            
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{SENDER_DISPLAY} <{SMTP_USER}>"
            msg["To"] = email
            msg["Reply-To"] = SENDER_EMAIL
            msg.attach(MIMEText(html_content, "html", "utf-8"))
            
            try:
                server.sendmail(SMTP_USER, [email], msg.as_string())
                sent_count += 1
                print(f"  ✅ Inviata [{sent_count}/{len(batch)}]: {email} ({city} - {category_code})")
                
                # Registra nel log
                with open(LOG_FILE, "a", encoding="utf-8", newline="") as lf:
                    writer = csv.writer(lf)
                    writer.writerow([email, datetime.now().isoformat(), category_code, city, zone])
                
                # Pausa casuale anti-spam
                time.sleep(random.uniform(2.5, 5.5))
            except Exception as e:
                print(f"  ❌ Errore invio a {email}: {e}")
                
        server.quit()
    except Exception as e:
        print(f"❌ Errore connessione SMTP: {e}")
        
    print(f"\n✨ Batch completato: {sent_count} email inviate con successo.")
    return sent_count

if __name__ == "__main__":
    limit = 35
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            pass
    send_outreach_batch(max_emails=limit)

