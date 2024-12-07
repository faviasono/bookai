class BaseTts:
    def __init__(self, model):
        self.model = model

    def synthesize(self, text: str):
        raise NotImplementedError
