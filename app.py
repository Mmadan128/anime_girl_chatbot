# app.py
import streamlit as st
import os
import re
import random
import time
import shutil
import base64 
from typing import Optional

# --- New Imports for ElevenLabs and Environment Variables ---
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

# Import core components from your luna_agent.py
try:
    from luna_agent import LunaAIMLEngine, create_luna_agent
except ImportError as e:
    st.error(f"Waaah! Luna can't find her main brain module! 😱 Error: {e}")
    st.info("Please make sure 'luna_agent.py' is in the same directory as 'app.py'!")
    st.stop()

# --- Load Environment Variables ---
load_dotenv()

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Luna - Anime AI Assistant 🌸",
    page_icon="🌸",
    layout="centered"
)

# --- Configuration ---
AVATAR_BASE_PATH = 'avatars/'
TEMP_AUDIO_DIR = 'temp_audio_luna/'
BACKGROUND_MUSIC_FILE = 'bg_music/luna_theme.mp3'
DEFAULT_AVATAR_EMOTION = 'idle'

# --- ElevenLabs Configuration ---
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
LUNA_VOICE_ID = "piTKgcLEGmPE4e6mEKli"  # This is the ID for the voice "Rachel"

# --- Initialize ElevenLabs Client ---
elevenlabs_client = None
if not ELEVENLABS_API_KEY:
    st.warning("Psst! Your ElevenLabs API key is missing. Luna can't use her cute voice! 🤫 Please add it to your `.env` file.")
    print("❌ ElevenLabs API key not found in environment variables")
else:
    try:
        elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        print("✅ Successfully initialized ElevenLabs client.")
        try:
            voices_response = elevenlabs_client.voices.get_all()
            if hasattr(voices_response, 'voices'): voice_count = len(voices_response.voices)
            else: voice_count = len(voices_response) if isinstance(voices_response, list) else "unknown number of"
            print(f"✅ Connected to ElevenLabs. Found {voice_count} voices.")
        except Exception as e:
            error_msg = str(e)
            if "invalid_api_key" in error_msg.lower() or "401" in str(e):
                print("❌ ElevenLabs API key is invalid!")
                st.error("🔑 Your ElevenLabs API key is invalid! Please check your `.env` file.")
                elevenlabs_client = None
            else:
                print(f"⚠️ Warning: Could not test ElevenLabs connection: {e}")
    except Exception as e:
        print(f"❌ Could not initialize ElevenLabs client: {e}")
        st.error(f"Oh no! Could not connect to ElevenLabs. Error: {e}")
        elevenlabs_client = None

AVATAR_IMAGE_MAP = {
    'idle': 'luna_idle.jpg', 'speaking': 'luna_speaking.jpg', 'happy': 'luna_happy.jpg',
    'excited': 'luna_excited.jpg', 'mischievous': 'luna_mischievous.jpg', 'curious': 'luna_curious.jpg',
    'sad': 'luna_sad.jpg', 'confused': 'luna_confused.jpg', 'thinking': 'luna_thinking.jpg',
    'energetic': 'luna_excited.jpg'
}

# --- Helper Functions ---

def infer_emotion_from_text(text: str) -> str:
    text_lower = text.lower()
    if any(k in text_lower for k in ["kyaa~!", "yay!", "excited!", "amazing!", "happy", "love", "✨", "🌸", "💖", "🌟"]): return random.choice(["happy", "excited", "energetic"])
    if any(k in text_lower for k in ["hehe!", "mischievous", "teasing"]): return "mischievous"
    if any(k in text_lower for k in ["ooh!", "curious", "mystery"]): return "curious"
    if any(k in text_lower for k in ["aww...", "waaah!", "miss", "sorry"]): return "sad"
    if any(k in text_lower for k in ["eeeek!", "confused", "problem", "oops"]): return "confused"
    return "speaking"

