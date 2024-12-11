import streamlit as st

st.set_page_config(layout="wide")
import os
import sys


os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
os.environ["BIONIC_API_KEY"] = st.secrets["BIONIC_API_KEY"]
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from bookai.scraper.ebook_scraper import EbookScraper  # Make sure to import your EbookScraper
from bookai.summarizers.gemini import Gemini  # Make sure to import your summarizer
from bookai.bionicreader.bionicreader import BionicReader
from bookai.scraper.utils import generate_html_page
from bookai.rag.question_answering_book import QuestionAnsweringBook
from collections import defaultdict
from bookai.tts.tts_google import GoogleTTS
from elevenlabs import save
from google.oauth2 import service_account


if "cache_summaries" not in st.session_state:
    st.session_state.cache_summaries = defaultdict(str)

if "chapter_1" not in st.session_state:
    st.session_state.chapter_1 = None

if "show_results" not in st.session_state:
    st.session_state.show_results = False

if "book_parsed" not in st.session_state:
    st.session_state.book_parsed = None

if "plain_summary" not in st.session_state:
    st.session_state.plain_summary = None

if "rag" not in st.session_state:
    st.session_state.rag = None

if "podcast" not in st.session_state:
    st.session_state.podcast = defaultdict(bytes)
credentials = None
if "gcp_service_account" in st.secrets:
    credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])


geminisummarizer = Gemini()
bionicreader = BionicReader()
tts = GoogleTTS(credentials=credentials)


def download_summary(summary, filename):
    st.session_state.show_results = True
    st.sidebar.download_button(
        label="Download Summary",
        data=summary,
        file_name=f"{filename}_analysis.html",
        mime="text/html",
    )


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

    # Analyze test
    st.sidebar.divider()
    st.sidebar.header("Summarize EPUB 📖")

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
                    st.session_state.plain_summary = scraper.summary

        download_summary(st.session_state.chapter_summaries, scraper.epub_title)

        if st.session_state.show_results:
            st.html(st.session_state.chapter_summaries)

        # Analyze test
        st.sidebar.divider()
        st.sidebar.header("Ask your Book 🕵🏼‍♀️")

        if st.sidebar.button("Initialize RAG") and st.session_state.book_parsed and not st.session_state.rag:
            with st.sidebar.container():
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
                with st.sidebar.expander("", expanded=True):
                    st.write_stream(response.response_gen)

        if st.session_state.plain_summary:
            # Podcast
            st.sidebar.divider()
            st.sidebar.header("Podcast 🎙️ (WIP ⚠️)")

            chapters = list(st.session_state.plain_summary.items())

            if st.sidebar.button("Generate Podcast") and not st.session_state.podcast:
                with st.sidebar.container():
                    with st.spinner("Generating podcast..."):
                        for title, content in chapters:
                            audio = tts.synthesize(content)
                            if audio:
                                st.session_state.podcast[title] = audio

            if st.session_state.podcast:
                combined_audio = b"".join(st.session_state.podcast.values())
                for title, audio in st.session_state.podcast.items():
                    st.sidebar.subheader(title)
                    st.sidebar.audio(audio, format="audio/wav", start_time=0)

                st.sidebar.download_button(
                    label="Download Podcast",
                    data=combined_audio,
                    file_name=f"podcast_{scraper.epub_title}.mp3",
                    mime="application/mp3",
                )


if __name__ == "__main__":
    main()