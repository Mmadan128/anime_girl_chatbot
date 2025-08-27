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
# --- THIS IS THE ONLY CHANGE: Updated the Voice ID to "Rachel" ---
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
        
        # Test the connection by listing voices (but handle errors gracefully)
        try:
            voices_response = elevenlabs_client.voices.get_all()
            if hasattr(voices_response, 'voices'):
                voice_count = len(voices_response.voices)
            else:
                voice_count = len(voices_response) if isinstance(voices_response, list) else "unknown number of"
            print(f"✅ Connected to ElevenLabs. Found {voice_count} voices.")
        except Exception as e:
            error_msg = str(e)
            if "invalid_api_key" in error_msg.lower() or "401" in str(e):
                print("❌ ElevenLabs API key is invalid!")
                st.error("🔑 Your ElevenLabs API key is invalid! Please check your `.env` file.")
                elevenlabs_client = None  # Disable client if key is invalid
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
    if any(k in text_lower for k in ["kyaa~!", "yay!", "excited!", "amazing!", "happy", "love", "✨", "🌸", "💖", "🌟"]): 
        return random.choice(["happy", "excited", "energetic"])
    if any(k in text_lower for k in ["hehe!", "mischievous", "teasing"]): 
        return "mischievous"
    if any(k in text_lower for k in ["ooh!", "curious", "mystery"]): 
        return "curious"
    if any(k in text_lower for k in ["aww...", "waaah!", "miss", "sorry"]): 
        return "sad"
    if any(k in text_lower for k in ["eeeek!", "confused", "problem", "oops"]): 
        return "confused"
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
    Generates an MP3 audio file using ElevenLabs - Following Official Documentation
    """
    if not text.strip() or not elevenlabs_client:
        print("❌ No text provided or ElevenLabs client not initialized")
        return None

    # Clean the text for TTS (remove emojis and special characters that might cause issues)
    clean_text = re.sub(r'[^\w\s\.,!?;:\-\'"()]', '', text)
    clean_text = clean_text.strip()
    
    if not clean_text:
        print("❌ No valid text after cleaning")
        return None

    print(f"🎤 Generating audio for: \"{clean_text[:50]}{'...' if len(clean_text) > 50 else ''}\"")
    
    try:
        # Ensure temp directory exists
        os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
        
        # Generate unique filename
        timestamp = int(time.time() * 1000)
        temp_audio_filename = os.path.join(TEMP_AUDIO_DIR, f"luna_response_{timestamp}.mp3")
        
        print(f"🔊 Making API call to ElevenLabs...")
        
        # OFFICIAL DOCS METHOD: Use text_to_speech.convert()
        audio_generator = elevenlabs_client.text_to_speech.convert(
            text=clean_text,
            voice_id=LUNA_VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        
        print(f"✅ API call successful, saving audio...")
        
        # Save the audio - the convert method returns audio bytes
        with open(temp_audio_filename, 'wb') as audio_file:
            for chunk in audio_generator:
                if chunk:
                    audio_file.write(chunk)
        
        # Verify file was created and has content
        if os.path.exists(temp_audio_filename) and os.path.getsize(temp_audio_filename) > 0:
            print(f"✅ Audio file successfully saved: {temp_audio_filename} ({os.path.getsize(temp_audio_filename)} bytes)")
            return temp_audio_filename
        else:
            print(f"❌ Audio file was not created properly")
            return None
            
    except Exception as e:
        error_message = str(e)
        print(f"❌ ERROR generating audio: {error_message}")
        
        # More specific error handling
        if "quota_exceeded" in error_message.lower() or "usage limit" in error_message.lower():
            st.warning("🔊 Luna's voice quota is used up! She'll be quiet for now~ 🤫")
        elif "invalid_api_key" in error_message.lower() or "unauthorized" in error_message.lower():
            st.error("🔐 Luna's voice key isn't working! Please check your ElevenLabs API key in the .env file.")
        elif "voice" in error_message.lower() and "not found" in error_message.lower():
            st.warning(f"🎭 Luna's voice ID might be wrong. Current ID: {LUNA_VOICE_ID}")
        elif "401" in error_message:
            st.error("🔑 Authentication failed! Please verify your ElevenLabs API key is correct.")
        else:
            st.warning("🔊 Luna's voice box is having a tiny problem! She'll try again later~ 💖")
        
        return None


# Alternative: If you want to stream audio directly (for real-time playback)
def generate_luna_audio_streaming(text: str):
    """
    Alternative method for streaming audio directly - Based on Official Docs
    """
    if not text.strip() or not elevenlabs_client:
        return None
    
    clean_text = re.sub(r'[^\w\s\.,!?;:\-\'"()]', '', text).strip()
    
    try:
        # Stream method from official docs
        audio_stream = elevenlabs_client.text_to_speech.convert_as_stream(
            text=clean_text,
            voice_id=LUNA_VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        
        # For streaming, you could use:
        # from elevenlabs import stream
        # stream(audio_stream)
        
        return audio_stream
        
    except Exception as e:
        print(f"❌ Streaming error: {e}")
        return None
def play_background_music(file_path: str, volume: float = 0.2):
    if not os.path.exists(file_path):
        st.warning(f"I can't find my theme music at `{file_path}`.")
        return

    with open(file_path, "rb") as f: 
        data = f.read()
    
    b64 = base64.b64encode(data).decode()
    md = f"""
        <audio id="bg-music" autoplay loop>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        <script>
            var audio = document.getElementById("bg-music");
            if (audio) {{
                audio.volume = {volume};
            }}
        </script>
        """
    st.markdown(md, unsafe_allow_html=True)

# --- Test ElevenLabs Connection ---
def test_elevenlabs_connection():
    """Test function to verify ElevenLabs is working"""
    if not elevenlabs_client:
        return False, "No client initialized"
    
    try:
        # Try to get voice info using the correct method
        voices_response = elevenlabs_client.voices.get_all()
        
        if hasattr(voices_response, 'voices'):
            voices = voices_response.voices
        else:
            voices = voices_response
        
        # Check if our specific voice exists
        luna_voice = None
        for voice in voices:
            if hasattr(voice, 'voice_id') and voice.voice_id == LUNA_VOICE_ID:
                luna_voice = voice
                break
        
        if luna_voice:
            voice_name = getattr(luna_voice, 'name', 'Unknown Voice')
            return True, f"Found Luna's voice: {voice_name}"
        else:
            # Show available voices for debugging
            available_voices = []
            for voice in voices[:5]:  # Show first 5 voices
                voice_name = getattr(voice, 'name', 'Unknown')
                voice_id = getattr(voice, 'voice_id', 'Unknown ID')
                available_voices.append(f"{voice_name} ({voice_id[:8]}...)")
            
            return False, f"Voice ID {LUNA_VOICE_ID[:8]}... not found. Available: {', '.join(available_voices)}"
            
    except Exception as e:
        error_msg = str(e)
        if "invalid_api_key" in error_msg.lower() or "401" in error_msg:
            return False, "❌ Invalid API Key - Please check your ElevenLabs API key"
        elif "quota" in error_msg.lower():
            return False, "⚠️ Quota exceeded - ElevenLabs usage limit reached"
        else:
            return False, f"Connection test failed: {error_msg}"

# --- Caching and Initialization ---
@st.cache_resource
def initialize_luna_brain():
    aiml_engine = LunaAIMLEngine()
    try:
        agent_executor = create_luna_agent()
        return aiml_engine, agent_executor, None
    except Exception as e:
        error_msg = f"Waaah! Luna's main brain had a big stumble! 😱 Error: {e}"
        st.error(error_msg)
        return aiml_engine, None, error_msg

# --- Custom CSS ---
st.markdown(
    """
    <style>
    .stApp { background-color: #fce4ec; }
    div[data-testid="stVerticalBlock"] > div:first-child { 
        background-color: #fff; 
        border-radius: 20px; 
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); 
        padding: 20px; 
        margin-top: 20px; 
        margin-bottom: 20px; 
    }
    h1 { 
        background-color: #ff80ab; 
        color: white; 
        padding: 15px 25px; 
        font-size: 1.8em; 
        text-align: center; 
        border-radius: 10px 10px 0 0; 
        margin-top: -20px; 
        margin-left: -20px; 
        margin-right: -20px; 
        margin-bottom: 20px; 
    }
    div[data-testid="chatMessage"] { 
        margin-bottom: 0.5rem; 
        margin-top: 0.5rem; 
        display: flex; 
    }
    div[data-testid="stChatMessageContent"] { 
        padding: 0; 
        background: none; 
    }
    .chat-bubble { 
        padding: 12px 18px; 
        border-radius: 18px; 
        line-height: 1.5; 
        word-wrap: break-word; 
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05); 
        max-width: 80%; 
        margin: 5px 0; 
        color: #333 !important; 
    }
    .chat-bubble.user { 
        background-color: #ffcdd2; 
        color: #4a148c !important; 
        margin-left: auto; 
        border-bottom-right-radius: 2px; 
    }
    .chat-bubble.luna { 
        background-color: #e0f2f7; 
        color: #004d40 !important; 
        margin-right: auto; 
        border-bottom-left-radius: 2px; 
    }
    div[data-testid="chatMessage"] img { display: none; }
    div[data-testid="chatMessage"] [data-testid="stImage"] { display: none; }
    [data-testid="stSidebar"] { 
        background-color: #ffb3c1; 
        border-right: 2px solid #e91e63; 
    }
    [data-testid="stSidebar"] img { 
        border-radius: 15px; 
        box-shadow: 0 5px 15px rgba(0,0,0,0.15); 
        margin-bottom: 15px; 
    }
    div[data-testid="stAudio"] { 
        margin-top: 5px; 
        border-radius: 10px; 
        background-color: rgba(255, 255, 255, 0.7); 
        padding: 5px; 
    }
    .status-indicator {
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8em;
        margin: 5px 0;
    }
    .status-success { background-color: #c8e6c9; color: #2e7d32; }
    .status-warning { background-color: #fff3e0; color: #f57c00; }
    .status-error { background-color: #ffcdd2; color: #c62828; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Luna's Chat Room 🌸")

# --- Initialize Session State ---
if 'luna_brain_init_status' not in st.session_state:
    st.session_state.aiml_engine, st.session_state.agent_executor, st.session_state.init_error = initialize_luna_brain()
    st.session_state.luna_brain_init_status = "initialized"

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    
    # Test ElevenLabs and set appropriate greeting
    if elevenlabs_client:
        test_success, test_message = test_elevenlabs_connection()
        if test_success:
            initial_greeting = "Kyaa~! Hello there, Master! ✨ My voice should work perfectly now! Let's chat! 🌟"
        else:
            initial_greeting = f"Kyaa~! Hello Master! ✨ My voice might be a bit shy today ({test_message}), but I'm still here to help! 💖"
    else:
        initial_greeting = "Kyaa~! Hello there, Master! ✨ I'm in text-only mode today, but still ready to help! 🌟"
    
    # Generate audio for initial greeting
    luna_audio_url = generate_luna_audio(initial_greeting)
    
    st.session_state.chat_history.append({
        "sender": "Luna", 
        "text": initial_greeting, 
        "emotion": "excited",
        "audio_url": luna_audio_url
    })

if 'current_avatar_emotion' not in st.session_state:
    st.session_state.current_avatar_emotion = "excited"

# --- Sidebar ---
with st.sidebar:
    st.image(get_avatar_image_path(st.session_state.current_avatar_emotion), 
             caption="Luna, your AI companion 💖", use_container_width=True)
    
    st.markdown("---")
    
    # Voice Status Indicator
    st.markdown("🎤 **Voice Status**")
    if elevenlabs_client:
        test_success, test_message = test_elevenlabs_connection()
        if test_success:
            st.markdown('<div class="status-indicator status-success">✅ Voice Active</div>', unsafe_allow_html=True)
            st.caption(test_message)
        else:
            st.markdown('<div class="status-indicator status-warning">⚠️ Voice Issues</div>', unsafe_allow_html=True)
            st.caption(test_message)
    else:
        st.markdown('<div class="status-indicator status-error">❌ Voice Disabled</div>', unsafe_allow_html=True)
        st.caption("ElevenLabs API key missing")
    
    st.markdown("---")
    
    # Background Music
    st.markdown("🎵 **Background Music**")
    if os.path.exists(BACKGROUND_MUSIC_FILE):
        play_background_music(BACKGROUND_MUSIC_FILE, volume=0.2)
        st.info("Background music is on~ 🎶")
    else:
        st.caption("No background music file found")

    st.markdown("---")
    st.markdown("🌸 **Luna's Abilities:**")
    st.markdown("- **Search-chan:** Web searches\n- **Calc-kun:** Math wizardry\n- **Muse-sensei:** Creative writing")
    
    # Debug button (only show in development)
    if st.button("🔧 Test Voice", help="Test ElevenLabs voice generation"):
        test_text = "Hello! This is a voice test from Luna!"
        test_audio = generate_luna_audio(test_text)
        if test_audio and os.path.exists(test_audio):
            st.success("Voice test successful!")
            st.audio(test_audio)
        else:
            st.error("Voice test failed!")

# --- Main Chat Logic ---
for msg in st.session_state.chat_history:
    role = "user" if msg["sender"] == "User" else "assistant"
    with st.chat_message(role):
        st.markdown(f'<div class="chat-bubble {role.lower()}">{msg["text"]}</div>', unsafe_allow_html=True)
        
        # Play audio if available and file exists
        if role == 'assistant' and msg.get("audio_url") and os.path.exists(msg["audio_url"]):
            st.audio(msg["audio_url"], format="audio/mp3", autoplay=True)

# --- User Input Handler ---
if user_input := st.chat_input("Type your message, Master..."):
    # Add user message
    st.session_state.chat_history.append({"sender": "User", "text": user_input})
    st.session_state.current_avatar_emotion = 'thinking'
    st.rerun()

# --- Luna Response Handler ---
if st.session_state.chat_history and st.session_state.chat_history[-1]["sender"] == "User":
    if not st.session_state.get('is_luna_processing', False):
        st.session_state.is_luna_processing = True
        latest_user_input = st.session_state.chat_history[-1]["text"]

        luna_response_text = ""
        try:
            # Try AIML first
            aiml_response = st.session_state.aiml_engine.process(latest_user_input)
            if aiml_response:
                luna_response_text = aiml_response
            elif st.session_state.agent_executor:
                # Fall back to agent
                response = st.session_state.agent_executor.invoke({"input": latest_user_input})
                luna_response_text = response['output']
            else:
                luna_response_text = "Waaah! My main brain isn't working right now! 😱"
                
        except Exception as e:
            print(f"Error processing user input: {e}")
            luna_response_text = f"Eeeek! A tiny problem occurred! Let's try again! 💖"

        # Determine emotion and generate audio
        luna_emotion = infer_emotion_from_text(luna_response_text)
        print(f"🎭 Luna emotion: {luna_emotion}")
        
        # Generate audio (this is where the fix is most important)
        luna_audio_url = generate_luna_audio(luna_response_text)
        print(f"🎤 Audio generated: {luna_audio_url}")

        # Add Luna's response to chat history
        st.session_state.chat_history.append({
            "sender": "Luna", 
            "text": luna_response_text,
            "emotion": luna_emotion, 
            "audio_url": luna_audio_url
        })
        
        # Update state and rerun
        st.session_state.is_luna_processing = False
        st.session_state.current_avatar_emotion = luna_emotion
        st.rerun()

# --- Cleanup old audio files periodically ---
def cleanup_old_audio_files(max_age_minutes=30):
    """Clean up old audio files to save disk space"""
    if not os.path.exists(TEMP_AUDIO_DIR):
        return
        
    current_time = time.time()
    for filename in os.listdir(TEMP_AUDIO_DIR):
        file_path = os.path.join(TEMP_AUDIO_DIR, filename)
        if os.path.isfile(file_path):
            file_age_minutes = (current_time - os.path.getmtime(file_path)) / 60
            if file_age_minutes > max_age_minutes:
                try:
                    os.remove(file_path)
                    print(f"🧹 Cleaned up old audio file: {filename}")
                except Exception as e:
                    print(f"❌ Could not clean up {filename}: {e}")

# --- Main Execution Guard ---
if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
    os.makedirs(AVATAR_BASE_PATH, exist_ok=True)
    
    # Clean up old audio files
    cleanup_old_audio_files()