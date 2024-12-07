import os
import requests
from os.path import join, dirname
from dotenv import load_dotenv
import logging

load_dotenv(join(dirname(__file__), "../", ".env"), verbose=True)


API_KEY = os.getenv("BIONIC_API_KEY")


class BionicReader:
    def __init__(self, fixations: int = 2, saccades: int = 20):
        self.url = "https://bionic-reading1.p.rapidapi.com/convert"
        self.header = {
            "x-rapidapi-key": API_KEY,
            "x-rapidapi-host": "bionic-reading1.p.rapidapi.com",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        self.fixations = fixations
        self.saccades = saccades

    def convert(self, text: str):
        payload = {
            "content": text,
            "response_type": "html",
            "request_type": "html",
            "fixation": self.fixations,
            "saccade": self.saccades,
        }
        response = requests.post(self.url, data=payload, headers=self.header)
        if response.status_code != 200:
            logging.error(f"Error converting text: {response.text}")
            return text
        logging.info("Converted text to Bionic Reading")
        return response.text


if __name__ == "__main__":
    reader = BionicReader()
    text = "The quick brown fox jumps over the lazy dog."
    print(reader.convert(text))
