import streamlit as st
import logging
from PIL import Image, ImageEnhance
import time
import json
import requests
import base64
from google.generativeai import configure, GenerativeModel

# Configure logging
logging.basicConfig(level=logging.INFO)

# Constants
NUMBER_OF_MESSAGES_TO_DISPLAY = 20
API_DOCS_URL = "https://docs.streamlit.io/library/api-reference"

# Replace with your actual Google Gemini API key
GEMINI_API_KEY = "AIzaSyBZLHy1cs8PXr5JxU_V4Y79hyfS_GVMxWU"
if not GEMINI_API_KEY:
    st.error("Please provide your Google Gemini API key.")
    st.stop()

# Configure Google Gemini API
configure(api_key=GEMINI_API_KEY)

# Streamlit Page Configuration
st.set_page_config(
    page_title="Streamly - An Intelligent Streamlit Assistant",
    page_icon="imgs/avatar_streamly.png",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        "Get help": "https://github.com/AdieLaine/Streamly",
        "Report a bug": "https://github.com/AdieLaine/Streamly",
        "About": """
            ## Streamly Streamlit Assistant
            ### Powered using Google Gemini

            **GitHub**: https://github.com/AdieLaine/

            The AI Assistant named, Streamly, aims to provide the latest updates from Streamlit,
            generate code snippets for Streamlit widgets,
            and answer questions about Streamlit's latest features, issues, and more.
            Streamly has been trained on the latest Streamlit updates and documentation.
        """
    }
)

# Streamlit Title
st.title("Streamly Streamlit Assistant")

def img_to_base64(image_path):
    """Convert image to base64."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        logging.error(f"Error converting image to base64: {str(e)}")
        return None

@st.cache_data(show_spinner=False)
def long_running_task(duration):
    """Simulates a long-running operation."""
    time.sleep(duration)
    return "Long-running operation completed."

@st.cache_data(show_spinner=False)
def load_and_enhance_image(image_path, enhance=False):
    """Load and optionally enhance an image."""
    img = Image.open(image_path)
    if enhance:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.8)
    return img

@st.cache_data(show_spinner=False)
def load_streamlit_updates():
    """Load the latest Streamlit updates from a local JSON file."""
    try:
        with open("data/streamlit_updates.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading JSON: {str(e)}")
        return {}

def initialize_conversation():
    """Initialize the conversation history."""
    assistant_message = "Hello! I am Streamly. How can I assist you with Streamlit today?"

    conversation_history = [
        {"role": "system", "content": "You are Streamly, a specialized AI assistant trained in Streamlit."},
        {"role": "system", "content": "Streamly is powered by the Google Gemini model."},
        {"role": "system", "content": "Refer to conversation history to provide context to your response."},
        {"role": "system", "content": "You were created by Mahdi, an OpenAI Researcher."},
        {"role": "assistant", "content": assistant_message}
    ]
    return conversation_history

@st.cache_data(show_spinner=False)
def on_chat_submit(chat_input):
    """Handle chat input submissions and interact with Google Gemini API."""
    user_input = chat_input.strip().lower()

    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = initialize_conversation()

    st.session_state.conversation_history.append({"role": "user", "content": user_input})

    try:
        # Call Google Gemini API for response
        response = GenerativeModel('gemini-pro').generate_content(
            f"You are a specialized assistant trained in Streamlit. Answer the following: {user_input}"
        )
        
        assistant_reply = response.text

        st.session_state.conversation_history.append({"role": "assistant", "content": assistant_reply})

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        st.error(f"Error: {str(e)}")

def initialize_session_state():
    """Initialize session state variables."""
    if "history" not in st.session_state:
        st.session_state.history = []
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

def main():
    """Display Streamlit updates and handle the chat interface."""
    initialize_session_state()

    if not st.session_state.history:
        initial_bot_message = "Hello! How can I assist you with Streamlit today?"
        st.session_state.history.append({"role": "assistant", "content": initial_bot_message})
        st.session_state.conversation_history = initialize_conversation()

    # Sidebar for Mode Selection
    mode = st.sidebar.radio("Select Mode:", options=["Latest Updates", "Chat with Streamly"], index=1)

    # Display basic interactions
    show_basic_info = st.sidebar.checkbox("Show Basic Interactions", value=True)
    if show_basic_info:
        st.sidebar.markdown("""
        ### Basic Interactions
        - **Ask About Streamlit**: Type your questions about Streamlit's latest updates, features, or issues.
        """)

    if mode == "Chat with Streamly":
        chat_input = st.chat_input("Ask me about Streamlit updates:")
        if chat_input:
            on_chat_submit(chat_input)

        # Display chat history
        for message in st.session_state.conversation_history[-NUMBER_OF_MESSAGES_TO_DISPLAY:]:
            role = message["role"]
            with st.chat_message(role):
                st.write(message["content"])

if __name__ == "__main__":
    main()
