#!/usr/bin/env python3
"""
FotoRomaImmobiliare — B2B Personalized Outreach Engine (Brand Edition)
Genera email HTML con Brand Identity ufficiale e copy segmentato su misura per:
1. Agenzie Immobiliari di Compravendita
2. Property Manager & Gestori Affitti Brevi (Airbnb / Booking)
3. Architetti, Costruttori e Home Stager
"""

import os
import sys
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "fotoroma18@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS")
SENDER_DISPLAY = "Antonio Picariello | FotoRomaImmobiliare"
SENDER_EMAIL = "info@fotoromaimmobiliare.it"

CONTACTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "enriched_contacts.csv")
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "contacted_log.csv")

def get_already_contacted():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        return set(row[0] for row in reader if row)

def log_contact(email, agency_name, category, status):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([email, agency_name, category, datetime.now().isoformat(), status])

def build_html_template(target_type, name, zone, city):
    """
    Costruisce il template HTML nei colori ufficiali del brand (#3A3C42, #F7F8E2, #87C054)
    personalizzando testi, benefici e ganci in base alla categoria.
    """
    
    if target_type == "PROPERTY_MANAGER":
        tagline = "Ottimizzazione Annunci Airbnb & Booking"
        subject = f"Presentazione annunci e foto per gli immobili a {city}"
        hero_title = f"Come massimizzare il prezzo per notte dei vostri alloggi a {city}?"
        intro_text = f"Negli affitti brevi gli ospiti decidono in 3 secondi sullo schermo dello smartphone: foto luminose e spazi valorizzati aumentano le prenotazioni dirette ed evitano recensioni negative o contestazioni al check-in."
        benefits = [
            ("✓", "Aumenta l'ADR (Prezzo medio/notte):", "Annunci curati trasmettono fiducia, pulizia e cura, riducendo la resistenza sul prezzo."),
            ("✓", "File ottimizzati per OTA:", "Foto dimensionate e calibrate per l'algoritmo di Airbnb, Booking e Vrbo."),
            ("✓", "Consegna ultra-rapida in 72h dal pagamento:", "Metti online l'alloggio velocemente senza perdere notti di incasso."),
            ("✓", "Tariffe dedicate:", "Servizio Basic Airbnb da 80 € (20 foto editate) o Full senza limiti a 150 €.")
        ]
        cta_text = "VEDI IL PORTFOLIO AIRBNB ➔"
    else:
        # AGENZIA IMMOBILIARE / BROKER
        tagline = "Filtra i curiosi • Riduci i tempi di vendita"
        subject = f"Qualificazione visite per i vostri annunci a {zone if zone else city}"
        hero_title = f"Quanti sopralluoghi a vuoto fate ogni mese per annunci poco chiari?"
        intro_text = f"Il problema più frequente riscontrato con i colleghi agenti a {city} è il tempo perso in visite con curiosi o persone che restano deluse dal vivo. Le foto professionali servono a <strong>filtrare a monte</strong> e portare in visita solo acquirenti pronti a fare una proposta."
        benefits = [
            ("✓", "Zero perditempo in visita:", "Chi vi contatta ha già compreso spazi e luce reale, azzerando le obiezioni durante il sopralluogo."),
            ("✓", "Proteggi il valore dell'immobile:", "Immagini ad alto impatto evitano la svalutazione dell'annuncio e le continue trattative al ribasso."),
            ("✓", "Servizio Full a 150 € (Foto illimitate):", "Copertura completa di ogni ambiente, terrazzo ed esterno senza costi nascosti."),
            ("✓", "Virtual Tour 360° & Video 4K:", "Ideale per qualificare acquirenti esteri e fuori sede senza farli viaggiare per il primo appuntamento.")
        ]
        cta_text = "VEDI IL NOSTRO PORTFOLIO ➔"

    # Costruzione righe benefici HTML
    benefits_html = ""
    for icon, title, desc in benefits:
        benefits_html += f"""
        <tr>
          <td width="28" valign="top" style="color: #87C054; font-size: 18px; font-weight: 800; line-height: 1;">{icon}</td>
          <td style="padding-left: 10px; color: #F7F8E2; font-size: 13px; line-height: 1.5;">
            <strong style="color: #87C054;">{title}</strong> {desc}
          </td>
        </tr>
        <tr><td height="14"></td></tr>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FotoRomaImmobiliare</title>
</head>
<body style="margin: 0; padding: 0; background-color: #24262A; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #F7F8E2;">
  
  <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #3A3C42; border-radius: 18px; overflow: hidden; margin: 30px auto; border: 1px solid #4D5058; box-shadow: 0 14px 35px rgba(0,0,0,0.4);">
    
    <!-- HEADER BRAND -->
    <tr>
      <td align="center" style="padding: 26px 20px; background-color: #2C2E33; border-bottom: 1px solid #4D5058;">
        <img src="https://fotoromaimmobiliare.it/assets/logo-jjOiLsXH.png" alt="FotoRomaImmobiliare" style="max-height: 46px; width: auto; display: block; margin-bottom: 8px;" />
        <p style="margin: 0; color: #B5B7AB; font-size: 11px; letter-spacing: 2px; text-transform: uppercase; font-weight: 700;">Studio Fotografico Immobiliare • Roma</p>
      </td>
    </tr>

    <!-- HERO IMAGE -->
    <tr>
      <td style="padding: 0;">
        <img src="https://fotoromaimmobiliare.it/assets/hero-interior-DPt5TKqx.jpg" alt="Interior Photography Roma" style="width: 100%; max-height: 250px; object-fit: cover; display: block;" />
      </td>
    </tr>

    <!-- CORPO PRINCIPALE -->
    <tr>
      <td style="padding: 30px 28px 20px 28px;">
        
        <p style="margin: 0 0 12px 0; color: #87C054; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px;">
          {tagline}
        </p>

        <h2 style="margin: 0 0 16px 0; color: #F7F8E2; font-size: 21px; font-weight: 800; line-height: 1.3;">
          {hero_title}
        </h2>
        
        <p style="margin: 0 0 22px 0; color: #B5B7AB; font-size: 14px; line-height: 1.6;">
          {intro_text}
        </p>

        <!-- GRIGLIA VANTAGGI & BENEFICI -->
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #2C2E33; border-radius: 12px; border: 1px solid #4D5058; margin-bottom: 24px;">
          <tr>
            <td style="padding: 20px 18px;">
              <table border="0" cellpadding="0" cellspacing="0" width="100%">
                {benefits_html}
              </table>
            </td>
          </tr>
        </table>

        <!-- CTA BRAND BUTTON -->
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%">
          <tr>
            <td align="center" style="padding-bottom: 12px;">
              <a href="https://fotoromaimmobiliare.it/portfolio" target="_blank" style="display: inline-block; background-color: #87C054; color: #1E2024; font-weight: 800; font-size: 14px; text-decoration: none; padding: 14px 30px; border-radius: 8px; box-shadow: 0 4px 15px rgba(135, 192, 84, 0.35);">
                {cta_text}
              </a>
            </td>
          </tr>
          <tr>
            <td align="center">
              <a href="https://wa.me/393343089759?text=Ciao%20Antonio,%20ho%20ricevuto%20la%20mail%20per%20un%20servizio%20fotografico" target="_blank" style="color: #B5B7AB; font-size: 12px; text-decoration: underline;">
                Oppure richiedi disponibilità su WhatsApp (+39 334 308 9759)
              </a>
            </td>
          </tr>
        </table>

      </td>
    </tr>

    <!-- FOOTER COORDINATO -->
    <tr>
      <td align="center" style="padding: 22px 24px; background-color: #2C2E33; border-top: 1px solid #4D5058; color: #8A8D82; font-size: 11px; line-height: 1.5;">
        <p style="margin: 0 0 4px 0; font-weight: 700; color: #F7F8E2;">FotoRomaImmobiliare • di Antonio Picariello</p>
        <p style="margin: 0 0 4px 0;">Via Filippo Cremonesi 8, 00155 Roma • Tel / WhatsApp: +39 334 308 9759</p>
        <p style="margin: 0;">Servizi per Agenzie Immobiliari, Property Manager e Host Airbnb a Roma, Napoli e Firenze.</p>
      </td>
    </tr>

  </table>

</body>
</html>
"""
    return subject, html

if __name__ == "__main__":
    print("B2B Outreach Engine pronto con segmentazione dinamica per Agenzie e Property Manager.")
