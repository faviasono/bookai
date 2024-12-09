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
from collections import defaultdict
from bookai.tts.tts_google import GoogleTTS
from elevenlabs import save

if "cache_summaries" not in st.session_state:
    st.session_state.cache_summaries = defaultdict(str)

if "chapter_1" not in st.session_state:
    st.session_state.chapter_1 = None

if "first_chapter_tts" not in st.session_state:
    st.session_state.first_chapter_tts = None

geminisummarizer = Gemini()
bionicreader = BionicReader()


@st.fragment
def dowload_summary(summary, filename):
    st.download_button(
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
    st.title("Ebook Analyzer")
    st.write("Upload your .epub file to analyze.")

    uploaded_file = st.file_uploader("Choose a .epub file", type="epub")

    if uploaded_file:
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
                    scraper.summarize_chapters()

                    st.session_state.chapter_1 = scraper.get_chapter_summary(0)
                    st.session_state.cache_summaries[scraper.epub_title] = generate_html_page(
                        scraper.summary_bionic, scraper.epub_title
                    )
                    st.session_state.chapter_summaries = st.session_state.cache_summaries[scraper.epub_title]

        col1, _, col2 = st.columns((2, 8, 2))
        # Display the results on another page
        show_results = False
        with col1:
            if st.button("Show Analysis Results"):
                show_results = True
        with col2:
            dowload_summary(st.session_state.chapter_summaries, scraper.epub_title)
        if show_results:
            st.html(st.session_state.chapter_summaries)

            # Display the first chapter audio
            if st.session_state.chapter_1:
                generate_audio_chapter_widget(st.session_state.chapter_1)

        # clean state
        os.remove("temp.epub")


if __name__ == "__main__":
    main()
