import streamlit as st
from engine import AuroraEngine
from langchain_core.messages import HumanMessage, AIMessage

MODELS = ["gemini-3.1-pro-preview", 
          "gemini-3-flash-preview",
          "gemini-3.1-flash-lite",
          "gemini-2.5-flash",
          "gemini-2.5-flash-lite",
          "gemini-2.5-pro"
          ]

st.set_page_config(page_title="Aurora Luxury Travel", page_icon="🌌")

# Sidebar for Authentication and Model Selection
with st.sidebar:
    st.title("🔐 Authentication")
    user_key = st.text_input("Enter Gemini API Key", type="password")
    selected_model = st.selectbox("Choose Model", MODELS)
    
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        if "engine" in st.session_state:
            st.session_state.engine.reset_chat()
        st.rerun()

st.title("🌌 Aurora")
st.caption("Elite Luxury Travel Consultant")

# Check for API key before proceeding
if not user_key:
    st.info("Please enter your Gemini API Key in the sidebar to begin.", icon="🔑")
    st.stop()

# Initialize Engine in Session State
try:
    if "engine" not in st.session_state or st.session_state.get("current_model") != selected_model or st.session_state.get("current_key") != user_key:
        with st.spinner("Initializing Aurora..."):
            st.session_state.engine = AuroraEngine(user_key, selected_model)
            st.session_state.current_model = selected_model
            st.session_state.current_key = user_key
            
            # Restore chat history in engine from messages (preserve conversation)
            if "messages" in st.session_state and st.session_state.messages:
                try:
                    for msg in st.session_state.messages:
                        if msg["role"] == "user":
                            st.session_state.engine.chat_history.append(HumanMessage(content=msg["content"]))
                        else:
                            st.session_state.engine.chat_history.append(AIMessage(content=msg["content"]))
                except Exception as e:
                    st.warning(f"Could not restore conversation: {str(e)}")

    if "messages" not in st.session_state:
        st.session_state.messages = []

except ValueError as e:
    st.error(f"❌ Configuration Error: {str(e)}")
    st.stop()
except Exception as e:
    st.error(f"❌ Failed to initialize Aurora: {str(e)}")
    st.stop()

# Display history
try:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
except Exception as e:
    st.error(f"Error displaying chat history: {str(e)}")

# Chat Logic
try:
    if prompt := st.chat_input("How may I assist you?"):
        if not prompt.strip():
            st.warning("Please enter a valid message.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                try:
                    response = st.session_state.engine.get_response(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"[Error]: {str(e)}"
                    st.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
except Exception as e:
    st.error(f"Unexpected error in chat logic: {str(e)}")