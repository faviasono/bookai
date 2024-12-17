import pypub

from dotenv import load_dotenv
import os

from pypub.builder import generate_font, get_textsize
from PIL import Image, ImageDraw

load_dotenv("../.env")

BASE_COVER_IMAGE_PATH = "bookai/converter/assets/cover_epub_generator.png"
if not os.path.exists(BASE_COVER_IMAGE_PATH):
    BASE_COVER_IMAGE_PATH = None  # use the default cover image

CREATOR = "Sumledge © 2024"


class EpubGenerator:
    def __init__(self, chapters: dict, title: str = ""):
        self.chapters = chapters
        self.title = title + " Summary"
        self.path_cover = self._generate_cover(title, CREATOR, BASE_COVER_IMAGE_PATH) if BASE_COVER_IMAGE_PATH else None
        self.book = pypub.Epub(self.title, creator="Sumledge © 2024", cover=self.path_cover)

    def generate_epub(self, pardir: str = "/tmp"):
        for chapter_title, chapter_text in self.chapters.items():
            chapter = pypub.create_chapter_from_text(chapter_text, title=chapter_title)
            self.book.add_chapter(chapter)
        return self.book.create(f"{pardir}/{self.title}_summary.epub")

    # override the default cover generation method
    def _generate_cover(self, title, author, image_path, output_path="/tmp/cover.png"):
        """generate cover image using PIL text overlay"""
        title = title.title()
        author = author.title()
        fill = (255, 255, 255, 255)
        with Image.open(image_path).convert("RGBA") as image:
            width, height = image.size
            draw = ImageDraw.Draw(image)
            # draw title on the top of the cover
            font = generate_font(title, 0.9, 70, width)
            w, _ = get_textsize(draw, title, font=font)
            draw.text(((width - w) / 2, 10), title, font=font, fill=fill)
            # draw author on the bottom of the cover
            font = generate_font(title, 0.5, 40, width)
            w, h = get_textsize(draw, author, font=font)
            draw.text(((width - w) / 2, height - int(h * 1.5)), author, font=font, fill=fill)
            # write cover directly into epub directory
            image.save(output_path)
            return output_path


if __name__ == "__main__":
    # try the new cover
    import os

    book = {"Chapter 1": "This is the first chapter of the book", "Chapter 2": "This is the second chapter of the book"}
    epub = EpubGenerator(book, "My Book")
    epub.generate_epub(pardir=os.getcwd())
