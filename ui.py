import streamlit as st
import httpx
from adept.core.config import MODEL_CONFIG

if "messages" not in st.session_state:
    st.session_state.messages = []
if "backend_history" not in st.session_state:
    st.session_state.backend_history = []

st.set_page_config(page_title="Adept", page_icon="🚀", layout="wide")

API_URL = "http://127.0.0.1:8000/chat"

st.title("🚀 Adept")
st.caption("A multi-cloud, context-aware AI orchestrator.")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    provider = st.selectbox("AI Provider", list(MODEL_CONFIG.keys()))
    model = st.selectbox("AI Model", list(MODEL_CONFIG[provider]["models"].keys()))
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.backend_history = []
        st.rerun()

# Main chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask Adept anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        try:
            with httpx.Client(timeout=60) as client:
                response = client.post(
                    API_URL,
                    json={
                        "message": prompt,
                        "provider": provider,
                        "model": model,
                        "conversation_history": st.session_state.backend_history,
                    }
                )
                response.raise_for_status()
            
            result = response.json()
            
            if result.get("status") == "success":
                full_response = result.get("response", "")
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.session_state.backend_history = result.get("conversation_history", [])
            else:
                st.error(f"API Error: {result.get('detail', 'Unknown error')}")

        except Exception as e:
            st.error(f"Failed to get response: {str(e)}")
