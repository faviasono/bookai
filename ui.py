import streamlit as st
import os
from bookai.scraper.ebook_scraper import EbookScraper

st.set_page_config(layout="wide", page_title="SumLedge 📚", page_icon="📚")

os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
os.environ["BIONIC_API_KEY"] = st.secrets["BIONIC_API_KEY"]
os.environ["TOKENIZERS_PARALLELISM"] = "false"
if "BIONIC_API_KEY" in st.secrets:
    os.environ["BIONIC_API_KEY"] = st.secrets["BIONIC_API_KEY"]
else:
    st.error("BIONIC_API_KEY is not set in the secrets")

os.environ["TOKENIZERS_PARALLELISM"] = "false"

from bookai.scraper.ebook_scraper import EbookScraper  # Make sure to import your EbookScraper
from bookai.summarizers.gemini import Gemini  # Make sure to import your summarizer
from bookai.bionicreader.bionicreader import BionicReader
from bookai.scraper.utils import generate_html_page
from bookai.rag.question_answering_book import QuestionAnsweringBook
from collections import defaultdict
from bookai.tts.tts_google import GoogleTTS
from google.oauth2 import service_account
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from bookai.converter.epubgenerator import EpubGenerator
from streamlit_extras.buy_me_a_coffee import button

qa_embedding_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")


session_keys = {
    "cache_summaries": defaultdict(str),
    "chapter_1": None,
    "show_results": False,
    "book_parsed": None,
    "plain_summary": None,
    "rag": None,
    "podcast": defaultdict(bytes),
    "disabled": False,
    "uploaded_file": False,
}

for key, value in session_keys.items():
    if key not in st.session_state:
        st.session_state[key] = value
if "gcp_service_account" in st.secrets:
    credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])


geminisummarizer = Gemini()
bionicreader = BionicReader()
tts = GoogleTTS(credentials=credentials if "gcp_service_account" in st.secrets else None)


def download_summary(summary, filename):
    """
    Downloads the provided summary as an HTML file.
    Parameters:
    summary (str): The summary content to be downloaded.
    filename (str): The name of the file to save the summary as.
    """
    st.session_state.show_results = True

    place_holder = st.sidebar.container()
    with place_holder:
        c1, c2 = st.sidebar.columns([1, 1])
        with c1:
            st.sidebar.download_button(
                label="Download Summary",
                data=summary,
                file_name=f"{filename}_analysis.html",
                mime="text/html",
            )

        with c2:
            path = EpubGenerator(st.session_state.plain_summary, filename).generate_epub()
            st.sidebar.download_button(
                label="Download Epub",
                data=open(path, "rb").read(),
                file_name=f"{filename}_summary.epub",
                mime="application/epub",
            )

    return place_holder


def clean_state():
    for key in st.session_state.keys():
        del st.session_state[key]


def disable_form():
    st.session_state.disabled = True


@st.dialog("Welcome to SumLedge 📚")
def welcome():
    st.write(
        "This app allows you to analyze the content of an ebook. It will summarize the chapters and provide a reflection point based on the summaries. You can also ask questions about the book using the RAG model or listen to a podcasted version of the summaries."
    )
    st.write("Open the sidebar to upload a .EPUB and to get started.")
    st.write("To try another book, refresh the page.")
    st.write(
        "You don't have an ebook? You can find them on, for example, [Project Gutenberg](https://www.gutenberg.org/) or Z-library..."
    )
    st.caption("Made with ❤️ by Andrea Favia")


def generate_title_and_caption():
    if not st.session_state.disabled:
        welcome()
    st.html(
        r"""<style>

        .st-emotion-cache-19ee8pt {
                height: 3rem;
                width : 3rem;
                # background-color: RED;
                animation: hithere 2s ease infinite;
            }
        @keyframes hithere {
            30% { transform: scale(1.2); }
            40%, 60% { transform: rotate(-20deg) scale(1.2); }
            50% { transform: rotate(20deg) scale(1.2); }
            70% { transform: rotate(0deg) scale(1.2); }
            100% { transform: scale(1); }
        }
        </style>
        """,
    )
    st.sidebar.title("SumLedge 📚")
    st.title("SumLedge 📚")
    st.caption("Analyze the content of an ebook and generate summaries, chat with the book, and listen to an automated podcast.")
    st.caption("Open the sidebar to get started.")

    st.divider()
    button(username="faviasono", text="Buy me a coffe", floating=False)
    st.markdown(
        f"""
            <style>
                iframe[width="{220}"] {{
                    position: fixed;
                    z-index: 100;
                    bottom: 60px;
                    right: 60px;
                }}
            </style>
            """,
        unsafe_allow_html=True,
    )


