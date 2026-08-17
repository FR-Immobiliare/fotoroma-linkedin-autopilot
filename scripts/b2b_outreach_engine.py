#!/usr/bin/env python3
"""
FotoRomaImmobiliare — B2B Direct Conversion Engine
CTA diretta a WhatsApp / Contatto per massimizzare le conversioni immediate.
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
    """
    Template ad altissima conversione con CTA diretta verso WhatsApp / Chiamata.
    """
    
    if target_type == "PROPERTY_MANAGER":
        badge = "AIRBNB & PROPERTY MANAGEMENT"
        subject = f"Presentazione annunci e valorizzazione per gli immobili a {city}"
        headline = f"Come massimizzare il prezzo per notte a {city}?"
        intro = f"Negli affitti brevi gli ospiti decidono in 3 secondi: immagini luminose e curate aumentano le prenotazioni dirette, proteggono il prezzo medio per notte ed evitano contestazioni al check-in."
        points = [
            ("Aumento del Prezzo Medio (ADR)", "La percezione di cura e pulizia riduce le resistenze sul prezzo anche in bassa stagione."),
            ("Ottimizzazione Algoritmi OTA", "File con risoluzione e luce calibrate per risaltare su Airbnb, Booking e Vrbo."),
            ("Consegna Rapida in 72 Ore", "Dal pagamento alla consegna dei file, per mettere online l'alloggio senza perdere notti d'incasso."),
            ("Tariffe Trasparenti", "Pacchetto Basic Airbnb da 80 € (20 foto) o Full senza limiti a 150 €.")
        ]
        whatsapp_msg = "Ciao%20Antonio,%20vorrei%20informazioni%20per%20un%20servizio%20fotografico%20per%20affitti%20brevi"
        cta_main = "💬 SCRIVICI SU WHATSAPP"
        cta_sub = "Risposta diretta in pochi minuti"
    else:
        badge = "QUALIFICAZIONE ANNUNCI & VISITE"
        subject = f"Presentazione e qualificazione visite per i vostri annunci a {zone if zone else city}"
        headline = f"Meno sopralluoghi a vuoto, contatti più qualificati."
        intro = f"Il problema più frequente negli annunci a {city} è il tempo perso in visite con curiosi o acquirenti che restano delusi dal vivo. Una fotografia professionale serve a <strong>filtrare a monte</strong> e portare all'appuntamento solo chi è pronto a fare una proposta."
        points = [
            ("Zero 'Turisti Immobiliari'", "Chi contatta l'agenzia ha già compreso spazi e luce reale, eliminando le obiezioni durante la visita."),
            ("Protezione del Valore di Vendita", "Una presentazione impeccabile evita che l'immobile rimanga fermo sui portali e subisca trattative al ribasso."),
            ("Servizio Fotografico Full a 150 €", "Copertura completa dell'immobile con foto illimitate in alta definizione, senza costi nascosti."),
            ("Virtual Tour 360° & Video 4K", "La soluzione ideale per qualificare acquirenti fuori sede ed esteri prima della visita.")
        ]
        whatsapp_msg = f"Ciao%20Antonio,%20vorrei%20fissare%20uno%20shooting%20o%20avere%20info%20per%20un%20immobile%20a%20{zone if zone else city}"
        cta_main = "💬 RICHIEDI DISPONIBILITÀ SU WHATSAPP"
        cta_sub = "Oppure chiama direttamente: +39 334 308 9759"

    items_html = ""
    for title, desc in points:
        items_html += f"""
        <tr>
          <td style="padding-bottom: 15px;">
            <table border="0" cellpadding="0" cellspacing="0" width="100%">
              <tr>
                <td width="18" valign="top" style="color: #88C253; font-size: 14px; line-height: 1.5; font-weight: bold;">•</td>
                <td style="padding-left: 8px; color: #D8D9CF; font-size: 13px; line-height: 1.6;">
                  <strong style="color: #F5F6E8; font-weight: 600;">{title}:</strong> {desc}
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
<body style="margin: 0; padding: 20px 0; background-color: #222428; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #F5F6E8; -webkit-font-smoothing: antialiased;">
  
  <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 580px; background-color: #2E3035; border-radius: 14px; overflow: hidden; margin: 0 auto; border: 1px solid #44474E; box-shadow: 0 12px 30px rgba(0,0,0,0.35);">
    
    <!-- HEADER -->
    <tr>
      <td align="center" style="padding: 24px 20px 18px 20px; background-color: #26282C; border-bottom: 1px solid #3F4248;">
        <img src="https://fotoromaimmobiliare.it/assets/logo-jjOiLsXH.png" alt="FotoRomaImmobiliare" style="max-height: 42px; width: auto; display: block; margin-bottom: 6px;" />
        <p style="margin: 0; color: #9E9F97; font-size: 10px; letter-spacing: 1.8px; text-transform: uppercase; font-weight: 600;">Studio Fotografico Immobiliare • Roma</p>
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
      <td style="padding: 28px 28px 24px 28px;">
        
        <!-- BADGE -->
        <div style="display: inline-block; padding: 4px 10px; background-color: rgba(136, 194, 83, 0.12); border: 1px solid rgba(136, 194, 83, 0.3); border-radius: 6px; margin-bottom: 14px;">
          <span style="color: #88C253; font-size: 10px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;">{badge}</span>
        </div>

        <h1 style="margin: 0 0 14px 0; color: #F5F6E8; font-size: 20px; font-weight: 700; line-height: 1.35; letter-spacing: -0.2px;">
          {headline}
        </h1>
        
        <p style="margin: 0 0 22px 0; color: #C2C3BA; font-size: 13.5px; line-height: 1.65;">
          {intro}
        </p>

        <!-- CARD BENEFICI -->
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #26282C; border-radius: 10px; border: 1px solid #3F4248; margin-bottom: 24px;">
          <tr>
            <td style="padding: 20px 18px 5px 18px;">
              <table border="0" cellpadding="0" cellspacing="0" width="100%">
                {items_html}
              </table>
            </td>
          </tr>
        </table>

        <!-- CTA DIRETTA A WHATSAPP / CONTATTO -->
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%">
          <tr>
            <td align="center" style="padding-bottom: 10px;">
              <a href="https://wa.me/393343089759?text={whatsapp_msg}" target="_blank" style="display: inline-block; background-color: #88C253; color: #1C1E22; font-weight: 800; font-size: 14px; text-decoration: none; padding: 14px 32px; border-radius: 8px; box-shadow: 0 4px 15px rgba(136, 194, 83, 0.35); letter-spacing: 0.3px;">
                {cta_main}
              </a>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding-bottom: 8px;">
              <p style="margin: 0; color: #9E9F97; font-size: 12px;">{cta_sub}</p>
            </td>
          </tr>
          <tr>
            <td align="center">
              <a href="https://fotoromaimmobiliare.it" target="_blank" style="color: #B5B7AB; font-size: 11.5px; text-decoration: underline;">
                Visita il sito web ufficiale: fotoromaimmobiliare.it
              </a>
            </td>
          </tr>
        </table>

      </td>
    </tr>

    <!-- FOOTER -->
    <tr>
      <td align="center" style="padding: 18px 24px; background-color: #242529; border-top: 1px solid #3F4248; color: #7F8177; font-size: 11px; line-height: 1.5;">
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

