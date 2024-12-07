# Use a pipeline as a high-level helper
from transformers import pipeline
from models.base_summarizer import SummarizerBaseModel

class HFBaseSummarizer(SummarizerBaseModel):
    def __init__(self, model_name: str = "sshleifer/distilbart-cnn-12-6"):
        self.pipe = pipeline("summarization", model=model_name)
    
    def summarize(self, text):
        prediction = self.pipe(text)
        return prediction[0]['summary_text']
    