def generate_about_and_how_sections():
    with st.sidebar.expander("About"):
        st.write(
            "This app allows you to analyze the content of an ebook. It will summarize the chapters and provide a reflection point based on the summaries. You can also ask questions about the book using the RAG model or listen to a podcasted version of the summaries."
        )

    with st.sidebar.expander("Instructions"):
        st.write(
            "1. Upload your .epub file to analyze."
            "\n2. Click on 'Show Analysis Results' to see the chapter summaries."
            "\n3. Click on 'Initialize RAG' to start the RAG model."
            "\n4. Ask a question about the book in the chat box."
            "\n5. Click on 'Generate Podcast' to create a podcast of the summaries."
        )

    st.sidebar.divider()


def main():
    generate_title_and_caption()

    generate_about_and_how_sections()

    # Summarize EPUB

    st.sidebar.header(
        "Summarize EPUB 📖",
        help="Identify the chapters and generate summaries for the book. You can also use the bionic reader to facilitate the reading process.",
    )

    with st.form(key="upload_epub"):
        with st.sidebar:
            uploaded_file = st.file_uploader("UPLOAD YOUR .EPUB TO ANALYZE", type="epub", label_visibility="collapsed")
            checkbox = st.checkbox(
                "Use bionic reading",
                value=False,
                help="Bionic reading is a method facilitating the reading process by guiding the eyes through the text with artificial fixation points.",
            )
            _ = st.form_submit_button("Summarize book 🚀", on_click=disable_form, disabled=st.session_state.disabled)

    if uploaded_file is not None:
        with open("temp.epub", "wb") as f:
            f.write(uploaded_file.getbuffer())
        try:
            # Process the file using EbookScraper

            scraper = EbookScraper("temp.epub", geminisummarizer, bionic_reader=bionicreader if checkbox else None)

            if "chapter_summaries" not in st.session_state:
                if scraper.epub_title in st.session_state.cache_summaries:
                    st.session_state.chapter_summaries = st.session_state.cache_summaries[scraper.epub_title]
                else:
                    with st.spinner("Analyzing chapters.. It could take a few minutes."):
                        st.session_state.cache_summaries[scraper.epub_title] = generate_html_page(
                            scraper.summarize_chapters(), scraper.epub_title
                        )
                        st.session_state.chapter_summaries = st.session_state.cache_summaries[scraper.epub_title]
                        st.session_state.book_parsed = scraper.book_parsed
                        st.session_state.plain_summary = scraper.summary

            download_summary(st.session_state.chapter_summaries, scraper.epub_title)

            if st.session_state.show_results:
                st.html(st.session_state.chapter_summaries)
        except Exception as e:
            st.error(f"Could not parse .Epub with Error: {e}")
            st.error("Please refresh the page and try again with a different file.")

    # RAG
    if st.session_state.plain_summary:
        st.sidebar.header(
            "Ask your Book 🕵🏼‍♀️",
            help="Do you have specific questions about the book, or would you like me to elaborate on points from the summaries?",
        )
        if (
            st.sidebar.button("Start asking your book ", disabled=st.session_state.book_parsed is None)
            and st.session_state.book_parsed
            and not st.session_state.rag
        ):
            with st.sidebar.container():
                with st.spinner("Initializing RAG system... \n It might take a few minutes."):
                    # Example query
                    qa_book = QuestionAnsweringBook(
                        st.session_state.book_parsed,
                        qa_embedding_model,
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

    # Podcast

    if st.session_state.plain_summary:
        # Podcast
        st.sidebar.divider()
        st.sidebar.header(
            "Podcast 🎙️", help="Convert the summary into an audio format that you can download and listen to anytime, anywhere."
        )

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
