# https://blog.futuresmart.ai/building-a-conversational-voice-chatbot-integrating-openais-speech-to-text-text-to-speech
# Reference: See above

import base64
import streamlit as st

import os
import openai
from openai import AzureOpenAI
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

load_dotenv(".env")

# Ensure the environment variables are set correctly
speech_key = os.environ.get('AZURE_SPEECH_KEY')
speech_region = os.environ.get('AZURE_SPEECH_REGION')
if not speech_key or not speech_region:
    raise ValueError("Please set the 'AZURE_SPEECH_KEY' and 'AZURE_SPEECH_REGION' environment variables.")

# Create the speech configuration
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
# Create an audio configuration to use the default speaker
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
# The neural multilingual voice can speak different languages based on the input text.
speech_config.speech_synthesis_voice_name='en-US-AvaMultilingualNeural'

api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("OPENAI_API_VERSION")

client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=azure_endpoint)

def speech_to_text(audio_data):
    with open(audio_data, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper",
            response_format="text",
            file=audio_file
        )
    return transcript

def text_to_speech(input_text, option='azure'):
    mp3_file_path = "temp_audio_play.mp3"
    if option == 'azure':
        audio_config = speechsdk.audio.AudioOutputConfig(filename=mp3_file_path)
        # Create a speech synthesizer with the specified audio output
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        # Perform text-to-speech synthesis
        speech_synthesis_result = speech_synthesizer.speak_text_async(input_text).get()

        # Check the result and handle errors
        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Speech synthesized and saved to file: {mp3_file_path}")
            return mp3_file_path
    elif option == 'openai':
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=input_text
        )
        webm_file_path = "temp_audio_play.mp3"
        with open(webm_file_path, "wb") as f:
            response.stream_to_file(webm_file_path)
        return webm_file_path
    
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    md = f"""
    <audio autoplay>
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)