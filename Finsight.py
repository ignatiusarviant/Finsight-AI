import os
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
import streamlit as st
import PyPDF2
import io

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from pdfminer.high_level import extract_text as pdfminer_extract_text
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False

# Set your OpenAI API key here

"""Use the code below only if you want to launch locally with Streamlit (.env method)"""
# from dotenv import load_dotenv
# load_dotenv(dotenv_path="C:\\Users\\HP\\Downloads\\Python Only\\Financial Langchain chatbot\\support.env")

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
else:
    raise ValueError("OPENAI_API_KEY not found! Check your .env file or Azure App Setting.")

# Define a template with financial context
template = """
You are an AI assistant specialized in financial topics. You can provide information about:
- Stock market investing
- Personal finance
- Banking and loans
- Retirement planning
- Tax strategies
- Financial analysis

You also have access to uploaded PDF documents. When answering questions, you can reference information from these documents if relevant.

{pdf_context}

Current conversation:
{history}
Human: {input}
AI Assistant:"""

prompt = PromptTemplate(
    input_variables=["history", "input"],
    template="""
You are an AI assistant specialized in financial topics. You can provide information about:
- Stock market investing
- Personal finance
- Banking and loans
- Retirement planning
- Tax strategies
- Financial analysis

Current conversation:
{history}
Human: {input}
AI Assistant:"""
)

# Initialize the language model
# You can adjust temperature (0.0 to 1.0) - lower for more focused responses
llm = ChatOpenAI(model_name="gpt-4o", temperature=0.3)

# Set up conversation memory
memory = ConversationBufferMemory()

# Create the conversation chain
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    prompt=prompt,
    verbose=True  # Set to False in production
)

# Streamlit interface with improved styling and features
st.set_page_config(page_title="Finsight-AI", page_icon="💡")

