from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, Document
from llama_index.llms.gemini import Gemini
import os
from os.path import join, dirname
from dotenv import load_dotenv
import time

load_dotenv(join(dirname(__file__), "../", ".env"))


class DictReader:
    def __init__(self, chapters_dict):
        self.chapters_dict = chapters_dict

    @staticmethod
    def create_document(item):
        title, content = item
        return Document(text=content, metadata={"chapter": title})

    def load_data(self):
        documents = [self.create_document(item) for item in self.chapters_dict.items()]
        return documents


class QuestionAnsweringBook:
    def __init__(self, chapters_dict, embedding_model, gemini_model, gemini_api_key=None):
        self.reader = DictReader(chapters_dict)
        self.documents = self.reader.load_data()
        self.embedding_model = (
            HuggingFaceEmbedding(model_name=embedding_model) if isinstance(embedding_model, str) else embedding_model
        )
        self.index = VectorStoreIndex.from_documents(self.documents, embed_model=self.embedding_model, show_progress=False)
        self.llm = (
            Gemini(
                model=gemini_model,
                api_key=gemini_api_key if gemini_api_key else os.environ.get("GEMINI_API_KEY"),
            )
            if isinstance(gemini_model, str)
            else gemini_model
        )
        self.query_engine = self.index.as_query_engine(llm=self.llm, streaming=True)

    def query(self, question):
        return self.query_engine.query(question)


if __name__ == "__main__":
    chapters_dict = {
        "Chapter 1": "Tim Cook was born on November 1, 1960, in Mobile, Alabama, United States.",
        "Chapter 2": "Tim Cook joined Apple in March 1998 as Senior Vice President for Worldwide Operations.",
        "Chapter 3": "Tim Cook became the CEO of Apple Inc. on August 24, 2011.",
    }

    # Example usage
    qa_book = QuestionAnsweringBook(
        chapters_dict=chapters_dict,
        embedding_model="BAAI/bge-small-en-v1.5",
        gemini_model="models/gemini-1.5-flash",
        gemini_api_key=os.environ.get("GEMINI_API_KEY"),
    )

    time_start = time.time()
    streaming_response = qa_book.query("In which chapter they talk about Tim Cook's birthplace?")
    streaming_response.print_response_stream()
    print(f"Time taken: {time.time() - time_start} seconds")
