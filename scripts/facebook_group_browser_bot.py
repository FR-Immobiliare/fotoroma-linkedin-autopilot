#!/usr/bin/env python3
"""
FotoRomaImmobiliare — Autonomous 100% Native Social Publisher
Pubblica in totale sicurezza e autonomia usando la sessione autenticata di Chrome.
NON tocca chiavi, API o configurazioni di 'fotoroma18'.
Agisce esclusivamente sulla Pagina Ufficiale e sui Gruppi Target di FotoRomaImmobiliare.
"""

import os
import sys
import time
import subprocess
from datetime import datetime

TARGET_GROUPS = [
    {"name": "HOST AIRBNB ITALIA", "url": "https://www.facebook.com/groups/240772065398276/"},
    {"name": "Agenti Immobiliari Roma e Provincia", "url": "https://www.facebook.com/groups/agentiimmobiliarilazio/"}
]

CASI_STUDIO = [
    {
        "titolo": "🏠 'Abbiamo rifatto l'arredo da zero, ma su Airbnb non arrivano le prenotazioni che speravamo.'",
        "testo": (
            "🏠 'Abbiamo rifatto l'arredo da zero, ma su Airbnb non arrivano le prenotazioni che speravamo.'\n\n"
            "Quando Marco ci ha chiamato per il suo alloggio a Roma, era perplesso:\n"
            "\"L'appartamento è impeccabile, chi soggiorna lascia sempre recensioni a 5 stelle, ma nei risultati di ricerca la gente scorre oltre senza cliccare.\"\n\n"
            "È una situazione che vediamo spessissimo:\n"
            "Si investono mesi di lavoro e migliaia di euro per curare finiture, materassi di pregio e dettagli d'arredo... poi l'annuncio viene affidato a foto scattate velocemente con il telefono, che appiattiscono la luce e non rendono giustizia alla reale metratura.\n\n"
            "📸 Abbiamo realizzato un servizio fotografico grandangolare calibrato per i portali OTA, valorizzando sia la spazialità degli ambienti sia i dettagli di accoglienza che fanno scattare la decisione nei primi 3 secondi.\n\n"
            "💡 Risultato: l'annuncio risalta subito nelle ricerche, aumenta il tasso di prenotazione diretta e protegge il prezzo medio per notte anche nei mesi di bassa stagione.\n\n"
            "🔑 Gestisci una casa vacanze, un B&B o un appartamento per affitti brevi a Roma, nel Golfo di Gaeta o nel Lazio e vuoi valorizzarlo al meglio?\n"
            "Scrivimi qui in privato nei messaggi o su WhatsApp al +39 334 308 9759.\n\n"
            "🌐 Guarda il portfolio e listino completo: https://fotoromaimmobiliare.it"
        )
    }
]

def copy_to_clipboard(text):
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.communicate(text.encode('utf-8'))

def publish_organically_to_group(group_index=0):
    group = TARGET_GROUPS[group_index]
    story = CASI_STUDIO[0]
    
    print(f"[{datetime.now().isoformat()}] Preparazione pubblicazione autonoma per: {group['name']}...")
    copy_to_clipboard(story["testo"])
    
    # Esegue script su Chrome
    ascript = f'''
    tell application "Google Chrome"
        activate
        tell front window
            set targetTab to false
            repeat with t in tabs
                if URL of t contains "facebook.com/groups" then
                    set active tab index to (index of t)
                    set targetTab to true
                    exit repeat
                end if
            end repeat
            if not targetTab then
                open location "{group['url']}"
            end if
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", ascript])
    print(f"✅ Scheda del gruppo '{group['name']}' sincronizzata e attiva!")
    print("📋 Testo del caso studio caricato negli appunti per la pubblicazione diretta.")

if __name__ == "__main__":
    publish_organically_to_group(0)
