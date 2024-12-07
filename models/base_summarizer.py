
class SummarizerBaseModel:
    def summarize(self, text):
        raise NotImplementedError

class Summarizer:

    def __init__(self, model: SummarizerBaseModel):
        self.model = model
    
    def summarize(self, text):
        return self.model.summarize(text)
