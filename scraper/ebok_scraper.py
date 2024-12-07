# import ebooklib
# from ebooklib import epub
# from bs4 import BeautifulSoup
# from collections import defaultdict
# from transformers import pipeline

# ABOUT_AUTHOR = "about the author"
# ACKNOWLEDGEMENTS = "acknowledgements"
# ABOUT_BOOK = "about the book"
# TABLE_OF_CONTENT = "table of content"
# CHAPTER = "chapter"


# class BookScraper:

#     def __init__(self):
#         self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
#         self.candidate_labels = ["about the author", "acknowledgements", "about the book", "table of content"]


#     def get_classification(self,text, eq=None, threshold=0.3):
#         assert eq in self.candidate_labels if eq else True
#         results = self.classifier(text, candidate_labels=self.candidate_labels)
#         if not eq:
#             return results["labels"][0]
#         else:
#             return results["labels"][0] == eq if results["scores"][0] > threshold else None
    
#     def is_about_author(self, item: epub.EpubItem, text_content: str) -> bool:
#         if "about_author" in item.get_id() or "author" in item.get_id():
#             return True
#         if self.get_classification(text_content, "about the author"):
#             return True
#         return False
    
#     def is_acknowledgements(self, item: epub.EpubItem, text_content) -> bool:
#         if "acknowledgements" in item.get_id():
#             return True
#         if self.get_classification(text_content, "acknowledgements"):
#             return True
#         return False
    
#     def is_about_book(self, item: epub.EpubItem, text_content) -> bool:
#         if "about_book" in item.get_id():
#             return True
#         if BookScraper.get_classification(text_content, "about the book"):
#             return True
#         return False
    
#     def is_table_of_content(self, item: epub.EpubItem, text_content) -> bool:
#         if "table_of_content" in item.get_id():
#             return True
#         if self.get_classification(text_content, "table of content"):
#             return True
#         return False
    
#     def is_a_chapter(self, item: epub.EpubItem, text_content) -> bool:
#         if "chapter" in item.get_id():
#             return True
#         if len(text_content) > 1000:
#             return True
    



# scraper = BookScraper()


    
# # Function to read EPUB file
# def read_epub(file_path, min_len_chapter=1000):
#     chapter_cnt = 0
#     result = defaultdict()
#     book = epub.read_epub(file_path)

#     result["title_of_book"] = book.title

#     for item in book.get_items():
#         # Check if item is of type document
#         if item.get_type() == ebooklib.ITEM_DOCUMENT:
#             soup = BeautifulSoup(item.get_body_content(), "html.parser")
#             text_content = soup.get_text()

#             if not result.get(ABOUT_AUTHOR) and scraper.is_about_author(item, text_content):
#                 result[ABOUT_AUTHOR] = text_content
#             elif not result.get(ACKNOWLEDGEMENTS) and scraper.is_acknowledgements(item, text_content):
#                 result[ACKNOWLEDGEMENTS] = text_content
#             elif not result.get(ABOUT_BOOK) and scraper.is_about_book(item, text_content):
#                 result[ABOUT_BOOK] = text_content
#             elif scraper.is_a_chapter(item, text_content):
#                 result[f"{CHAPTER}_{chapter_cnt}"] = text_content
#                 chapter_cnt += 1
#             elif not result.get(TABLE_OF_CONTENT) and scraper.is_table_of_content(item, text_content):
#                 result[TABLE_OF_CONTENT] = text_content

#     return result


# # Path to your EPUB file
# file_path = "/Users/andreafavia/development/bookai/files/21 Lessons for the 21st Century (Yuva... (z-lib.org).epub"


# # Read and display the content
# epub_content = read_epub(file_path)
# import pprint
# pprint.pprint(epub_content)

from ebooklib import epub
import re
from typing import List, Dict, Union

def is_potential_chapter(title: str) -> bool:
    """
    Determine if a given title is likely to be a chapter based on patterns and keywords.
    
    Args:
        title (str): The title of the section.
    
    Returns:
        bool: True if it is likely a chapter, False otherwise.
    """
    # Define keywords for non-chapter sections
    non_chapter_keywords = [
        "Acknowledgments","Acknowledgements", "Index", "Notes", "About the", "Dedication", 
        "Title Page", "Copyright", "Contents", "Cover", "Index", "Contents","Notes","List of", "Annex",
        "Also by", "Foreword", "Preface", "Appendix", "Glossary", "Bibliography",
        "Introduction", "Prologue", "Epilogue", "Afterword", "Appendix", "Endnotes", "Footnotes",
        "References", "Further Reading", "Permissions", "Colophon", "Errata", "Erratum",
        "Errata Corrige", "Errata Sheet", "Erratum Sheet", "Errata Slip", "Erratum Slip",
        "Copyright", "About the Author", "About the Translator", "About the Editor", "Note to the Reader",
        "Credits", "List of Illustrations", "List of Tables", "List of Figures", "List of Maps",
        "Epigraph", "Table of Cases", "Table of Statutes", "Table of Authorities", "Table of Abbreviations",
        "Note", "Translator's Note", "Editor's Note", "Editorial Note", "Publisher's Note",
        "Buy the book", "Recommended Reading", "About the Series", "About the Publisher", "About the Cover",
    ]
    
    # Check for keywords indicating non-chapter sections
    if any(keyword.lower() in title.lower() for keyword in non_chapter_keywords):
        return False

    # Check for chapter-like patterns (e.g., numbers or "Chapter")
    if re.search(r'^(Chapter|[0-9]+(\.|:))', title, re.IGNORECASE):
        return True

    # If no clear indicators, consider it a chapter by default
    return True

def get_chapters_with_uids(toc: List[Union[epub.Link, tuple]]) -> Dict[str, str]:
    """
    Extract chapters and their UIDs from the Table of Contents (TOC) of an EPUB book.

    Args:
        toc (List[Union[epub.Link, tuple]]): The TOC of the EPUB book, containing Links and Sections.

    Returns:
        Dict[str, str]: A dictionary where keys are chapter titles and values are their UIDs.
    """
    chapters = {}

    def extract_links(items: List[Union[epub.Link, tuple]]):
        for item in items:
            if isinstance(item, epub.Link):
                if is_potential_chapter(item.title):
                    chapters[item.title] = item.uid
            elif isinstance(item, tuple) and isinstance(item[0], epub.Section):
                # If the item is a Section, process its links recursively
                extract_links(item[1])

    extract_links(toc)
    return chapters

# Usage example
# Assuming `book` is an ebooklib.epub.EpubBook object
book = epub.read_epub("/Users/andreafavia/development/bookai/files/The Responsible Company.epub")
toc = book.toc
chapter_uids = get_chapters_with_uids(toc)

print("\n\n")
# Print results
for title, uid in chapter_uids.items():
    print(f"{title}, UID: {uid}")



# TODO: Save chapters only  +  metadata + analyse text withs ummarization + indexing for LLM