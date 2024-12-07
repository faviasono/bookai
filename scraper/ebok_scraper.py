import ebooklib
from ebooklib import epub
import re
from typing import List, Dict, Union
from transformers import pipeline
import warnings
from models.base_summarizer import SummarizerBaseModel
from summarizers.base_hf import HFBaseSummarizer
from summarizers.gemini import Gemini
from bs4 import BeautifulSoup
import tqdm


# TODO: Add vector database to store chapters
# TODO: create 3 points for each chapter

warnings.filterwarnings("ignore")


class EbookScraper:
    def __init__(
        self, epub_path: str, summarizer: SummarizerBaseModel, zero_shot_classifier_model_hf: str = "facebook/bart-large-mnli"
    ):
        self.epub = self._load_epub(epub_path)
        self.epub_title = self.epub.title
        self.classifier = pipeline("zero-shot-classification", model=zero_shot_classifier_model_hf)
        self.candidate_labels = ["about the author", "acknowledgements", "about the book", "table of content"]
        self.chapters_idx = self._get_chapters_with_uids(self.epub.toc)
        self.items = self.epub.get_items()
        self.summarizer = summarizer

        self.summary = None
        self.book_parsed = None

    @staticmethod
    def _load_epub(epub_path):
        try:
            return epub.read_epub(epub_path)
        except Exception as e:
            raise Exception(f"Error loading EPUB file: {str(e)}")

    def summarize_chapters(self):
        """Summarize all chapters of the EPUB book using the specified summarizer."""
        summary = {}
        if not self.book_parsed:
            self._scrape_chapters()
        for chapter_title, chapter_text in tqdm.tqdm(self.book_parsed.items()):
            summary[chapter_title] = self.summarizer.summarize(chapter_text)

        self.summary = summary
        return self.summary

    def _scrape_chapters(self):
        book_parsed = {}
        for item in self.items:
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                if (file_name := item.get_name()) in self.chapters_idx:
                    soup = BeautifulSoup(item.get_body_content(), "html.parser")
                    text_content = soup.get_text()
                    if len(text_content) > 1000:
                        book_parsed[self.chapters_idx.get(file_name)] = text_content

        self.book_parsed = book_parsed

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
                        chapters[item.href] = item.title
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
            "Acknowledgments",
            "Acknowledgements",
            "Index",
            "Notes",
            "About the",
            "Dedication",
            "Title Page",
            "Copyright",
            "Contents",
            "Cover",
            "Index",
            "Contents",
            "Notes",
            "List of",
            "Annex",
            "Also by",
            "Foreword",
            "Preface",
            "Appendix",
            "Glossary",
            "Bibliography",
            "Introduction",
            "Prologue",
            "Epilogue",
            "Afterword",
            "Appendix",
            "Endnotes",
            "Footnotes",
            "References",
            "Further Reading",
            "Permissions",
            "Colophon",
            "Errata",
            "Erratum",
            "Errata Corrige",
            "Errata Sheet",
            "Erratum Sheet",
            "Errata Slip",
            "Erratum Slip",
            "Copyright",
            "About the Author",
            "About the Translator",
            "About the Editor",
            "Note to the Reader",
            "Credits",
            "List of Illustrations",
            "List of Tables",
            "List of Figures",
            "List of Maps",
            "Epigraph",
            "Table of Cases",
            "Table of Statutes",
            "Table of Authorities",
            "Table of Abbreviations",
            "Note",
            "Translator's Note",
            "Editor's Note",
            "Editorial Note",
            "Publisher's Note",
            "Buy the book",
            "Recommended Reading",
            "About the Series",
            "About the Publisher",
            "About the Cover",
        ]

        # Check for keywords indicating non-chapter sections
        if any(keyword.lower() in title.lower() for keyword in non_chapter_keywords):
            return False

        # Check for chapter-like patterns (e.g., numbers or "Chapter")
        if re.search(r"^(Chapter|[0-9]+(\.|:))", title, re.IGNORECASE):
            return True

        # If no clear indicators, consider it a chapter by default
        return True


def generate_html_page(chapters, title):
    """
    Generates an HTML page with a stylish layout for the given chapters.

    Args:
      chapters: A dictionary where keys are chapter titles and values are chapter content.

    Returns:
      A string containing the HTML code for the page.
    """

    html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{title}</title>
                <style>
                    /* Basic Styling */
                    body {{
                        font-family: 'Open Sans', sans-serif;
                        background-color: #f0f0f0;
                        margin: 0;
                        padding: 0;
                        display: flex;
                        flex-direction: column;
                        min-height: 100vh;
                    }}

                    header {{
                        background-color: #333;
                        color: #fff;
                        text-align: center;
                        padding: 2rem 0;
                    }}

                    h1 {{
                        font-size: 2.5rem;
                        margin: 0;
                    }}

                    nav {{
                        background-color: #eee;
                        padding: 1rem 0;
                    }}

                    nav ul {{
                        list-style: none;
                        padding: 0;
                        margin: 0;
                        display: flex;
                        justify-content: center;
                    }}

                    nav li {{
                        margin: 0 1rem;
                    }}

                    nav a {{
                        color: #333;
                        text-decoration: none;
                        font-weight: bold;
                        transition: color 0.3s ease;
                    }}

                    nav a:hover {{
                        color: #007bff;
                    }}

                    main {{
                        flex-grow: 1;
                        padding: 2rem;
                        background-color: #fff;
                        border-radius: 5px;
                        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                        margin: 1rem;
                    }}

                    h2 {{
                        color: #333;
                        margin-bottom: 1rem;
                    }}

                    footer {{
                        background-color: #333;
                        color: #fff;
                        text-align: center;
                        padding: 1rem 0;
                        position: fixed;
                        bottom: 0;
                        width: 100%;
                    }}
                </style>
            </head>
            <body>

                <header>
                    <h1>{title}</h1>
                </header>

                <nav>
                    <ul>
            """

    for title in chapters:
        html += f"              <li><a href='#{title.replace(' ', '-')}'>{title}</a></li>\n"

    html += """
          </ul>
      </nav>

      <main>
  """

    for title, content in chapters.items():
        html += f"""
          <section id="{title.replace(' ', '-')}">
              <h2>{title}</h2>
              <p>{content}</p>
          </section>
  """

    html += """
      </main>

      <footer>
          &copy; 2024 Book AI: All rights reserved
      </footer>

  </body>
  </html>
  """

    return html


if __name__ == "__main__":
    import json

    title = "The Responsible Company"
    epub_path = f"/Users/andreafavia/development/bookai/files/{title}.epub"

    try:
        book_parsed = json.load(open(f"/Users/andreafavia/development/bookai/{title}.json"))

    except Exception as e:
        print(f"Error loading book: {str(e)}")
        scraper = EbookScraper(epub_path, Gemini())
        book_parsed = scraper.summarize_chapters()
        json.dump(book_parsed, open(f"/Users/andreafavia/development/bookai/{title}.json", "w"))

    html = generate_html_page(book_parsed, title)
    with open(f"{title}_summary.html", "w") as file:
        file.write(html)
