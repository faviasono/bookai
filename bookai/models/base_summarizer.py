class SummarizationException(Exception):
    pass


class SummarizerBaseModel:
    def summarize(self, text):
        raise NotImplementedError


class Summarizer:
    def __init__(self, model: SummarizerBaseModel):
        self.model = model

    def summarize(self, text):
        try:
            return self.model.summarize(text)
        except Exception as e:
            raise SummarizationException(f"Error summarizing text: {str(e)}")
