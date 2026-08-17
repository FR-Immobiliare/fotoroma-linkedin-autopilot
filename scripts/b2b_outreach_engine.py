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
SENDER_DISPLAY = "Antonio Picariello | FotoRomaImmobiliare"
SENDER_EMAIL = "info@fotoromaimmobiliare.it"

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CONTACTS_FILES = [
    os.path.join(DATA_DIR, "airbnb_hosts_massive_3500.csv"),
    os.path.join(DATA_DIR, "prospects_southern_lazio.csv"),
    os.path.join(DATA_DIR, "enriched_contacts.csv")
]
LOG_FILE = os.path.join(DATA_DIR, "contacted_log.csv")
UNSUBSCRIBE_FILE = os.path.join(DATA_DIR, "unsubscribed.csv")

LOGO_PATH = "/Users/antoniopicariello/Desktop/Repo/FotoRomaImmobiliare/public/logo_fotoroma_perfect_green.png"
with open(LOGO_PATH, "rb") as f:
    LOGO_B64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"

PM_IMAGES = [
    "https://fotoromaimmobiliare.it/hero_airbnb_pm.jpg",
    "https://fotoromaimmobiliare.it/hero_pm/008%20-%20antoniopicariello.it%20-%20via%20candia%2065_-Modifica.jpg",
    "https://fotoromaimmobiliare.it/hero_pm/038%20-%20antoniopicariello.it%20-%203343089759%20-%20%20Via%20Capo%20d%27Africa%2015_.jpg",
    "https://fotoromaimmobiliare.it/hero_pm/218%20-%20antoniopicariello.it%20-%203343089759%20-%20%20Bea%20Suites_-2.jpg"
]

AGENCY_IMAGES = [
    "https://fotoromaimmobiliare.it/hero_agency/ZZ6_8894.jpg",
    "https://fotoromaimmobiliare.it/hero_agency/ZZ6_8893-2-2.jpg",
    "https://fotoromaimmobiliare.it/hero_agency/DSC_1225.jpg",
    "https://fotoromaimmobiliare.it/hero_agency/DSC_1200.jpg",
    "https://fotoromaimmobiliare.it/hero_agency/DSC_2022-HDR-2.jpg"
]

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
    
    if is_pm:
        badge = "AIRBNB · B&B · PROPERTY MANAGEMENT"
        hero_img = random.choice(PM_IMAGES)
        subject = f"Presentazione annunci e valorizzazione per gli alloggi a {city}"
        hook_question = f"Lo sapevate che l'80% degli ospiti su Airbnb decide se aprire un annuncio nei primi 3 secondi solo per via della prima foto?"
        intro = f"Negli affitti brevi le foto non servono solo a mostrare la casa: servono ad <strong>alzare il prezzo medio per notte</strong>, aumentare le prenotazioni dirette ed evitare contestazioni al check-in."
        points = [
            ("Fotografia d'Interni per Airbnb (80 € / 150 €)", "Scatti luminosi ad alta definizione studiati per valorizzare gli spazi e i dettagli di accoglienza."),
            ("Virtual Tour 360° Matterport (290 €)", "Visita virtuale interattiva per permettere agli ospiti di esplorare l'alloggio prima di prenotare."),
            ("Video Reportage 4K & Drone", "Walkthrough completi e riprese aeree per alloggi di pregio e promozioni social."),
            ("Consegna Rapida in 72h dal pagamento", "Tutti i file consegnati già calibrati per Airbnb, Booking e Vrbo, pronti per essere caricati subito.")
        ]
        whatsapp_msg = f"Ciao,%20ti%20contatto%20dall%27email%20di%20FotoRomaImmobiliare.it,%20vorrei%20informazioni%20per%20un%20servizio%20fotografico%20a%20{city}"
    else:
        badge = "STUDIO FOTOGRAFICO IMMOBILIARE"
        hero_img = random.choice(AGENCY_IMAGES)
        subject = f"Qualificazione visite e annunci per le agenzie di {zone if zone else city}"
        hook_question = f"Quante visite a vuoto fate ogni mese con persone che poi dicono: 'Ah, ma dalle foto sembrava un'altra cosa'?"
        intro = f"Il vero costo delle foto amatoriali o ingannevoli è il vostro tempo. Una fotografia professionale serve a <strong>filtrare i curiosi a monte</strong> e portare all'appuntamento solo acquirenti pronti a fare una proposta seria."
        points = [
            ("Servizio Fotografico Full a 150 €", "Foto professionali d'interni ed esterni <strong>illimitate</strong> in alta definizione, per coprire ogni singolo ambiente."),
            ("Virtual Tour 360° Matterport (290 €)", "Scansione 3D interattiva per qualificare acquirenti fuori sede ed esteri prima di fissare il sopralluogo."),
            ("Video Reportage 4K & Riprese Drone (150 €)", "Video emozionali e riprese aeree per dare massimo risalto agli annunci di fascia alta."),
            ("Consegna in 72h dal pagamento", "Tutti i file consegnati già calibrati per i principali portali immobiliari e sito di agenzia.")
        ]
        whatsapp_msg = f"Ciao,%20ti%20contatto%20dall%27email%20di%20FotoRomaImmobiliare.it,%20vorrei%20informazioni%20per%20un%20servizio%20fotografico%20a%20{zone if zone else city}"

    items_html = ""
    for title, desc in points:
        items_html += f"""
        <tr>
          <td style="padding-bottom: 14px;">
            <table border="0" cellpadding="0" cellspacing="0" width="100%">
              <tr>
                <td width="22" valign="top" style="padding-top: 2px;">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#87C054" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display: block;">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                </td>
                <td style="padding-left: 8px; color: #B5B7AB; font-size: 13px; line-height: 1.55;">
                  <strong style="color: #87C054; font-weight: 700;">{title}:</strong> {desc}
                </td>
              </tr>
            </table>
          </td>
        </tr>
        """

    auto_unsub_url = f"https://fotoromaimmobiliare.it/disiscrizione?email={urllib.parse.quote(recipient_email)}"
    prezzi_url = "https://fotoromaimmobiliare.it/prezzi-fotografo-immobiliare-roma"
    tracking_pixel_url = f"https://fotoromaimmobiliare.it/assets/logo.png?trk={urllib.parse.quote(recipient_email)}&cat={category_code}&t={int(time.time())}"

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="format-detection" content="telephone=no, date=no, address=no, email=no, url=no">
  <title>FotoRomaImmobiliare</title>
