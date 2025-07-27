# Finsight-AI

Finsight-AI is a PDF-based financial assistant chatbot built using Streamlit and LangChain.  
It is designed to help users extract insights from uploaded financial documents. In addition, 
my model is only to answer the financial-related questions. 

## Features

- Financial Statement Reader (PDF upload with fallback extraction methods)
- Multi-session Chat Interface with Conversation Memory
- Stock Market, Personal Finance, and Banking Question Answering
- Tax Strategy and Retirement Planning Assistance
- Built with LangChain, OpenAI API, and Streamlit
- Custom Dark Mode Interface for Enhanced Readability

## Tech Stack

- Python 3.11
- Streamlit
- LangChain
- OpenAI API
- pdfplumber / PyPDF2

## Usage

1. Upload your PDF financial report
2. Ask questions related to the content
3. Receive instant responses from the AI assistant

## Installation

```bash
pip install -r requirements.txt
streamlit run Fininsight.py
```

## Setup Instructions

## 1. Install Dependencies

Make sure you have Python 3.8 or later installed. Then, install the required packages by running:

```bash
pip install -r requirements.txt
```

## 2. Set Environment Variables

Create a .env file in the project directory and add your OpenAI API key:

```bash
OPENAI_API_KEY=your_openai_api_key
```

Please make sure the path to the .env file is correctly referenced in the code, if necessary.

## 3. Run the Application
Start the Streamlit app by running the following command:

```bash
streamlit run Finsight.py
```

The application will open in your default browser. You can now upload a PDF file and interact with the financial assistant.
