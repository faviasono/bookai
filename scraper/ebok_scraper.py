from ebooklib import epub
import re
from typing import List, Dict, Union
from transformers import pipeline
import warnings
warnings.filterwarnings("ignore")

# TODO: Save chapters only  +  metadata + analyse text withs ummarization + indexing for LLM

class EbookScraper:

    def __init__(self,epub_path: str,  zero_shot_classifier_model_hf: str = "facebook/bart-large-mnli"):
        self.epub = self._load_epub(epub_path)
        self.classifier = pipeline("zero-shot-classification", model=zero_shot_classifier_model_hf)
        self.candidate_labels = ["about the author", "acknowledgements", "about the book", "table of content"]
        self.chapters_idx = self._get_chapters_with_uids(self.epub.toc)

    @staticmethod
    def _load_epub(epub_path):
        try:
            return epub.read_epub(epub_path)
        except Exception as e:
            raise Exception(f"Error loading EPUB file: {str(e)}")

    def _get_chapters_with_uids(self, toc: List[Union[epub.Link, tuple]]) -> Dict[str, str]:
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
                    if self.is_potential_chapter(item.title):
                        chapters[item.title] = item.uid
                elif isinstance(item, tuple) and isinstance(item[0], epub.Section):
                    # If the item is a Section, process its links recursively
                    extract_links(item[1])

        extract_links(toc)
        return chapters   
    
    def is_potential_chapter(self, title: str) -> bool:
        """
        Determine if a given title of an ItemEpub is likely to be a chapter based on patterns and keywords.
        
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
    


if __name__ == "__main__":

    epub_path = "/Users/andreafavia/development/bookai/files/The Responsible Company.epub"
    scraper = EbookScraper(epub_path)
    chapters = scraper.chapters_idx
    print(chapters)
