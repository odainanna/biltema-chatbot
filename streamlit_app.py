import streamlit as st
from openai import OpenAI
import requests
from urllib.parse import quote


def fetch_biltema_context(query: str, limit: int = 2000):
    """Fetch raw HTML from biltema.no search as context for RAG."""
    url = f"https://www.biltema.no/sok/?query={quote(query)}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        text = response.text[:limit]
    except Exception as exc:  # pragma: no cover - best effort
        text = f"Kunne ikke hente informasjon fra biltema.no: {exc}"
    return text, url

# Show title and description.
st.title("💬 Biltema-bot")
st.write(
    "Dette er en MVP som hjelper kundeservice hos Biltema Tønsberg. "
    "Boten bruker OpenAI sammen med informasjon fra biltema.no for å svare på "
    "spørsmål om produktene. Oppgi din OpenAI API-nøkkel for å komme i gang."
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        context, source_url = fetch_biltema_context(prompt)
        with st.expander("RAG-kontekst"):
            st.write(f"Kilde: {source_url}")
            st.write(context)

        messages_for_openai = [
            {
                "role": "system",
                "content": (
                    "Du er en hjelpsom assistent for Biltema Tønsberg. "
                    "Bruk konteksten fra biltema.no når du svarer."
                ),
            }
        ]
        messages_for_openai.extend(
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[:-1]
        )
        messages_for_openai.append(
            {
                "role": "user",
                "content": f"{prompt}\n\nKontekst fra biltema.no:\n{context}",
            }
        )
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages_for_openai,
            stream=True,
        )

        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
