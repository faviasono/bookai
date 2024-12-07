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


geminisummarizer = Gemini()
bionicreader = BionicReader()


def main():
    st.title("Ebook Analyzer")
    st.write("Upload your .epub file to analyze.")

    uploaded_file = st.file_uploader("Choose a .epub file", type="epub")

    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with open("temp.epub", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Process the file using EbookScraper
        scraper = EbookScraper("temp.epub", geminisummarizer, bionic_reader=bionicreader)

        if "chapter_summaries" not in st.session_state:
            with st.spinner("Analyzing chapters..."):
                st.session_state.chapter_summaries = generate_html_page(scraper.summarize_chapters(), scraper.epub_title)

        # Display the results on another page
        if st.button("Upload complete! View results"):
            st.write("Analysis Results")
            st.html(st.session_state.chapter_summaries)


if __name__ == "__main__":
    main()
