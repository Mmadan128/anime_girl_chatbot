# app.py
import streamlit as st
import os
import re
import random
import time
import shutil # For cleaning up directories

# Import gTTS for dynamic text-to-speech
from gtts import gTTS
# Removed 'from gtts.tts import gTTSLangError' as it's causing the ImportError.
# We will catch a more general Exception for gTTS failures.
from typing import Optional # For type hinting

# Import core components from your luna_agent.py
# Make sure luna_agent.py is in the same directory
try:
    from luna_agent import LunaAIMLEngine, create_luna_agent
except ImportError as e:
    st.error(f"Waaah! Luna can't find her main brain module! 😱 Error: {e}")
    st.info("Please make sure 'luna_agent.py' is in the same directory as 'app.py'!")
    st.stop() # Stop the app if core logic isn't found

# --- Streamlit Page Configuration (MUST BE THE FIRST STREAMLIT COMMAND) ---
# This ensures it runs only once and at the very beginning of the script execution.
st.set_page_config(
    page_title="Luna - Anime AI Assistant 🌸",
    page_icon="🌸",
    layout="centered"
)

# --- Configuration ---
AVATAR_BASE_PATH = 'avatars/' # Path to your avatar images
TEMP_AUDIO_DIR = 'temp_audio_luna/' # Directory for gTTS generated audio files
DEFAULT_AVATAR_EMOTION = 'idle'

# Define avatar image map for emotions
# Ensure these files exist in your 'avatars/' directory!
AVATAR_IMAGE_MAP = {
    'idle': 'luna_idle.png',
    'speaking': 'luna_speaking.png',
    'happy': 'luna_happy.png',
    'excited': 'luna_excited.png',
    'mischievous': 'luna_mischievous.png',
    'curious': 'luna_curious.png',
    'sad': 'luna_sad.png',
    'confused': 'luna_confused.png',
    'thinking': 'luna_thinking.png',
    'energetic': 'luna_excited.png'
}

# --- Helper Function for Emotion Inference ---
def infer_emotion_from_text(text: str) -> str:
    """
    A simple function to infer Luna's emotion based on keywords and emojis.
    This can be greatly expanded with more advanced NLP or sentiment analysis.
    """
    text_lower = text.lower()
    
    # Positive/Excited
    if "kyaa~!" in text_lower or "yay!" in text_lower or "excited!" in text_lower or "amazing!" in text_lower or "happy" in text_lower or "love" in text_lower or "✨" in text or "🌸" in text or "💖" in text or "🌟" in text:
        return random.choice(["happy", "excited", "energetic"])
    # Mischievous/Playful
    if "hehe!" in text_lower or "mischievous" in text_lower or "teasing" in text_lower:
        return "mischievous"
    # Curious
    if "ooh!" in text_lower or "curious" in text_lower or "mystery" in text_lower:
        return "curious"
    # Sad/Aww
    if "aww..." in text_lower or "waaah!" in text_lower or "miss" in text_lower or "sorry" in text_lower:
        return "sad"
    # Confused/Oops
    if "eeeek!" in text_lower or "confused" in text_lower or "problem" in text_lower or "oops" in text_lower:
        return "confused"
    # Default
    return "speaking"

def get_avatar_image_path(emotion: str) -> str:
    """
    Returns the full path to the avatar image for a given emotion.
    Includes a fallback to the idle avatar if a specific emotion's image is missing.
    """
    filename = AVATAR_IMAGE_MAP.get(emotion)
    full_path = os.path.join(AVATAR_BASE_PATH, filename if filename else AVATAR_IMAGE_MAP[DEFAULT_AVATAR_EMOTION])
    
    if not os.path.exists(full_path):
        st.warning(f"Could not find avatar file: '{full_path}'. Falling back to default idle image.")
        return os.path.join(AVATAR_BASE_PATH, AVATAR_IMAGE_MAP[DEFAULT_AVATAR_EMOTION])
    return full_path

