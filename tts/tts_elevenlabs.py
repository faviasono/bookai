from os.path import join, dirname
from dotenv import load_dotenv
from bookai.models.base_tts import BaseTts

from elevenlabs import ElevenLabs, play


# Load the environment variables
load_dotenv(join(dirname(__file__), ".env"))


class ElevenLabsTTS(BaseTts):
    def __init__(self, model_name="eleven_multilingual_v2", voice_id="21m00Tcm4TlvDq8ikWAM"):
        self.client = ElevenLabs()
        self.model_name = model_name
        self.voice_id = voice_id

    def synthesize(self, text):
        return self.client.text_to_speech.convert(
            voice_id=self.voice_id,
            model_id=self.model_name,
            text=text,
        )
