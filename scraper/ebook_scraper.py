import ebooklib
from ebooklib import epub
import re
from typing import List, Dict, Union
from transformers import pipeline
import warnings
from models.base_summarizer import SummarizerBaseModel
from scraper.utils import generate_html_page, NON_CHAPTER_WORDS
from summarizers.base_hf import HFBaseSummarizer
from models.base_summarizer import SummarizationException
from summarizers.gemini import Gemini
from bionicreader.bionicreader import BionicReader
from bs4 import BeautifulSoup
import tqdm
import time
import logging

warnings.filterwarnings("ignore")

PATTERN_HREF = r"^[^#]+\.html"
MIN_LENGTH = 700

# TODO: Add vector database to store chapters
# TODO: create 3 points for each chapter
# TODO: add tests


class EbookScraper:
    def __init__(
        self,
        epub_path: str,
        summarizer: SummarizerBaseModel,
        zero_shot_classifier_model_hf: str = "facebook/bart-large-mnli",
        bionic_reader: BionicReader = None,
    ):
        self.epub = self._load_epub(epub_path)
        self.epub_title = self.epub.title
        self.classifier = pipeline("zero-shot-classification", model=zero_shot_classifier_model_hf)
        self.candidate_labels = ["about the author", "acknowledgements", "about the book", "table of content"]
        self.chapters_idx = self._get_chapters_with_uids(self.epub.toc)
        self.items = self.epub.get_items()
        self.summarizer = summarizer

        self.summary = None
        self.summary_bionic = None
        self.book_parsed = None
        self.bionic_reader = bionic_reader

    @staticmethod
    def _load_epub(epub_path):
        try:
            return epub.read_epub(epub_path)
        except Exception as e:
            raise Exception(f"Error loading EPUB file: {str(e)}")

    def _extract_title(self, text):
        """Extract the title from the title text, there might be some IDs after the html"""
        match = re.match(PATTERN_HREF, text)
        if match:
            return match.group()
        return text

    def summarize_chapters(self):
        """Summarize all chapters of the EPUB book using the specified summarizer."""
        summary = {}
        summary_bionic = {}
        if not self.book_parsed:
            self._scrape_chapters()
        for chapter_title, chapter_text in tqdm.tqdm(self.book_parsed.items()):
            try:
                result_summary = self.summarizer.summarize(chapter_text)
                summary[chapter_title] = result_summary
                if self.bionic_reader:  # it returns a html output, but I want to keep the text as well
                    summary_bionic[chapter_title] = self.bionic_reader.convert(result_summary)
                time.sleep(0.04)  # Avoid rate limiting of gemini API
            except SummarizationException as e:
                logging.warning(f"Error summarizing chapter '{chapter_title}': {str(e)}")
                summary[chapter_title] = "Error summarizing chapter"
                summary_bionic[chapter_title] = "Error summarizing chapter"

        self.summary = summary
        self.summary_bionic = summary_bionic
        return self.summary_bionic

    def _scrape_chapters(self):
        """Scrape the text content of the chapters from the EPUB book."""
        book_parsed = {}
        for item in self.items:
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                if (file_name := item.get_name()) in self.chapters_idx:
                    soup = BeautifulSoup(item.get_body_content(), "html.parser")
                    text_content = soup.get_text()
                    if len(text_content) > MIN_LENGTH:
                        book_parsed[self.chapters_idx.get(file_name)] = text_content
                    else:
                        logging.warning(f"Chapter '{self.chapters_idx.get(file_name)}' is too short and will be skipped.")

        self.book_parsed = book_parsed

    def _get_chapters_with_uids(self, toc: List[Union[epub.Link, tuple]]) -> Dict[str, str]:
        """Extract the chapters from the table of contents of the EPUB book."""

        chapters = {}

        def extract_links(items: List[Union[epub.Link, tuple]]):
            for item in items:
                if isinstance(item, epub.Link):
                    if self.is_potential_chapter(item.title):
                        chapters[self._extract_title(item.href)] = item.title
                elif isinstance(item, tuple) and isinstance(item[0], epub.Section):
                    # If the item is a Section, process its links recursively
                    extract_links(item[1])

        extract_links(toc)
        return chapters

    def is_potential_chapter(self, title: str) -> bool:
        """Determine if a given title of an ItemEpub is likely to be a chapter based on patterns and keywords."""
        # Define keywords for non-chapter sections
        non_chapter_keywords = NON_CHAPTER_WORDS

        # Check for keywords indicating non-chapter sections
        if any(keyword.lower() in title.lower() for keyword in non_chapter_keywords):
            return False

        # Check for chapter-like patterns (e.g., numbers or "Chapter")
        if re.search(r"^(Chapter|[0-9]+(\.|:))", title, re.IGNORECASE):
            return True

        # If no clear indicators, consider it a chapter by default
        return True


if __name__ == "__main__":
    import json

    title = "Big Feelings"
    epub_path = f"/Users/andreafavia/development/bookai/files/{title}.epub"

    try:
        book_parsed = json.load(open(f"/Users/andreafavia/development/bookai/{title}.json"))

    except Exception as e:
        print(f"Error loading book: {str(e)}")
        scraper = EbookScraper(epub_path, Gemini(), bionic_reader=BionicReader())
        book_parsed = scraper.summarize_chapters()
        json.dump(book_parsed, open(f"/Users/andreafavia/development/bookai/{title}.json", "w"))

    html = generate_html_page(book_parsed, title)
    with open(f"{title}_summary.html", "w") as file:
        file.write(html)
