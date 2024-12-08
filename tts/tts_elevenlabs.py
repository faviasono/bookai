from os.path import join, dirname
from dotenv import load_dotenv
from bookai.models.base_tts import BaseTts
import logging
from elevenlabs import ElevenLabs


# Load the environment variables
load_dotenv(join(dirname(__file__), ".env"))


class ElevenLabsTTS(BaseTts):
    def __init__(self, model_name="eleven_multilingual_v2", voice_id="nPczCjzI2devNBz1zQrb"):
        self.client = ElevenLabs()
        self.model_name = model_name
        self.voice_id = voice_id

    def clean_text(self, text):
        """Clean the text from any special characters"""
        text = text.replace("\n", " ")
        text = text.replace("\r", " ")
        text = text.replace("\t", " ")
        return text

    def synthesize(self, text):
        try:
            return self.client.text_to_speech.convert(
                voice_id=self.voice_id,
                model_id=self.model_name,
                text=self.clean_text(text),
            )
        except Exception as e:
            logging.error(f"Error synthesizing text: {str(e)}")
            return None
