from os.path import join, dirname
from dotenv import load_dotenv
from bookai.models.base_tts import BaseTts
import logging
from google.cloud import texttospeech

# Load the environment variables
load_dotenv(join(dirname(__file__), ".env"))


class GoogleTTS(BaseTts):
    def __init__(self, model_name="en-US-Neural2-D", credentials=None):
        self.client = texttospeech.TextToSpeechClient(credentials=credentials)

        self.model_name = model_name
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="",
            ssml_gender=texttospeech.SsmlVoiceGender.MALE,
        )
        self.audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    def clean_text(self, text):
        """Clean the text from any special characters"""
        text = text.replace("\n", " ")
        text = text.replace("\r", " ")
        text = text.replace("\t", " ")
        text = text.replace("**", "")
        text = text.replace("*", "")
        return text

    def synthesize(self, text):
        text = texttospeech.SynthesisInput(text=self.clean_text(text))
        try:
            return self.client.synthesize_speech(
                request={"input": text, "voice": self.voice, "audio_config": self.audio_config}
            ).audio_content
        except Exception as e:
            logging.error(f"Error synthesizing text: {str(e)}")
            return None
