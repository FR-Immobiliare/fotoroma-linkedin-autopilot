#!/usr/bin/env python3
"""
FotoRomaImmobiliare — B2B Direct Conversion Engine (Exact Website UI Clone)
Replica fedele dei componenti grafici del sito:
- Background card: #2F3136 (con raggio 24px e bordo 1px)
- Titoli dei punti: VERDE BRAND #87C054 (come sul sito)
- Spunta Checkmark SVG verde
- Pulsante CTA compatto su una sola riga: "Richiedi disponibilità su WhatsApp"
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

def build_html_template(target_type, name, zone, city):
    if target_type == "PROPERTY_MANAGER":
        badge = "AIRBNB · B&B · AFFITTI BREVI"
        subject = f"Presentazione annunci e valorizzazione per gli immobili a {city}"
        headline = f"Come massimizzare il prezzo per notte a {city}?"
        intro = f"Negli affitti brevi gli ospiti decidono in 3 secondi: immagini luminose e curate aumentano le prenotazioni dirette, proteggono il prezzo medio per notte ed evitano contestazioni al check-in."
        points = [
            ("Aumento del Prezzo Medio (ADR)", "La percezione di cura e pulizia riduce le resistenze sul prezzo anche in bassa stagione."),
            ("Ottimizzazione per Portali OTA", "File con risoluzione e proporzioni calibrate per risaltare su Airbnb, Booking e Vrbo."),
            ("Consegna Rapida in 72h dal pagamento", "Per mettere online l'alloggio senza perdere notti d'incasso."),
            ("Servizio Fotografico Dedicato", "Pacchetto Basic da 80 € (20 foto) o Full senza limiti a 150 €.")
        ]
        whatsapp_msg = "Ciao%20Antonio,%20vorrei%20informazioni%20per%20un%20servizio%20fotografico%20per%20affitti%20brevi"
    else:
        badge = "AGENZIE · PROPERTY MANAGER · COMPRAVENDITA"
        subject = f"Qualificazione visite per i vostri annunci a {zone if zone else city}"
        headline = f"Meno sopralluoghi a vuoto, contatti più qualificati."
        intro = f"Il problema più frequente negli annunci a {city} è il tempo perso in visite con curiosi o persone che restano deluse dal vivo. Le foto professionali servono a <strong>filtrare a monte</strong> e portare in visita solo acquirenti pronti a fare una proposta seria."
        points = [
            ("Zero 'Turisti Immobiliari'", "Chi contatta l'agenzia ha già compreso spazi e luce reale, eliminando le obiezioni durante il sopralluogo."),
            ("Protezione del Valore di Vendita", "Una presentazione impeccabile evita che l'immobile rimanga fermo sui portali e subisca trattative al ribasso."),
            ("Servizio Fotografico Full a 150 €", "Copertura completa dell'immobile con foto illimitate in alta definizione, senza costi nascosti."),
            ("Virtual Tour 360° & Video 4K", "La soluzione ideale per qualificare acquirenti esteri e fuori sede prima della visita.")
        ]
        whatsapp_msg = f"Ciao%20Antonio,%20vorrei%20informazioni%20per%20un%20servizio%20fotografico%20a%20{zone if zone else city}"

    # Genera i punti con la spunta SVG verde e il titolo verde come sul sito
    items_html = ""
    for title, desc in points:
        items_html += f"""
        <tr>
          <td style="padding-bottom: 14px;">
            <table border="0" cellpadding="0" cellspacing="0" width="100%">
              <tr>
                <td width="22" valign="top" style="padding-top: 2px;">
                  <!-- Checkmark icon identica a Lucide Check -->
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

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FotoRomaImmobiliare</title>
</head>
<body style="margin: 0; padding: 24px 0; background-color: #24262A; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #F7F8E2; -webkit-font-smoothing: antialiased;">
  
  <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 580px; background-color: #33353B; border-radius: 20px; overflow: hidden; margin: 0 auto; border: 1px solid #484B52; box-shadow: 0 16px 36px rgba(0,0,0,0.45);">
    
    <!-- HEADER BRAND -->
    <tr>
      <td align="center" style="padding: 24px 20px 18px 20px; background-color: #282A2E; border-bottom: 1px solid #42454B;">
        <img src="https://fotoromaimmobiliare.it/assets/logo-jjOiLsXH.png" alt="FotoRomaImmobiliare" style="max-height: 42px; width: auto; display: block; margin-bottom: 6px;" />
        <p style="margin: 0; color: #9A9C91; font-size: 10.5px; letter-spacing: 1.8px; text-transform: uppercase; font-weight: 600;">Studio Fotografico Immobiliare • Roma</p>
      </td>
    </tr>

    <!-- HERO IMAGE -->
    <tr>
      <td style="padding: 0;">
        <img src="https://fotoromaimmobiliare.it/assets/hero-interior-DPt5TKqx.jpg" alt="Interior Photography Roma" style="width: 100%; max-height: 230px; object-fit: cover; display: block;" />
      </td>
    </tr>

    <!-- CONTENUTO PRINCIPALE -->
    <tr>
      <td style="padding: 28px 26px 24px 26px;">
        
        <!-- BADGE VERDE COME SUL SITO -->
        <p style="margin: 0 0 10px 0; color: #87C054; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px;">
          {badge}
        </p>

        <h1 style="margin: 0 0 14px 0; color: #F7F8E2; font-size: 20px; font-weight: 700; line-height: 1.35;">
          {headline}
        </h1>
        
        <p style="margin: 0 0 22px 0; color: #B5B7AB; font-size: 13.5px; line-height: 1.6;">
          {intro}
        </p>

        <!-- CARD 3D IDENTICA AL SITO -->
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #2B2D31; border-radius: 14px; border: 1px solid #42454B; margin-bottom: 24px;">
          <tr>
            <td style="padding: 20px 18px 6px 18px;">
              <table border="0" cellpadding="0" cellspacing="0" width="100%">
                {items_html}
              </table>
            </td>
          </tr>
        </table>

        <!-- PULSANTE CTA DIRETTA WHATSAPP COMPATTO -->
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%">
          <tr>
            <td align="center" style="padding-bottom: 12px;">
              <a href="https://wa.me/393343089759?text={whatsapp_msg}" target="_blank" style="display: inline-block; background-color: #87C054; color: #1E2024; font-weight: 700; font-size: 14px; text-decoration: none; padding: 13px 32px; border-radius: 9px; box-shadow: 0 4px 14px rgba(135, 192, 84, 0.3); white-space: nowrap;">
                Scrivici su WhatsApp ➔
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
              <a href="https://fotoromaimmobiliare.it" target="_blank" style="color: #B5B7AB; font-size: 11px; text-decoration: underline;">
                fotoromaimmobiliare.it
              </a>
            </td>
          </tr>
        </table>

      </td>
    </tr>

    <!-- FOOTER -->
    <tr>
      <td align="center" style="padding: 18px 24px; background-color: #26282C; border-top: 1px solid #42454B; color: #7F8177; font-size: 11px; line-height: 1.5;">
        <p style="margin: 0 0 3px 0; font-weight: 600; color: #B5B7AB;">FotoRomaImmobiliare • di Antonio Picariello</p>
        <p style="margin: 0 0 3px 0;">Via Filippo Cremonesi 8, 00155 Roma • Consegna in 72h dal pagamento</p>
        <p style="margin: 0;">Servizi fotografici professionali per il Real Estate a Roma, Napoli e Firenze.</p>
      </td>
    </tr>

  </table>

</body>
</html>
"""
    return subject, html

