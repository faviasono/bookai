import streamlit as st

st.set_page_config(layout="wide")
import os
import sys


os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
os.environ["BIONIC_API_KEY"] = st.secrets["BIONIC_API_KEY"]


# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from bookai.scraper.ebook_scraper import EbookScraper  # Make sure to import your EbookScraper
from bookai.summarizers.gemini import Gemini  # Make sure to import your summarizer
from bookai.bionicreader.bionicreader import BionicReader
from bookai.scraper.utils import generate_html_page
from bookai.rag.question_answering_book import QuestionAnsweringBook
from collections import defaultdict
from bookai.tts.tts_google import GoogleTTS
from elevenlabs import save

if "cache_summaries" not in st.session_state:
    st.session_state.cache_summaries = defaultdict(str)

if "chapter_1" not in st.session_state:
    st.session_state.chapter_1 = None

if "first_chapter_tts" not in st.session_state:
    st.session_state.first_chapter_tts = None

if "show_results" not in st.session_state:
    st.session_state.show_results = False

if "book_parsed" not in st.session_state:
    st.session_state.book_parsed = None

if "rag" not in st.session_state:
    st.session_state.rag = None

geminisummarizer = Gemini()
bionicreader = BionicReader()


def download_summary(summary, filename):
    st.session_state.show_results = True
    st.sidebar.download_button(
        label="Download Summary",
        data=summary,
        file_name=f"{filename}_analysis.html",
        mime="text/html",
    )


@st.fragment
def generate_audio_chapter_widget(text):
    if st.button("Listen to the first chapter"):
        tts = GoogleTTS()
        if st.session_state.first_chapter_tts is None:
            with st.spinner("Generating audio..."):
                audio = tts.synthesize(text)
                if audio:
                    save(audio, "temp_first_chapter.mp3")
                    st.session_state.first_chapter_tts = "temp_first_chapter.mp3"

        st.audio(st.session_state.first_chapter_tts, format="audio/wav", start_time=0)


def main():
    st.sidebar.title("Ebook Analyzer 📚")
    st.title("Ebook Analyzer 📚")
    st.divider()

    with st.sidebar.expander("About"):
        st.write(
            "This app allows you to analyze the content of an ebook. It will summarize the chapters and provide a reflection point based on the summaries. You can also ask questions about the book using the RAG model."
        )

    with st.sidebar.expander("Instructions"):
        st.write(
            "1. Upload your .epub file to analyze."
            "\n2. Click on 'Show Analysis Results' to see the chapter summaries."
            "\n3. Click on 'Initialize RAG' to start the RAG model."
            "\n4. Ask a question about the book in the chat box."
        )

    st.sidebar.divider()

    # st.sidebar.write("Upload your .epub file to analyze.")
    uploaded_file = st.sidebar.file_uploader("UPLOAD YOUR .EPUB TO ANALYZE", type="epub", label_visibility="collapsed")

    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with open("temp.epub", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Process the file using EbookScraper
        scraper = EbookScraper("temp.epub", geminisummarizer, bionic_reader=bionicreader)

        if "chapter_summaries" not in st.session_state:
            if scraper.epub_title in st.session_state.cache_summaries:
                st.session_state.chapter_summaries = st.session_state.cache_summaries[scraper.epub_title]
            else:
                with st.spinner("Analyzing chapters..."):
                    st.session_state.cache_summaries[scraper.epub_title] = generate_html_page(
                        scraper.summarize_chapters(), scraper.epub_title
                    )
                    st.session_state.chapter_summaries = st.session_state.cache_summaries[scraper.epub_title]
                    st.session_state.book_parsed = scraper.book_parsed

        download_summary(st.session_state.chapter_summaries, scraper.epub_title)

        if st.session_state.show_results:
            st.html(st.session_state.chapter_summaries)

        st.sidebar.divider()

        container_sidebar = st.sidebar.container()
        if st.sidebar.button("Initialize RAG") and st.session_state.book_parsed and not st.session_state.rag:
            with container_sidebar:
                with st.spinner("Initializing RAG..."):
                    # Example query
                    qa_book = QuestionAnsweringBook(
                        st.session_state.book_parsed,
                        "BAAI/bge-small-en-v1.5",
                        "models/gemini-1.5-flash",
                        os.environ.get("GEMINI_API_KEY"),
                    )
                    st.session_state.rag = qa_book

        if st.session_state.rag:
            text = st.sidebar.chat_input("Ask a question about the book")
            if text:
                response = st.session_state.rag.query(text)
                with st.sidebar.container():
                    st.sidebar.write_stream(response.response_gen)


if __name__ == "__main__":
    main()