def generate_luna_audio(text: str, emotion: str) -> Optional[str]:
    """
    Generates an MP3 audio file using gTTS and returns its path.
    The 'emotion' parameter is currently not used by gTTS but kept for future TTS APIs.
    """
    if not text.strip(): # gTTS can fail on empty strings
        return None

    try:
        os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
        
        # Simple language detection for gTTS, default to English
        lang = 'en'
        # A more robust solution would use a proper language detection library
        # For gTTS, we generally stick to 'en' or other common languages.
        # If the text contains a lot of Japanese characters, gTTS might auto-detect
        # or require explicit lang='ja'. For now, a simple check.
        if re.search(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]', text): # Check for Japanese/Chinese characters
             lang = 'ja'
        
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Create a unique temporary file name
        temp_audio_filename = os.path.join(TEMP_AUDIO_DIR, f"luna_response_{int(time.time() * 1000)}_{random.randint(0, 9999)}.mp3")
        tts.save(temp_audio_filename)
        return temp_audio_filename
    except Exception as e: # Catching a general Exception for robustness
        st.error(f"Waaah! Luna's voice box got tangled! (gTTS error: {e}) No audio for this message. 🤫")
        return None

def cleanup_temp_audio(age_seconds=3600): # Clean files older than 1 hour
    """Removes old temporary audio files."""
    if os.path.exists(TEMP_AUDIO_DIR):
        now = time.time()
        for filename in os.listdir(TEMP_AUDIO_DIR):
            filepath = os.path.join(TEMP_AUDIO_DIR, filename)
            if os.path.isfile(filepath):
                if os.stat(filepath).st_mtime < now - age_seconds:
                    try:
                        os.remove(filepath)
                        # print(f"Cleaned up old audio file: {filename}") # Uncomment for debugging cleanup
                    except Exception as e:
                        print(f"Error cleaning up {filename}: {e}")
    
    # Also clean the directory itself if it's empty
    if os.path.exists(TEMP_AUDIO_DIR) and not os.listdir(TEMP_AUDIO_DIR):
        try:
            os.rmdir(TEMP_AUDIO_DIR)
        except Exception as e:
            print(f"Error removing empty audio directory {TEMP_AUDIO_DIR}: {e}")

# --- Caching Luna's Brain (LLM Agent and AIML Engine) ---
@st.cache_resource
def initialize_luna_brain():
    """Initializes Luna's AIML engine and LangChain agent."""
    aiml_engine = LunaAIMLEngine()
    
    try:
        agent_executor = create_luna_agent()
        return aiml_engine, agent_executor, None # No error message if successful
    except Exception as e:
        error_msg = f"Waaah! Luna's main brain had a big stumble during initialization! 😱 Error: {e}"
        st.error(error_msg)
        st.info("💡 Please check your `GOOGLE_API_KEY` in the `.env` file and ensure all dependencies are installed. (You might need to restart the Streamlit app after fixing).")
        return aiml_engine, None, error_msg # Return error message

