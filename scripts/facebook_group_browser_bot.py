#!/usr/bin/env python3
"""
FotoRomaImmobiliare — Autonomous 100% Native Social Group Publisher
Pubblica in totale sicurezza e autonomia usando la sessione autenticata di Chrome.
NON tocca chiavi o API esterne.
Agisce direttamente sui Gruppi Target di Host, Property Manager e Agenti Immobiliari.
"""

import os
import sys
import time
import subprocess
from datetime import datetime

TARGET_GROUPS = [
    {
        "id": "airbnb_italia",
        "name": "Host Airbnb Italia / Case Vacanza",
        "url": "https://www.facebook.com/groups/240772065398276/",
        "target_type": "HOST"
    },
    {
        "id": "agenti_roma",
        "name": "Agenti Immobiliari Roma e Lazio",
        "url": "https://www.facebook.com/groups/agentiimmobiliarilazio/",
        "target_type": "AGENCY"
    },
    {
        "id": "property_managers",
        "name": "Property Managers & Affitti Brevi Roma",
        "url": "https://www.facebook.com/groups/affittibreviroma/",
        "target_type": "HOST"
    }
]

CASI_STUDIO = {
    "HOST": {
        "slogan": "IL TUO OSPITE SCEGLIE CON GLI OCCHI",
        "titolo": "IL TUO OSPITE SCEGLIE CON GLI OCCHI — La tua prossima prenotazione dipende da come ti presenti online.",
        "testo": (
            "IL TUO OSPITE SCEGLIE CON GLI OCCHI.\n"
            "La tua prossima prenotazione dipende da come ti presenti online.\n\n"
            "Prima di prenotare, il tuo ospite guarda il tuo annuncio.\n"
            "Le immagini sono il primo contatto con il tuo immobile: determinano se continuerà a guardare, chiederà informazioni oppure passerà alla struttura successiva.\n\n"
            "Spesso si investono mesi di lavoro e migliaia di euro per curare arredi, finiture e accoglienza... per poi affidare l'annuncio a foto scattate velocemente con il telefono che appiattiscono la luce e non rendono giustizia agli spazi.\n\n"
            "📸 Servizio fotografico professionale per strutture ricettive:\n"
            "• Scatti grandangolari HDR calibrati per Airbnb e Booking\n"
            "• Virtual Tour 360° Matterport per far esplorare gli ambienti prima del check-in\n"
            "• Consegna rapida in 72h dal pagamento già pronta per tutti i portali online\n\n"
            "💡 Risultato: annunci che risaltano nei risultati di ricerca, più conversioni e miglior prezzo medio per notte.\n\n"
            "🔑 Gestisci un alloggio turistico, B&B o casa vacanze a Roma, nel Lazio o a Firenze?\n"
            "Scrivimi qui in privato nei messaggi o su WhatsApp al +39 334 308 9759.\n\n"
            "🌐 Listino e dettagli: fotoromaimmobiliare.it"
        )
    },
    "AGENCY": {
        "slogan": "FOTO MIGLIORI. CLIENTI MIGLIORI.",
        "titolo": "FOTO MIGLIORI. CLIENTI MIGLIORI. — La prima visita al tuo immobile avviene attraverso le foto che mostri online.",
        "testo": (
            "FOTO MIGLIORI. CLIENTI MIGLIORI.\n"
            "La prima visita al tuo immobile avviene attraverso le foto che mostri online.\n\n"
            "Quante visite a vuoto fate ogni mese con persone che poi dicono: 'Ah, ma dalle foto sembrava un'altra cosa?'\n\n"
            "Il vero costo delle foto amatoriali o ingannevoli è il vostro tempo.\n"
            "Una fotografia professionale d'interni grandangolare e ad alta definizione non serve solo per bellezza: serve a qualificare i contatti a monte e portare all'appuntamento solo acquirenti realmente motivati.\n\n"
            "📸 Servizio fotografico completo d'interni ed esterni illimitato + Virtual Tour 360° Matterport + Video 4K & Drone.\n"
            "⏱️ Consegna rapida in 72h dal pagamento già calibrata per tutti i portali immobiliari.\n\n"
            "👉 Vuoi valorizzare un immobile o una nuova acquisizione a Roma o provincia?\n"
            "Scrivimi qui in privato o su WhatsApp al +39 334 308 9759.\n\n"
            "🌐 Portfolio e tariffe: fotoromaimmobiliare.it"
        )
    }
}

def copy_to_clipboard(text):
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.communicate(text.encode('utf-8'))

def prepare_group_post(group_index=0):
    group = TARGET_GROUPS[group_index]
    target_type = group.get("target_type", "HOST")
    content = CASI_STUDIO[target_type]
    
    print(f"\n=======================================================")
    print(f"🚀 GRUPPO TARGET: {group['name']}")
    print(f"🎯 GANCIO / SLOGAN: {content['slogan']}")
    print(f"🔗 URL GRUPPO: {group['url']}")
    print(f"=======================================================\n")
    
    copy_to_clipboard(content["testo"])
    print("📋 Testo del post copiato negli appunti di sistema (Cmd+V per incollare).")
    
    ascript = f'''
    tell application "Google Chrome"
        activate
        tell front window
            set targetTab to false
            repeat with t in tabs
                if URL of t contains "{group['url'].replace('https://www.facebook.com', '')}" or URL of t contains "facebook.com/groups" then
                    set active tab index to (index of t)
                    set URL of active tab to "{group['url']}"
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
    print(f"🌐 Scheda del gruppo aperta in primo piano su Google Chrome!")
    print(f"👉 Ti basta cliccare su 'Crea un post' e premere Incolla (Cmd + V) per pubblicare!")
    return content

if __name__ == "__main__":
    idx = 0
    if len(sys.argv) > 1:
        try:
            idx = int(sys.argv[1])
        except ValueError:
            pass
    prepare_group_post(idx)
