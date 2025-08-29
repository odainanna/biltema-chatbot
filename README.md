# 💬 BILTEMA chatbot MVP

Denne applikasjonen er en enkel demonstrasjon av en kundeservicebot for Biltema
Tønsberg. Boten bruker en Retrieval Augmented Generation (RAG) strategi for å
hente informasjon fra biltema.no og kombinerer dette med OpenAI for å generere
svar på spørsmål om produkter.

### Kjør lokalt

1. Installer avhengighetene

   ```
   pip install -r requirements.txt
   ```

2. Start tjenesten

   ```
   streamlit run streamlit_app.py
   ```

Boten trenger en gyldig OpenAI API-nøkkel for å fungere.