# --- Custom CSS for app styling ---
st.markdown(
    """
    <style>
    /* General background for the entire Streamlit app */
    .stApp {
        background-color: #fce4ec; /* Light pink overall background */
    }
    /* Styling for the main content container (the white card) */
    div[data-testid="stVerticalBlock"] > div:first-child { 
        background-color: #fff;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    /* Custom header for the app title */
    h1.st-emotion-cache-1pxairm { /* Targets the h1 title element */
        background-color: #ff80ab; /* Bright pink header */
        color: white;
        padding: 15px 25px;
        font-size: 1.8em; /* Slightly larger title */
        font-weight: bold;
        text-align: center;
        border-bottom: 2px solid #e91e63;
        border-radius: 10px 10px 0 0; /* Match container border-radius */
        margin-top: -20px; /* Adjust to sit at top of the white container */
        margin-left: -20px;
        margin-right: -20px;
        margin-bottom: 20px;
    }

    /* Chat message container styling */
    div[data-testid="chatMessage"] {
        margin-bottom: 0.5rem; /* Space between messages */
        margin-top: 0.5rem;
        padding: 0; 
        display: flex; /* Flexbox for alignment */
    }
    div[data-testid="stChatMessageContent"] {
        padding: 0; /* Remove default padding */
        background: none; /* Remove default background */
    }
    
    .chat-bubble { /* Generic bubble styling */
        padding: 12px 18px;
        border-radius: 18px;
        line-height: 1.5;
        word-wrap: break-word;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        max-width: 80%; /* Limit message width */
        margin: 5px 0; /* Spacing */
        color: #333 !important; /* Ensure chat text itself is dark and visible */
    }
    .chat-bubble.user {
        background-color: #ffcdd2; /* Light user bubble */
        color: #4a148c !important; /* Dark purple text */
        margin-left: auto; /* Align to right */
        border-bottom-right-radius: 2px;
    }
    .chat-bubble.luna {
        background-color: #e0f2f7; /* Light Luna bubble */
        color: #004d40 !important; /* Dark teal text */
        margin-right: auto; /* Align to left */
        border-bottom-left-radius: 2px;
    }

    /* Custom avatar for chat messages (hide Streamlit's default) */
    div[data-testid="chatMessage"] img { 
        display: none;
    }
    div[data-testid="chatMessage"] [data-testid="stImage"] { 
        display: none;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #ffb3c1; /* Lighter pink sidebar */
        border-right: 2px solid #e91e63;
    }
    [data-testid="stSidebar"] img {
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        margin-bottom: 15px;
    }

    /* St.audio styling */
    div[data-testid="stAudio"] { /* Targets the st.audio container */
        margin-top: 5px; /* Space above audio player */
        border-radius: 10px;
        background-color: rgba(255, 255, 255, 0.7); /* Slightly transparent background */
        padding: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Luna's Chat Room 🌸")

# --- Initialize Session State (if not already done) ---
if 'luna_brain_init_status' not in st.session_state:
    st.session_state.aiml_engine, st.session_state.agent_executor, st.session_state.init_error = initialize_luna_brain()
    st.session_state.luna_brain_init_status = "initialized" if not st.session_state.init_error else "failed"

    # If there's an initialization error, display it and potentially stop
    if st.session_state.init_error:
        # initialize_luna_brain already calls st.error and st.info, so we just pass here.
        # The app will continue, but the agent_executor will be None.
        pass

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    # Initial greeting from Luna
    initial_greeting_text = "Kyaa~! Hello there, Master! ✨ This Luna is super excited to meet you! I have lots of amazing tools to help you with anything you need! Hehe! 🌟"
    st.session_state.chat_history.append({
        "sender": "Luna",
        "text": initial_greeting_text,
        "emotion": "excited",
        "audio_url": generate_luna_audio(initial_greeting_text, "excited")
    })

if 'current_avatar_emotion' not in st.session_state:
    st.session_state.current_avatar_emotion = DEFAULT_AVATAR_EMOTION

# --- Sidebar for Luna's Avatar and Info ---
with st.sidebar:
    st.image(get_avatar_image_path(st.session_state.current_avatar_emotion), 
             caption="Luna, your AI companion 💖", use_container_width=True) 
    
    st.markdown("---")
    st.markdown("🎵 **Background Music (Conceptual):**")
    st.markdown("_(In a full app, Luna would have cute background music here!)_")
    # Example: if os.path.exists("audio/luna_theme.mp3"):
    #             st.audio("audio/luna_theme.mp3", format="audio/mp3", loop=True)
    #           else:
    #             st.info("Place 'luna_theme.mp3' in the audio/ folder for background music!")
    
    st.markdown("---")
    st.markdown("🌸 **Luna's Abilities:**")
    st.markdown("- **Search-chan:** Web searches")
    st.markdown("- **Calc-kun:** Math wizardry")
    st.markdown("- **Muse-sensei:** Creative writing")
    st.markdown("- **Translate-kun:** Language expert")
    st.markdown("- **Memo-chan:** Reminders (simulated)")
    st.markdown("---")
    st.markdown("💖 Ask Luna anything! (e.g., 'What's the capital of France?', 'Calculate 15*8+2', 'Tell me a short story about a brave cat')")

# --- Display Chat History ---
for chat_message in st.session_state.chat_history:
    if chat_message["sender"] == "User":
        with st.chat_message("user"):
            st.markdown(f'<div class="chat-bubble user">{chat_message["text"]}</div>', unsafe_allow_html=True)
    else: # Sender is Luna
        with st.chat_message("assistant"):
            st.markdown(f'<div class="chat-bubble luna">{chat_message["text"]}</div>', unsafe_allow_html=True)
            # Play audio if available and the file actually exists
            if 'audio_url' in chat_message and chat_message['audio_url'] and os.path.exists(chat_message['audio_url']):
                st.audio(chat_message['audio_url'], format="audio/mp3", autoplay=True, loop=False)
            # else:
                # If no audio or file not found, we don't display an empty audio player,
                # just the text.

# --- User Input ---
# The key ensures that Streamlit treats this input widget uniquely across reruns
user_input = st.chat_input("Type your message, Master...", key="chat_input_widget")

if user_input:
    # 1. Add user message to history
    st.session_state.chat_history.append({"sender": "User", "text": user_input})
    
    # 2. Update avatar to 'thinking'
    st.session_state.current_avatar_emotion = 'thinking'
    
    # This rerun displays the user's message and the 'thinking' avatar immediately
    st.rerun()

# --- Processing Luna's Response ---
# This block runs *if* the last message in history is from the User
# AND Luna has not yet responded to it.
if st.session_state.chat_history and st.session_state.chat_history[-1]["sender"] == "User":
    # This check ensures we only process the *most recent* user message once.
    # We use a session state flag `is_luna_processing` for more explicit control.
    if not st.session_state.get('is_luna_processing', False):
        st.session_state.is_luna_processing = True # Set flag to prevent re-entry

        latest_user_input = st.session_state.chat_history[-1]["text"]

        with st.chat_message("assistant"):
            # Display a thinking message while processing
            with st.spinner("💖 Luna is thinking... Hehe! ✨"):
                luna_response_text = ""
                luna_emotion = DEFAULT_AVATAR_EMOTION
                luna_audio_url = None

                try:
                    # First, try the AIML engine for quick responses
                    aiml_response = st.session_state.aiml_engine.process(latest_user_input)
                    
                    if aiml_response:
                        luna_response_text = aiml_response
                        luna_emotion = infer_emotion_from_text(luna_response_text)
                    else:
                        # If no AIML match, use the LangChain agent for complex tasks
                        if st.session_state.agent_executor:
                            response = st.session_state.agent_executor.invoke({"input": latest_user_input})
                            luna_response_text = response['output']
                            luna_emotion = infer_emotion_from_text(luna_response_text)
                        else:
                            luna_response_text = "Waaah! Luna's main brain isn't working right now! 😱 Can you try again later, Master?"
                            luna_emotion = "sad"
                    
                    # Generate audio for Luna's response
                    luna_audio_url = generate_luna_audio(luna_response_text, luna_emotion)

                except Exception as e:
                    luna_response_text = f"Eeeek! Luna encountered a tiny problem! {str(e)} But don't worry, this Luna is resilient! Let's try again! 💖"
                    luna_emotion = "confused"
                    luna_audio_url = generate_luna_audio(luna_response_text, luna_emotion) # Still try to speak the error message


            # 3. Add Luna's complete response to chat history
            st.session_state.chat_history.append({
                "sender": "Luna",
                "text": luna_response_text,
                "emotion": luna_emotion,
                "audio_url": luna_audio_url
            })
            
            # The chat history is re-rendered above, so Luna's message will appear there.
            
            # 4. Reset processing flag and update avatar for next interaction
            st.session_state.is_luna_processing = False # Allow new user input to be processed
            st.session_state.current_avatar_emotion = luna_emotion # Set avatar based on Luna's response
            st.rerun() # This final rerun updates the sidebar avatar and ensures audio plays

# Any code here runs after all primary app logic, typically for global cleanup or final checks.
if __name__ == "__main__":
    # Ensure temporary audio directory exists and clean up old files
    os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
    cleanup_temp_audio()
    
    # Check for placeholder avatar images existence
    if not os.path.exists(os.path.join(AVATAR_BASE_PATH, AVATAR_IMAGE_MAP[DEFAULT_AVATAR_EMOTION])):
        st.error(
            f"Waaah! No default avatar image '{AVATAR_IMAGE_MAP[DEFAULT_AVATAR_EMOTION]}' found in '{AVATAR_BASE_PATH}'. "
            "Please add an image to start Luna! 😱"
        )
        st.stop() # Stop the app if crucial images are missing
    
    # The main app logic is now defined directly in the script, not inside a main() function call here.