def get_avatar_image_path(emotion: str) -> str:
    filename = AVATAR_IMAGE_MAP.get(emotion, AVATAR_IMAGE_MAP[DEFAULT_AVATAR_EMOTION])
    full_path = os.path.join(AVATAR_BASE_PATH, filename)
    if not os.path.exists(full_path):
        st.warning(f"Could not find avatar file: '{full_path}'.")
        return os.path.join(AVATAR_BASE_PATH, AVATAR_IMAGE_MAP[DEFAULT_AVATAR_EMOTION])
    return full_path

def generate_luna_audio(text: str) -> Optional[str]:
    """
    Generates an MP3 audio file using ElevenLabs.
    THIS FUNCTION REMAINS UNCHANGED, AS PER YOUR REQUEST.
    """
    if not text.strip() or not elevenlabs_client:
        print("❌ No text provided or ElevenLabs client not initialized")
        return None
    clean_text = re.sub(r'[^\w\s\.,!?;:\-\'"()]', '', text).strip()
    if not clean_text:
        print("❌ No valid text after cleaning")
        return None
    print(f"🎤 Generating audio for: \"{clean_text[:50]}{'...' if len(clean_text) > 50 else ''}\"")
    try:
        os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
        timestamp = int(time.time() * 1000)
        temp_audio_filename = os.path.join(TEMP_AUDIO_DIR, f"luna_response_{timestamp}.mp3")
        print(f"🔊 Making API call to ElevenLabs...")
        audio_generator = elevenlabs_client.text_to_speech.convert(
            text=clean_text,
            voice_id=LUNA_VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        print(f"✅ API call successful, saving audio...")
        with open(temp_audio_filename, 'wb') as audio_file:
            for chunk in audio_generator:
                if chunk:
                    audio_file.write(chunk)
        if os.path.exists(temp_audio_filename) and os.path.getsize(temp_audio_filename) > 0:
            print(f"✅ Audio file successfully saved: {temp_audio_filename} ({os.path.getsize(temp_audio_filename)} bytes)")
            return temp_audio_filename
        else:
            print(f"❌ Audio file was not created properly")
            return None
    except Exception as e:
        # Error handling is unchanged
        error_message = str(e)
        print(f"❌ ERROR generating audio: {error_message}")
        if "quota_exceeded" in error_message.lower(): st.warning("🔊 Luna's voice quota is used up! 🤫")
        elif "invalid_api_key" in error_message.lower(): st.error("🔐 Luna's voice key isn't working!")
        elif "voice" in error_message.lower() and "not found" in error_message.lower(): st.warning(f"🎭 Luna's voice ID might be wrong.")
        else: st.warning("🔊 Luna's voice box is having a tiny problem! 💖")
        return None

def play_background_music(file_path: str, volume: float = 0.2):
    if not os.path.exists(file_path):
        st.warning(f"I can't find my theme music at `{file_path}`.")
        return
    with open(file_path, "rb") as f: data = f.read()
    b64 = base64.b64encode(data).decode()
    md = f"""
        <audio id="bg-music" autoplay loop>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        <script>
            var audio = document.getElementById("bg-music");
            if (audio) {{ audio.volume = {volume}; }}
        </script>
        """
    st.markdown(md, unsafe_allow_html=True)

# --- Caching and Initialization ---
@st.cache_resource
def initialize_luna_brain():
    """Initializes and caches Luna's AIML and LangChain agent."""
    aiml_engine = LunaAIMLEngine()
    try:
        agent_executor = create_luna_agent()
        return aiml_engine, agent_executor
    except Exception as e:
        st.error(f"Waaah! Luna's main brain had a big stumble! 😱 Error: {e}")
        return aiml_engine, None

# --- Custom CSS ---
st.markdown("""<style>...</style>""".replace("...", """
    .stApp { background-color: #fce4ec; }
    div[data-testid="stVerticalBlock"] > div:first-child { background-color: #fff; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); padding: 20px; margin: 20px 0; }
    h1 { background-color: #ff80ab; color: white; padding: 15px 25px; font-size: 1.8em; text-align: center; border-radius: 10px 10px 0 0; margin: -20px -20px 20px -20px; }
    .chat-bubble { padding: 12px 18px; border-radius: 18px; line-height: 1.5; max-width: 80%; margin: 5px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .chat-bubble.user { background-color: #ffcdd2; color: #4a148c !important; margin-left: auto; border-bottom-right-radius: 2px; }
    .chat-bubble.luna { background-color: #e0f2f7; color: #004d40 !important; margin-right: auto; border-bottom-left-radius: 2px; }
    [data-testid="stSidebar"] { background-color: #ffb3c1; border-right: 2px solid #e91e63; }
    [data-testid="stSidebar"] img { border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.15); margin-bottom: 15px; }
"""), unsafe_allow_html=True)

st.title("Luna's Chat Room 🌸")

# --- Initialize Brain and Session State ---
st.session_state.aiml_engine, st.session_state.agent_executor = initialize_luna_brain()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    initial_greeting = "Kyaa~! Hello there, Master! ✨ I'm all ready to go! Let's chat! 🌟"
    st.session_state.chat_history.append({
        "sender": "Luna", "text": initial_greeting, "emotion": "excited",
        "audio_url": generate_luna_audio(initial_greeting)
    })

if 'current_avatar_emotion' not in st.session_state:
    st.session_state.current_avatar_emotion = "excited"

# --- Sidebar ---
with st.sidebar:
    # --- FIXED: Replaced use_container_width with width ---
    st.image(get_avatar_image_path(st.session_state.current_avatar_emotion), 
             caption="Luna, your AI companion 💖", width='stretch')
    st.markdown("---")
    st.markdown("🎵 **Background Music**")
    play_background_music(BACKGROUND_MUSIC_FILE, volume=0.2)
    st.info("Background music is on~ 🎶")
    st.markdown("---")
    st.markdown("🌸 **Luna's Abilities:**")
    st.markdown("- **Search-chan:** Web searches\n- **Calc-kun:** Math wizardry\n- **Muse-sensei:** Creative writing")

# --- Display Chat History ---
for msg in st.session_state.chat_history:
    role = "user" if msg["sender"] == "User" else "assistant"
    with st.chat_message(role):
        st.markdown(f'<div class="chat-bubble {role.lower()}">{msg["text"]}</div>', unsafe_allow_html=True)
        if role == 'assistant' and msg.get("audio_url") and os.path.exists(msg["audio_url"]):
            st.audio(msg["audio_url"], format="audio/mp3", autoplay=True)

# --- FIXED: Consolidated Input and Response Logic to prevent image cache errors ---
if user_input := st.chat_input("Type your message, Master..."):
    # Add user message to history
    st.session_state.chat_history.append({"sender": "User", "text": user_input})

    # Process Luna's response immediately
    with st.spinner("💖 Luna is thinking... Hehe! ✨"):
        luna_response_text = ""
        try:
            # Try AIML first for quick responses
            aiml_response = st.session_state.aiml_engine.process(user_input)
            if aiml_response:
                luna_response_text = aiml_response
            # Fall back to the LangChain agent if no AIML match
            elif st.session_state.agent_executor:
                response = st.session_state.agent_executor.invoke({"input": user_input})
                luna_response_text = response['output']
            else:
                luna_response_text = "Waaah! My main brain isn't working right now! 😱"
        except Exception as e:
            print(f"Error processing user input: {e}")
            luna_response_text = f"Eeeek! A tiny problem occurred! Let's try again! 💖"

        # Determine emotion and generate audio
        luna_emotion = infer_emotion_from_text(luna_response_text)
        luna_audio_url = generate_luna_audio(luna_response_text)

        # Add Luna's complete response to history
        st.session_state.chat_history.append({
            "sender": "Luna", 
            "text": luna_response_text,
            "emotion": luna_emotion, 
            "audio_url": luna_audio_url
        })
        
        # Update the avatar emotion for the UI refresh
        st.session_state.current_avatar_emotion = luna_emotion

    # Use a single rerun at the end to update the UI reliably
    st.rerun()

# --- Main Execution Guard ---
if __name__ == "__main__":
    os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)