# Apply dark theme styling
st.markdown("""
<style>
    html, body, .stApp {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .block-container, .main {
        background-color: #1E1E1E;
    }
    .stMarkdown, .stText, h1, h2, h3, p {
        color: #FFFFFF !important;
    }
    .stTextInput > div > div > input {
        caret-color: white;
        background-color: #2D2D2D;
        color: #FFFFFF;
    }
    .stButton > button {
        background-color: #4D4D4D;
        color: white;
    }
    .stSidebar {
        background-color: #252526;
    }
    .stSidebar .stMarkdown {
        color: #E0E0E0 !important;
    }
    header, footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

st.title("💡Finsight-AI")
st.markdown("""
This chatbot can help you with various financial topics including:
- Financial Statement Reader
- Stock market investing
- Personal finance
- Banking and loans
- Retirement planning
- Tax strategies
- Financial analysis
""")

# Initialize PDF storage
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""

# Function to extract text from PDF
def extract_pdf_text(pdf_file):
    # Reset file pointer to beginning
    pdf_file.seek(0)
    
    # Try PyPDF2 first
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        if text.strip():  # If we got text, return it
            return text
    except Exception as e:
        error_msg = str(e)
        if "PyCryptodome is required for AES algorithm" in error_msg:
            st.warning("⚠️ The PDF is encrypted with AES. Trying a different reader...")
        else:
            st.warning(f"⚠️ PyPDF2 failed: {error_msg}. Trying a different reader...")
    
    # Try pdfplumber as fallback
    if PDFPLUMBER_AVAILABLE:
        try:
            pdf_file.seek(0)
            with pdfplumber.open(pdf_file) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                if text.strip():
                    st.success("✅ Successfully read the PDF using pdfplumber!")
                    return text
        except Exception as e:
            st.warning(f"⚠️ pdfplumber also failed: {str(e)}")
    
    # Try pdfminer as last resort
    if PDFMINER_AVAILABLE:
        try:
            pdf_file.seek(0)
            text = pdfminer_extract_text(pdf_file)
            if text.strip():
                st.success("✅ Successfully read the PDF using pdfminer!")
                return text
        except Exception as e:
            st.warning(f"⚠️ pdfminer also failed: {str(e)}")
    
    # If all methods failed
    st.error("❌ All PDF reading methods failed. Possible reasons:")
    st.error("1. The PDF is password-protected")
    st.error("2. The PDF uses an unsupported encryption method")
    st.error("3. The PDF file is corrupted or has a non-standard format")

    return ""

# Function to create conversation chain with PDF context
def create_conversation_chain():
    return ConversationChain(
        llm=llm,
        memory=ConversationBufferMemory(),
        prompt=prompt,
        verbose=True
    )

# Initialize chat sessions
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {
        "Tab 1": {
            "chat_history": [],
            "scroll_to_index": None,
            "input_counter": 0,
            "memory": ConversationBufferMemory(),
            "conversation": create_conversation_chain()
        }
    }

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Tab 1"

if "tab_counter" not in st.session_state:
    st.session_state.tab_counter = 1

# PDF Upload Section
st.markdown("### 📄 Upload PDF Document")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Extract text from PDF
    pdf_text = extract_pdf_text(uploaded_file)
    if pdf_text:
        st.session_state.pdf_content = pdf_text
        st.success(f"✅ PDF uploaded successfully! ({len(pdf_text)} characters extracted)")
        
        # Show preview of PDF content
        with st.expander("📖 Preview PDF Content"):
            st.text_area("PDF Content Preview", pdf_text[:1000] + "..." if len(pdf_text) > 1000 else pdf_text, height=200)

# Create tabs
tab_names = list(st.session_state.chat_sessions.keys())
tabs = st.tabs(tab_names)

# Handle each tab
for i, tab_name in enumerate(tab_names):
    with tabs[i]:
        current_session = st.session_state.chat_sessions[tab_name]
        
        # Create a container for the chat history
        chat_container = st.container()
        
        # Display chat history for current tab
        with chat_container:
            for idx, (sender, message) in enumerate(current_session["chat_history"]):
                # Add highlight if this is the target conversation
                highlight_style = ""
                if current_session["scroll_to_index"] is not None and idx == current_session["scroll_to_index"]:
                    highlight_style = "border: 2px solid #FFD700; box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);"
                    current_session["scroll_to_index"] = None  # Reset after highlighting
                
                if sender == "You":
                    st.markdown(f"<div style='background-color: #2D3748; padding: 10px; border-radius: 5px; margin-bottom: 10px; {highlight_style}'><strong style='color: #63B3ED;'>{sender}:</strong> <span style='color: #E2E8F0;'>{message}</span></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='background-color: #1A202C; padding: 10px; border-radius: 5px; margin-bottom: 10px; {highlight_style}'><strong style='color: #68D391;'>{sender}:</strong> <span style='color: #E2E8F0;'>{message}</span></div>", unsafe_allow_html=True)

        # User input area for current tab
        user_input = st.text_input("Ask me anything about finance:", key=f"user_input_{tab_name}_{current_session['input_counter']}")

        # Create two equal columns for the buttons
        col1, col2 = st.columns([1,1])
        with col1:
            search = st.button("🔍 Send Message", key=f"search_{tab_name}")
        with col2:
            new_chat = st.button("💬 New Chat", key=f"new_chat_{tab_name}")

        if search and user_input:
            with st.spinner("Thinking..."):
                try:
                    # Prepare input with PDF context if available
                    full_input = user_input
                    if st.session_state.pdf_content:
                        full_input = f"Context from uploaded PDF document:\n{st.session_state.pdf_content}\n\nUser question: {user_input}"
                    
                    # Get response from conversation chain
                    response = current_session["conversation"].predict(input=full_input)
                    
                    current_session["chat_history"].append(("You", user_input))
                    current_session["chat_history"].append(("Assistant", response))
                    # Clear the input box after sending by incrementing counter
                    current_session["input_counter"] += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

        if new_chat:
            # Create new tab
            st.session_state.tab_counter += 1
            new_tab_name = f"Tab {st.session_state.tab_counter}"
            st.session_state.chat_sessions[new_tab_name] = {
                "chat_history": [],
                "scroll_to_index": None,
                "input_counter": 0,
                "memory": ConversationBufferMemory(),
                "conversation": create_conversation_chain()
            }
            st.session_state.active_tab = new_tab_name
            st.rerun()

with st.sidebar:
    st.markdown("🕓 Previous Questions")
    
    # Show previous questions for all tabs
    for tab_name, session in st.session_state.chat_sessions.items():
        if session["chat_history"]:
            st.markdown(f"**{tab_name}:**")
            for idx, (sender, message) in enumerate(session["chat_history"]):
                if sender == "You":
                    if st.button(f"📝 {message}", key=f"history_{tab_name}_{idx}"):
                        # Set scroll target to highlight the question-answer pair
                        session["scroll_to_index"] = idx
                        st.rerun()
