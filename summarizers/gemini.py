import os
from os.path import join, dirname
import google.generativeai as genai
from dotenv import load_dotenv
from models.base_summarizer import SummarizerBaseModel
# Load the environment variables
load_dotenv(join(dirname(__file__), '.env'))

SYSTEM_INSTRUCTIONS = "You are a non-fictional book chapter summarizer.  Focus on the main concepts, use paragraphs (without writing paragraph) to separate concepts within the same chapter and get the most important aspect of each chapter. Also, end with a Conclusion paragraph.\nIt should be about 20% of original length that takes 80% of the most important concepts\n"


class Gemini(SummarizerBaseModel):
    def __init__(self, model_name = "gemini-1.5-flash-8b", temperature=1, top_p=0.95, top_k=40, max_output_tokens=8192):
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
        chat_session = self.model.start_chat(
            history=[
                
            ]
        )
        response = chat_session.send_message(text)
        return response.text
