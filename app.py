# app.py - Streamlit Cloud Ready Version
import streamlit as st
import os
import re
import random
import time
import base64 
from typing import Optional

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Luna - Anime AI Assistant 🌸",
    page_icon="🌸",
    layout="centered"
)

# --- Configuration ---
DEFAULT_AVATAR_EMOTION = 'idle'

# --- ElevenLabs Configuration ---
ELEVENLABS_API_KEY = st.secrets.get("ELEVENLABS_API_KEY", None)
LUNA_VOICE_ID = "piTKgcLEGmPE4e6mEKli"  # Nicole - Perfect anime girl voice

# --- Initialize ElevenLabs Client ---
elevenlabs_client = None
if not ELEVENLABS_API_KEY:
    st.warning("ElevenLabs API key is missing. Luna will be in text-only mode. Add your API key in Streamlit secrets.")
    print("❌ ElevenLabs API key not found in secrets")
else:
    try:
        # Only import and initialize ElevenLabs if API key is available
        from elevenlabs.client import ElevenLabs
        
        elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        print("✅ Successfully initialized ElevenLabs client.")
        
        # Test the connection
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
                st.error("🔑 Your ElevenLabs API key is invalid! Please check your Streamlit secrets.")
                elevenlabs_client = None
            else:
                print(f"⚠️ Warning: Could not test ElevenLabs connection: {e}")
            
    except ImportError:
        st.warning("ElevenLabs library not installed. Luna will be in text-only mode.")
        elevenlabs_client = None
    except Exception as e:
        print(f"❌ Could not initialize ElevenLabs client: {e}")
        st.error(f"Could not connect to ElevenLabs. Error: {e}")
        elevenlabs_client = None

