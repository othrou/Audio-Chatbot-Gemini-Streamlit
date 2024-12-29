import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from streamlit_extras.add_vertical_space import add_vertical_space
import sounddevice as sd
import soundfile as sf
from googletrans import Translator

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Sidebar contents
with st.sidebar:
    st.image("ensias.png", width=200)
    st.title('Audio - Chatbot💬')
    st.markdown('''
    ## About APP:

    The app's primary resources are utilised to create:

    - [Streamlit](https://streamlit.io/)
    - [Gemini](https://ai.google.dev/tutorials/python_quickstart#chat_conversations)

    ## About this project:

    - This project was created by O.ROUGUI and Z.ZHAR in the context of the Multimedia Data Processing course.
    ''')
    add_vertical_space(1)
    st.write('💡All about Gemini exploration: Gemini is a multimodal LLM that can be used to generate text and voice... :)')

# Initialize session state variables
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = ""
if 'generated_text' not in st.session_state:
    st.session_state.generated_text = ""
if 'translation' not in st.session_state:
    st.session_state.translation = ""

# List available models
models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

# Streamlit app
st.title("Multimedia Data Processing: Audio Transcription and Translation💬")
st.subheader("Gemini Audio Chatbot")
st.write("By: Othmane ROUGUI & Zahra ZHAR")
st.info("This project aims to create an audio chatbot that detects the voice, identifies the language, transcribes the audio, generates a response, and translates it into a target language.")

# Model selection
selected_model = st.selectbox("Select a Generative Model", models)

# Real-time audio input and speech-to-text conversion
fs = 16000  # Sample rate
duration = 10  # Recording duration in seconds

# Check if the user has submitted audio
submitted = st.button("Speak and Submit")

if submitted:
    st.write("Speak now...")

    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait for recording to finish

    # Save the recorded audio to a temporary file
    temp_file = "temp.wav"
    sf.write(temp_file, recording, fs)

    try:
        # Upload the file to Gemini
        myfile = genai.upload_file(temp_file)
        if myfile:
            st.write(f"File uploaded")

        # Use Gemini for transcription
        model = genai.GenerativeModel("gemini-1.5-flash")

        response = model.generate_content([myfile, "Transcript the audio file and detect the language"])

        st.session_state.transcribed_text = response.text
        st.subheader("Transcription :")
        st.write(response.text)
    except Exception as e:
        st.error(f"An error occurred during transcription: {e}")

    # Display transcribed text
    #st.subheader("Transcribed Text:")
    #st.write(st.session_state.transcribed_text)

    # Generate content using Gemini
    response = model.generate_content(f"Generate a response based on this transcription: {st.session_state.transcribed_text}")

    # Store and display generated content
    st.session_state.generated_text = response.text
    st.subheader("Generated Content:")
    st.write(st.session_state.generated_text)

    # Clean up the temporary audio file
    os.remove(temp_file)


# Translation step
st.subheader("Translation:")
dest_lang = st.selectbox("Select destination language", ["Arabic", "English", "French", "Hindi", "Telugu", "Punjabi", "German"])
translate_button = st.button("Translate")

if translate_button and st.session_state.generated_text:
    dest_lang_code = {
        "Arabic": "ar",
        "English": "en",
        "French": "fr",
        "Hindi": "hi",
        "Telugu": "te",
        "Punjabi": "pa",
        "German": "de"
    }.get(dest_lang)

    try:
        translator = Translator()
        translation = translator.translate(st.session_state.generated_text, dest=dest_lang_code)
        st.session_state.translation = translation.text
    except Exception as e:
        st.error(f"An error occurred during translation: {str(e)}")

if st.session_state.translation:
    st.subheader("Translated Answer:")
    st.write(f"**Translated Answer ({dest_lang}):** {st.session_state.translation}")
