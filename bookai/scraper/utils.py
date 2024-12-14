NON_CHAPTER_WORDS = [
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
                </style>
            </head>
            <body>

                <header>
                    <h1>{title}</h1>
                </header>

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

      </body>
      </html>
      """

    return html