# --- Avatar Images (Using emoji as fallback) ---
AVATAR_IMAGE_MAP = {
    'idle': '😊', 'speaking': '💬', 'happy': '😄',
    'excited': '✨', 'mischievous': '😏', 'curious': '🤔',
    'sad': '😢', 'confused': '😕', 'thinking': '🤓',
    'energetic': '⚡'
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

def get_avatar_emoji(emotion: str) -> str:
    return AVATAR_IMAGE_MAP.get(emotion, AVATAR_IMAGE_MAP[DEFAULT_AVATAR_EMOTION])

def generate_luna_audio(text: str) -> Optional[bytes]:
    """
    Generates audio bytes using ElevenLabs - Streamlit Cloud Compatible
    """
    if not text.strip() or not elevenlabs_client:
        print("❌ No text provided or ElevenLabs client not initialized")
        return None

    # Clean the text for TTS
    clean_text = re.sub(r'[^\w\s\.,!?;:\-\'"()]', '', text)
    clean_text = clean_text.strip()
    
    if not clean_text:
        print("❌ No valid text after cleaning")
        return None

    print(f"🎤 Generating audio for: \"{clean_text[:50]}{'...' if len(clean_text) > 50 else ''}\"")
    
    try:
        print(f"🔊 Making API call to ElevenLabs...")
        
        # Use text_to_speech.convert() method
        audio_generator = elevenlabs_client.text_to_speech.convert(
            text=clean_text,
            voice_id=LUNA_VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        
        print(f"✅ API call successful, processing audio...")
        
        # Collect audio bytes in memory
        audio_bytes = b""
        for chunk in audio_generator:
            if chunk:
                audio_bytes += chunk
        
        if len(audio_bytes) > 0:
            print(f"✅ Audio generated successfully ({len(audio_bytes)} bytes)")
            return audio_bytes
        else:
            print("❌ No audio data received")
            return None
            
    except Exception as e:
        error_message = str(e)
        print(f"❌ ERROR generating audio: {error_message}")
        
        # Specific error handling with user-friendly messages
        if "quota_exceeded" in error_message.lower() or "usage limit" in error_message.lower():
            st.warning("🔊 Luna's voice quota is used up! She'll be quiet for now~ 🤫")
        elif "invalid_api_key" in error_message.lower() or "unauthorized" in error_message.lower():
            st.error("🔐 Luna's voice key isn't working! Please check your ElevenLabs API key in Streamlit secrets.")
        elif "voice" in error_message.lower() and "not found" in error_message.lower():
            st.warning(f"🎭 Luna's voice ID might be wrong. Current ID: {LUNA_VOICE_ID}")
        elif "401" in error_message:
            st.error("🔑 Authentication failed! Please verify your ElevenLabs API key is correct.")
        else:
            st.warning("🔊 Luna's voice box is having a tiny problem! She'll try again later~ 💖")
        
        return None

def test_elevenlabs_connection():
    """Test function to verify ElevenLabs is working"""
    if not elevenlabs_client:
        return False, "No client initialized"
    
    try:
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

# --- Fallback Luna AI Engine (Simple responses) ---
class SimpleLunaEngine:
    def __init__(self):
        self.responses = {
            "hello": ["Kyaa~! Hello there, Master! ✨", "Hi hi! Luna is here to help! 🌸", "Ooh! Hello, Master! How can Luna assist you today? 💖"],
            "how are you": ["I'm doing great, Master! Full of energy! ⚡", "Luna is super duper fine! Thanks for asking! 😊", "Kyaa~! I'm wonderful! Ready for anything! 🌟"],
            "bye": ["Aww... bye bye, Master! Come back soon! 🌸", "See you later! Luna will miss you! 💖", "Bye bye! Take care, Master! ✨"],
            "default": [
                "Hmm... that's interesting, Master! Tell me more! 🤔",
                "Ooh! Luna thinks that's really cool! ✨",
                "Kyaa~! Luna isn't sure about that, but she's learning! 🌸",
                "That sounds fascinating! Luna loves learning new things! 💖",
                "Eeeek! Luna's not quite sure, but she'll do her best to help! 😊"
            ]
        }
    
    def process(self, text: str) -> str:
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["hello", "hi", "hey"]):
            return random.choice(self.responses["hello"])
        elif any(word in text_lower for word in ["how are you", "how're you", "how do you feel"]):
            return random.choice(self.responses["how are you"])
        elif any(word in text_lower for word in ["bye", "goodbye", "see you", "farewell"]):
            return random.choice(self.responses["bye"])
        else:
            return random.choice(self.responses["default"])

# --- Initialize Simple Luna Engine ---
@st.cache_resource
def initialize_luna_brain():
    return SimpleLunaEngine()

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
    .chat-bubble.assistant { 
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
    .avatar-large {
        font-size: 4em;
        text-align: center;
        margin: 20px 0;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Luna's Chat Room 🌸")

# --- Initialize Session State ---
if 'luna_brain_init_status' not in st.session_state:
    st.session_state.aiml_engine = initialize_luna_brain()
    st.session_state.luna_brain_init_status = "initialized"

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    
    # Test ElevenLabs and set appropriate greeting
    if elevenlabs_client:
        test_success, test_message = test_elevenlabs_connection()
        if test_success:
            initial_greeting = "Kyaa~! Hello there, Master! ✨ My voice should work perfectly now! Let's chat! 🌟"
        else:
            initial_greeting = f"Kyaa~! Hello Master! ✨ My voice might be a bit shy today, but I'm still here to help! 💖"
    else:
        initial_greeting = "Kyaa~! Hello there, Master! ✨ I'm in text-only mode today, but still ready to help! 🌟"
    
    # Generate audio for initial greeting
    luna_audio_bytes = generate_luna_audio(initial_greeting) if elevenlabs_client else None
    
    st.session_state.chat_history.append({
        "sender": "Luna", 
        "text": initial_greeting, 
        "emotion": "excited",
        "audio_bytes": luna_audio_bytes
    })

if 'current_avatar_emotion' not in st.session_state:
    st.session_state.current_avatar_emotion = "excited"

# --- Sidebar ---
with st.sidebar:
    # Display avatar emoji
    current_emoji = get_avatar_emoji(st.session_state.current_avatar_emotion)
    st.markdown(f'<div class="avatar-large">{current_emoji}</div>', unsafe_allow_html=True)
    st.markdown("**Luna, your AI companion 💖**")
    
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
        st.caption("ElevenLabs API key missing or library not installed")
    
    st.markdown("---")
    st.markdown("🌸 **Luna's Abilities:**")
    st.markdown("- **Chat-chan:** Friendly conversations\n- **Emotion-kun:** Expressive responses\n- **Voice-sensei:** Text-to-speech (when available)")
    
    # Debug button
    if st.button("🔧 Test Voice", help="Test ElevenLabs voice generation"):
        if elevenlabs_client:
            test_text = "Hello! This is a voice test from Luna!"
            test_audio = generate_luna_audio(test_text)
            if test_audio:
                st.success("Voice test successful!")
                st.audio(test_audio, format="audio/mp3")
            else:
                st.error("Voice test failed!")
        else:
            st.error("Voice system not available!")

# --- Main Chat Logic ---
for msg in st.session_state.chat_history:
    role = "user" if msg["sender"] == "User" else "assistant"
    with st.chat_message(role):
        st.markdown(f'<div class="chat-bubble {role.lower()}">{msg["text"]}</div>', unsafe_allow_html=True)
        
        # Play audio if available
        if role == 'assistant' and msg.get("audio_bytes"):
            st.audio(msg["audio_bytes"], format="audio/mp3", autoplay=False)

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

        # Generate Luna's response using simple engine
        luna_response_text = st.session_state.aiml_engine.process(latest_user_input)

        # Determine emotion and generate audio
        luna_emotion = infer_emotion_from_text(luna_response_text)
        print(f"🎭 Luna emotion: {luna_emotion}")
        
        # Generate audio if available
        luna_audio_bytes = generate_luna_audio(luna_response_text) if elevenlabs_client else None
        print(f"🎤 Audio generated: {'Yes' if luna_audio_bytes else 'No'}")

        # Add Luna's response to chat history
        st.session_state.chat_history.append({
            "sender": "Luna", 
            "text": luna_response_text,
            "emotion": luna_emotion, 
            "audio_bytes": luna_audio_bytes
        })
        
        # Update state and rerun
        st.session_state.is_luna_processing = False
        st.session_state.current_avatar_emotion = luna_emotion
        st.rerun()