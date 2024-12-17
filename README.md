
# Sumledge - Book AI
Sumledge is a simple application that allows scraping chapters content from .Epub, summarize the content, initialize a RAG to ask specific question about the book and even generate a podcast with Text-To-Speech (TTS) technologies.

## Streamlit app
You can try the application directly from this [Streamlit app](https://sumledge.streamlit.app)

## Description
The project uses Google APIs both for Vertex AI Gemini as well as for TTS models. They are virtually free and below more details about the current dependencies:

- Summarizer model: Gemini 1.5 Flash
- Embedding model for RAG: Hugging face BAAI/bge-small-en-v1.5
- Response generator for RAG: Gemini 1.5 Flash
- Text-To-Speech model: Google en-US-Neural2-D 

It's possible to quickly change the models for the embeddings and for gemini, as well as the model for TTS to get a more natural voice (more expensive).
At the same time, a TTS interface with ElevenLabs is implemented.



=======
# Book AI 

stremlit app: https://sumledge.streamlit.app

Example of Epub: https://drive.google.com/file/d/151oujA8zI3PVzSlNycD2iKyaTKhu0dsQ/view?usp=share_link



## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation
Instructions on how to install and set up your project.

```bash
# Clone the repository
git clone https://github.com/faviasono/bookai.git

# Navigate to the project directory
cd bookai

# Install dependencies
pip install .
```

## Usage

### 1. Set Up Gemini APIs
Create Gemini APIs in your Google account using **AI Studio**.

### 2. Enable Text-to-Speech
Enable the Text-to-Speech functionality using either **Google Cloud Platform (GCP)** or **Eleven Labs APIs**:
- If using GCP, download the **JSON key** for the Service Account (SA) authorized to call the Text-to-Speech endpoint.

### 3. Obtain Bionic Reader APIs
Generate the required **Bionic Reader APIs** from the [RapidAPI](https://rapidapi.com) platform.

### 4. Create a `.env` File
In the root directory of your project, create a `.env` file, copy the following configurations and replace with your information.


```
GEMINI_API_KEY="XXXXXXXXXX"
ELEVEN_API_KEY="XXXXXXXXXX"
BIONIC_API_KEY="XXXXXXXXXX"

[gcp_service_account]
type = "service_account"
project_id = "PROJECT_ID"
private_key_id = "XXXXXXXXXX"
private_key = "PRIVATE_KEY"
client_email = "CLIENT_EMAIL"
client_id = "XXX"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "CLIENT_CERT_URL"
```


Run the application with the following:
```bash
# streamlit run ui.py

```

## Contributing
Guidelines for contributing to the project.

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
[Andrea Favia](mailto:andrea.faviait@gmail.com)

[Github](https://github.com/faviasono/bookai)



## TODO:

[] Dockerize
[] Deploy on GCP
