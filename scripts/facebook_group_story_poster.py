#!/usr/bin/env python3
"""
FotoRomaImmobiliare — Facebook Group Organic Storytelling Engine
Genera post narrativi ad altissimo engagement per gruppi di Host Airbnb e Agenti,
con foto caricate in galleria e copy basato sul metodo 'Caso Studio Reale'.
"""

import os
import random
from datetime import datetime

STORIES = [
    {
        "title": "🏠 'Abbiamo rifatto l'arredo da zero, ma su Airbnb non arrivano le prenotazioni che speravamo.'",
        "intro": "Quando Marco ci ha chiamato per il suo alloggio a Roma, era perplesso:\n\"L'appartamento è impeccabile, chi soggiorna lascia sempre recensioni a 5 stelle, ma nei risultati di ricerca la gente scorre oltre senza cliccare.\"",
        "problem": "È una situazione che vediamo spessissimo:\nSi investono mesi di lavoro e migliaia di euro per curare finiture, materassi di pregio e dettagli d'arredo... poi l'annuncio viene affidato a foto scattate velocemente con il telefono, che appiattiscono la luce e non rendono giustizia alla reale metratura.",
        "solution": "📸 Abbiamo realizzato un servizio fotografico grandangolare calibrato per i portali OTA, valorizzando sia la spazialità degli ambienti sia i dettagli di accoglienza che fanno scattare la decisione nei primi 3 secondi.",
        "outcome": "💡 Risultato: l'annuncio risalta subito nelle ricerche, aumenta il tasso di prenotazione diretta e protegge il prezzo medio per notte anche nei mesi di bassa stagione.",
        "cta": "🔑 Gestisci una casa vacanze, un B&B o un appartamento per affitti brevi a Roma, nel Golfo di Gaeta o nel Lazio e vuoi valorizzarlo al meglio?\nScrivimi qui in privato nei messaggi o su WhatsApp al +39 334 308 9759.\n\n🌐 Guarda il portfolio e listino completo: https://fotoromaimmobiliare.it",
        "photos": [
            "https://fotoromaimmobiliare.it/hero_airbnb_pm.jpg",
            "https://fotoromaimmobiliare.it/hero_pm/008%20-%20antoniopicariello.it%20-%20via%20candia%2065_-Modifica.jpg",
            "https://fotoromaimmobiliare.it/hero_pm/038%20-%20antoniopicariello.it%20-%203343089759%20-%20%20Via%20Capo%20d%27Africa%2015_.jpg",
            "https://fotoromaimmobiliare.it/hero_pm/218%20-%20antoniopicariello.it%20-%203343089759%20-%20%20Bea%20Suites_-2.jpg"
        ]
    }
]

def generate_ready_post():
    s = STORIES[0]
    post_text = f"{s['title']}\n\n{s['intro']}\n\n{s['problem']}\n\n{s['solution']}\n\n{s['outcome']}\n\n{s['cta']}"
    
    # Salva il testo pronto per copia/incolla o pubblicazione automatica
    output_path = "/Users/antoniopicariello/Desktop/POST_PRONTO_PER_GRUPPO_FACEBOOK.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(post_text)
    
    return post_text, s["photos"], output_path

if __name__ == "__main__":
    text, photos, path = generate_ready_post()
    print("✅ POST GENERATO PER IL GRUPPO FACEBOOK:")
    print("="*60)
    print(text)
    print("="*60)
    print(f"👉 File salvato sulla Scrivania: {path}")
