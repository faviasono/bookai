import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from collections import defaultdict
from transformers import pipeline

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
candidate_labels = ["about the author", "acknowledgements", "about the book", "table of content"]
def get_classification(text, eq=None, threshold=0.3):
    assert eq in candidate_labels if eq else True
    if not eq:
        return classifier(text, candidate_labels=candidate_labels)["labels"][0]
    else:
        res = classifier(text, candidate_labels=candidate_labels)
        return res["labels"][0] == eq if res["scores"][0] > threshold else None
# Function to read EPUB file
def read_epub(file_path, min_len_chapter=1000):
    chapter_cnt = 0
    result = defaultdict()
    book = epub.read_epub(file_path)

    result["title_of_book"] = book.title

    for item in book.get_items():
        # Check if item is of type document
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_body_content(), "html.parser")
            text_content = soup.get_text()

            if (
                not result.get("about_the_author")
                and len(text_content) < min_len_chapter
                and get_classification(text_content, "about the author")
            ):
                result["about_the_author"] = text_content
            elif (
                not result.get("acknowledgements")
                and len(text_content) < min_len_chapter
                and get_classification(text_content, "acknowledgements")
            ):
                result["acknowledgements"] = text_content
            elif (
                not result.get("about_the_book")
                and len(text_content) < min_len_chapter
                and get_classification(text_content, "about the book")
            ):
                result["about_the_book"] = text_content
            elif (
                not result.get("table_of_content")
                and len(text_content) < min_len_chapter
                and get_classification(text_content, "table of content")
            ):
                result["table_of_content"] = text_content
            elif len(text_content) > min_len_chapter:
                result[f"chapter_{chapter_cnt}"] = text_content
                chapter_cnt += 1

    return result, item


# Path to your EPUB file
file_path = "/Users/andreafavia/development/bookai/files/The Responsible Company.epub"


# Read and display the content
epub_content, item = read_epub(file_path)
print(epub_content)