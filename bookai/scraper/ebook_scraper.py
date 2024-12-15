import concurrent.futures
import ebooklib
from ebooklib import epub
import re
from typing import List, Dict, Union

# from transformers import pipeline
import warnings

from bookai.models.base_summarizer import SummarizerBaseModel
from bookai.scraper.utils import generate_html_page, NON_CHAPTER_WORDS
from bookai.models.base_summarizer import SummarizationException
from bookai.summarizers.gemini import Gemini
from bookai.bionicreader.bionicreader import BionicReader
from bs4 import BeautifulSoup
import tqdm
import time
import logging
import concurrent

warnings.filterwarnings("ignore")

PATTERN_HREF = r"^[^#]+\.html"
MIN_LENGTH = 105

# TODO: create 3 points for each chapter
# TODO: add tests


class EbookScraper:
    def __init__(
        self,
        epub_path: str,
        summarizer: SummarizerBaseModel,
        bionic_reader: BionicReader = None,
    ):
        self.epub = self._load_epub(epub_path)
        self.epub_title = self.epub.title
        self.chapters_idx = self._get_chapters_with_uids(self.epub.toc)
        self.items = self.epub.get_items()
        self.summarizer = summarizer

        self.summary = None
        self.summary_bionic = None
        self.book_parsed = None
        self.bionic_reader = bionic_reader

    def _is_allowed_language(self, epub):
        """Check if the EPUB is in allowed language (English for now)."""
        return epub.language in ["en"]

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

        # Initialize summarizer and bionic_reader because MP does not allow to pass class methods
        summarizer = self.summarizer()
        bionic_reader = self.bionic_reader() if self.bionic_reader else None

        if not self.book_parsed:
            self._scrape_chapters()
        start_time = time.time()
        for chapter_title, chapter_text in tqdm.tqdm(self.book_parsed.items()):
            try:
                result_summary = summarizer.summarize(chapter_text)
                summary[chapter_title] = result_summary
                if self.bionic_reader:  # it returns a html output, but I want to keep the text as well
                    summary_bionic[chapter_title] = bionic_reader.convert(result_summary)
                time.sleep(0.02)  # Avoid rate limiting of gemini API
            except SummarizationException as e:
                logging.warning(f"Error summarizing chapter '{chapter_title}': {str(e)}")
                summary[chapter_title] = "Error summarizing chapter"
                summary_bionic[chapter_title] = "Error summarizing chapter"

        self.summary = summary
        self.summary_bionic = summary_bionic
        print(f"Time elapsed: {time.time() - start_time}")
        return self.summary_bionic if self.bionic_reader else self.summary

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
                        logging.warning(
                            f"Chapter '{self.chapters_idx.get(file_name)}'  with len {len(text_content)} is too short and will be skipped."
                        )

        self.book_parsed = book_parsed

    def get_chapter_summary(self, idx: int):
        """Get the text content of a specific chapter by its index."""
        if not self.summary:
            raise Exception("Chapters have not been summarized yet.")
        keys = list(self.chapters_idx.values())
        if idx >= len(keys):
            idx = len(keys) - 1
        return self.summary.get(keys[idx])

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

    @staticmethod
    def _summarize_chapter_worker(args):
        """Standalone function to summarize a chapter."""
        chapter_title, chapter_text, summarizer, bionic_reading = args

        # Initialize summarizer and bionic_reader inside the worker
        summarizer = summarizer()
        bionic_reader = bionic_reading() if bionic_reading else None

        try:
            result_summary = summarizer.summarize(chapter_text)
            if bionic_reader:
                result_summary_bionic = bionic_reader.convert(result_summary)
                return chapter_title, result_summary, result_summary_bionic
            else:
                return chapter_title, result_summary, None
        except SummarizationException as e:
            logging.warning(f"Error summarizing chapter '{chapter_title}': {str(e)}")
            return chapter_title, "Error summarizing chapter", "Error summarizing chapter"

    def summarize_chapters_mp(self):
        """Summarize all chapters of the EPUB book using the specified summarizer using multiprocessing."""
        if not self.book_parsed:
            self._scrape_chapters()

        self.summary = {}
        self.summary_bionic = {}
        start_time = time.time()
        chapters = list(self.book_parsed.items())
        # Prepare arguments for the worker function
        worker_args = [
            (chapter_title, chapter_text, self.summarizer, self.bionic_reader) for chapter_title, chapter_text in chapters
        ]

        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = list(tqdm.tqdm(executor.map(self._summarize_chapter_worker, worker_args), total=len(self.book_parsed)))

        # Process results
        for chapter_title, result_summary, result_summary_bionic in results:
            self.summary[chapter_title] = result_summary
            if self.bionic_reader:
                self.summary_bionic[chapter_title] = result_summary_bionic

        print(f"Time elapsed: {time.time() - start_time}")

        return self.summary_bionic if self.bionic_reader else self.summary


if __name__ == "__main__":
    import json

    title = "Ultra Processed People"
    epub_path = f"/Users/andreafavia/development/bookai/files/{title}.epub"

    try:
        book_parsed = json.load(open(f"/Users/andreafavia/development/bookai/{title}.json"))

    except Exception as e:
        print(f"Error loading book: {str(e)}")
        scraper = EbookScraper(epub_path, Gemini, bionic_reader=BionicReader)
        book_parsed = scraper.summarize_chapters_mp()
        json.dump(book_parsed, open(f"/Users/andreafavia/development/bookai/{title}.json", "w"))

    html = generate_html_page(book_parsed, title)
    with open(f"{title}_summary.html", "w") as file:
        file.write(html)
