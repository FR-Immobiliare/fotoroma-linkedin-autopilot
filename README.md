# 📸 FotoRomaImmobiliare — LinkedIn Autopilot Engine

Sistema autonomo in Cloud per la generazione e pubblicazione di post strategici su LinkedIn (profilo personale o Company Page).

## 🚀 Come Funziona
1. **Coda Immagini (`queue_photos/`):** Contiene le foto dei tuoi shooting a Roma.
2. **AI Copywriting:** L'AI analizza la foto, legge la location e scrive un copy persuasivo orientato ai benefici di business (filtro curiosi, zero sopralluoghi a vuoto, velocità di chiusura).
3. **Pubblicazione Schedulata:** Tramite GitHub Actions, il bot pubblica ogni **Martedì e Venerdì alle 10:00**.
4. **Auto-Archivio (`published/`):** La foto pubblicata viene archiviata automaticamente senza duplicati.

## 🔐 Configurazione Secrets su GitHub
Nel tuo repository GitHub (in `Settings` -> `Secrets and variables` -> `Actions`), aggiungi:
- `LINKEDIN_ACCESS_TOKEN`: Il token OAuth di LinkedIn.
- `LINKEDIN_AUTHOR_URN`: Il tuo URN persona (`urn:li:person:XXXX`) o pagina (`urn:li:organization:XXXX`).
- `GEMINI_API_KEY` (Opzionale): Chiave API gratuita di Google Gemini per generare variazioni creative sempre uniche.
