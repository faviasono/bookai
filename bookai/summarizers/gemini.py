import os
from os.path import join, dirname
import google.generativeai as genai
from dotenv import load_dotenv
from bookai.models.base_summarizer import SummarizerBaseModel

# Load the environment variables
load_dotenv(join(dirname(__file__), "../", ".env"))

SYSTEM_INSTRUCTIONS = 'You are a non-fictional book chapter summarizer. I will give you a single chapter as input. You should present the concept in an interesting way, without saying the sentences such as "This chapter .." or "The author ..." - just think about creating a script for a podcaster. but without writing anything about podcast (e.g., "hey Podcaster"). Focus on the main concepts and provide an engaging but clear and professional narrative.It should be about 20% of original length that takes 80% of the most important concepts. Do not return markdowns, HTML tags, apostrophes or underscores - just plain text.'
REFLECTION_POINTS_PROMPT = "Can you provide a reflection points based on the summaries of all the chapters?"


class Gemini(SummarizerBaseModel):
    def __init__(self, model_name="gemini-1.5-flash-8b", temperature=1, top_p=0.95, top_k=40, max_output_tokens=8192):
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        # Create the model
        generation_config = {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "max_output_tokens": max_output_tokens,
            "response_mime_type": "text/plain",
        }
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            system_instruction=SYSTEM_INSTRUCTIONS,
        )

    def summarize(self, text):
        chat_session = self.model.start_chat(history=[])
        response = chat_session.send_message(text)
        return response.text

    def create_reflection(self, history=[]):  # TODO: test and check  funtionality
        chat_session = self.model.start_chat(history=history)
        response = chat_session.send_message(REFLECTION_POINTS_PROMPT)
        return response.text
