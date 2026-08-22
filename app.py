import streamlit as st
import os
from agent import get_agent_chat_session

# Page Configuration
st.set_page_config(
    page_title="Aster & Row Support Agent", 
    page_icon="🛍️", 
    layout="centered"
)

# Header Section (Always renders)
st.title("🛍️ Aster & Row Support Agent")
st.markdown("Your AI assistant for product policies, warranties, and order tracking.")
st.markdown("---")

# Initialize chat session in Streamlit state if it doesn't exist
if "chat_session" not in st.session_state:
    st.session_state.chat_session = get_agent_chat_session()

# Initialize message history in Streamlit state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat messages from history on rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input box at the bottom
if user_input := st.chat_input("Ask about an order (e.g., ORD-1005) or policy..."):
    
    # 1. Append user message to state and display it
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking and checking tools..."):
            try:
                response = st.session_state.chat_session.send_message(user_input)
                bot_reply = response.text
                st.markdown(bot_reply)
                
                # 3. Append assistant response to state
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                error_msg = f"Error: {e}"
                st.error(error_msg)