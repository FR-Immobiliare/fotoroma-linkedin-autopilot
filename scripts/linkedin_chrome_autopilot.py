#!/usr/bin/env python3
"""
FotoRomaImmobiliare — LinkedIn Native Chrome Autopilot
Automatizza la pubblicazione tramite il browser Google Chrome (sessione utente già loggata).
Prende la prossima foto dalla coda, genera il copy persuasivo anti-curiosi e apre Chrome
pronto con il testo negli appunti e l'interfaccia di condivisione di LinkedIn.
"""

import os
import sys
import shutil
import subprocess
import time
from datetime import datetime
from auto_poster import get_next_photo, generate_copy_with_ai, PUBLISHED_DIR

def copy_to_clipboard(text):
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.communicate(text.encode('utf-8'))

def open_linkedin_in_chrome():
    ascript = '''
    tell application "Google Chrome"
        activate
        tell front window
            set targetTab to false
            repeat with t in tabs
                if URL of t contains "linkedin.com" then
                    set active tab index to (index of t)
                    set targetTab to true
                    exit repeat
                end if
            end repeat
            if not targetTab then
                open location "https://www.linkedin.com/feed/?shareActive=true"
            end if
        end tell
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", ascript], check=True)
        print("✅ LinkedIn aperto/attivato in Google Chrome!")
    except Exception as e:
        print(f"⚠️ Impossibile attivare Chrome via AppleScript: {e}")
        print("🌐 Apertura generica URL...")
        subprocess.run(["open", "https://www.linkedin.com/feed/?shareActive=true"])

def main():
    print("="*65)
    print(" 🚀 FotoRomaImmobiliare — LinkedIn Native Chrome Autopilot")
    print("="*65)
    
    photo = get_next_photo()
    if not photo:
        print("❌ Nessuna foto in coda in queue_photos/.")
        sys.exit(0)

    print(f"📸 Foto selezionata: {os.path.basename(photo)}")
    print("✍️ Generazione copy AI orientato ai benefici...")
    copy_text = generate_copy_with_ai(photo)
    
    print("\n" + "-"*65)
    print(copy_text)
    print("-" * 65 + "\n")
    
    print("📋 Caricamento testo negli appunti di sistema...")
    copy_to_clipboard(copy_text)
    
    print("🌐 Apertura sessione LinkedIn in Google Chrome...")
    open_linkedin_in_chrome()
    
    print("\n" + "="*65)
    print(" 🎉 PROCESSO DI PUBBLICAZIONE AVVIATO")
    print("="*65)
    print("1. Nel browser si è aperta la finestra di condivisione di LinkedIn.")
    print("2. Fai Cmd+V (Incolla) per inserire il testo già formattato.")
    print(f"3. Trascina o seleziona l'immagine: {photo}")
    print("="*65 + "\n")

    # Sposta la foto in published
    dest = os.path.join(PUBLISHED_DIR, os.path.basename(photo))
    shutil.move(photo, dest)
    print(f"📁 Foto archiviata in: {dest}")

if __name__ == "__main__":
    main()