</head>
<body style="margin: 0; padding: 24px 0; background-color: #24262A; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #F7F8E2; -webkit-font-smoothing: antialiased;">
  
  <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 580px; background-color: #33353B; border-radius: 20px; overflow: hidden; margin: 0 auto; border: 1px solid #484B52; box-shadow: 0 16px 36px rgba(0,0,0,0.45);">
    
    <!-- HEADER BRAND (LOGO ORIGINALE INGRANDITO) -->
    <tr>
      <td align="center" style="padding: 20px 20px 14px 20px; background-color: #282A2E; border-bottom: 1px solid #42454B;">
        <img src="{LOGO_B64}" alt="FotoRomaImmobiliare" style="height: 82px; max-height: 82px; width: auto; display: block; margin: 0 auto 6px auto;" />
        <p style="margin: 0; color: #F7F8E2; font-size: 11px; letter-spacing: 2px; text-transform: uppercase; font-weight: 700;">FOTO • VIDEO • VIRTUAL TOUR PER IMMOBILI</p>
      </td>
    </tr>

    <!-- HERO IMAGE ROTANTE -->
    <tr>
      <td style="padding: 0;">
        <img src="{hero_img}" alt="Photography Roma" style="width: 100%; max-height: 240px; object-fit: cover; display: block;" />
      </td>
    </tr>

    <!-- CONTENUTO PRINCIPALE -->
    <tr>
      <td style="padding: 28px 26px 24px 26px;">
        
        <!-- BADGE -->
        <p style="margin: 0 0 10px 0; color: #87C054; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px;">
          {badge}
        </p>

        <!-- GANCIO FORTE / TITOLO -->
        <h1 style="margin: 0 0 14px 0; color: #F7F8E2; font-size: 20px; font-weight: 800; line-height: 1.35;">
          {hook_question}
        </h1>
        
        <!-- INTRO -->
        <p style="margin: 0 0 22px 0; color: #B5B7AB; font-size: 13.5px; line-height: 1.6;">
          {intro}
        </p>

        <!-- CARD SERVIZI -->
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #2B2D31; border-radius: 14px; border: 1px solid #42454B; margin-bottom: 24px;">
          <tr>
            <td style="padding: 20px 18px 6px 18px;">
              <table border="0" cellpadding="0" cellspacing="0" width="100%">
                {items_html}
              </table>
            </td>
          </tr>
        </table>

        <!-- CTA WHATSAPP -->
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%">
          <tr>
            <td align="center" style="padding-bottom: 12px;">
              <a href="https://wa.me/393343089759?text={whatsapp_msg}" target="_blank" style="display: inline-block; background-color: #87C054; color: #1E2024; font-weight: 700; font-size: 14px; text-decoration: none; padding: 13px 32px; border-radius: 9px; box-shadow: 0 4px 14px rgba(135, 192, 84, 0.3); white-space: nowrap;">
                Richiedi disponibilità su WhatsApp ➔
              </a>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding-bottom: 6px;">
              <p style="margin: 0; color: #9A9C91; font-size: 12px;">Oppure chiama: <strong>+39 334 308 9759</strong></p>
            </td>
          </tr>
          <tr>
            <td align="center">
              <a href="{prezzi_url}" target="_blank" style="color: #B5B7AB; font-size: 11px; text-decoration: underline;">
                Consulta il listino prezzi ufficiale su fotoromaimmobiliare.it
              </a>
            </td>
          </tr>
        </table>

      </td>
    </tr>

    <!-- FOOTER ISTITUZIONALE & GDPR COMPLIANCE AUTOMATICO -->
    <tr>
      <td align="center" style="padding: 20px 24px; background-color: #26282C; border-top: 1px solid #42454B; color: #7F8177; font-size: 11px; line-height: 1.5;">
        <p style="margin: 0 0 4px 0; font-weight: 600; color: #B5B7AB;">FotoRomaImmobiliare • di Antonio Picariello</p>
        <p style="margin: 0 0 4px 0;">Via Filippo Cremonesi 8, 00155 Roma • P.IVA 15883601002 • Consegna in 72h dal pagamento</p>
        <p style="margin: 0 0 12px 0;">Fotografia d'interni, Video 4K, Drone e Virtual Tour 360° per compravendite e alloggi turistici.</p>
        
        <div style="border-top: 1px solid #383A3F; padding-top: 10px; font-size: 10px; color: #6D6F66; text-align: center;">
          <p style="margin: 0 0 4px 0;">
            <em>Ricevi questa comunicazione informativa B2B in quanto la tua struttura o agenzia è presente su elenchi pubblici, portali di settore o registri di categoria.</em>
          </p>
          <p style="margin: 0;">
            Se non desideri più ricevere aggiornamenti o proposte, <a href="{auto_unsub_url}" target="_blank" style="color: #87C054; text-decoration: underline;">clicca qui per disiscriverti automaticamente con 1 click</a>.
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

