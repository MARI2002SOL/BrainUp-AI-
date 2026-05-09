import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# =========================
# LOAD ENV VARIABLES
# =========================

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
MONGODB_URI = st.secrets["MONGODB_URI"]
# =========================
# GEMINI CONFIG
# =========================

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash"
)

# =========================
# MONGODB CONFIG
# =========================

client = MongoClient(MONGODB_URI)

db = client["scientific_papers"]

collection = db["summaries"]

# =========================
# STREAMLIT UI
# =========================

st.set_page_config(
    page_title="AI Scientific Paper Summarizer",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Scientific Paper Summarizer")

st.markdown("""
Upload a scientific paper in PDF format and Gemini AI will generate:

- General Summary
- Main Objective
- Methodology
- Key Results
- Limitations
- Conclusions
- Simple Explanation
""")

# =========================
# FILE UPLOAD
# =========================

uploaded_file = st.file_uploader(
    "Upload your scientific paper",
    type=["pdf"]
)

# =========================
# PROCESS PDF
# =========================

if uploaded_file is not None:

    st.success("PDF uploaded successfully ✅")

    # Extract text from PDF
    reader = PdfReader(uploaded_file)

    paper_text = ""

    for page in reader.pages:

        text = page.extract_text()

        if text:
            paper_text += text

    # Show extracted text size
    st.info(f"Extracted {len(paper_text)} characters from PDF")

    # =========================
    # GENERATE SUMMARY BUTTON
    # =========================

    if st.button("Generate AI Summary"):

        with st.spinner("Gemini is analyzing the paper..."):

            try:

                # Limit text size
                limited_text = paper_text[:15000]

                # Prompt
                prompt = f"""
                You are an expert scientific research assistant.

                Analyze the following scientific article and generate:

                1. General Summary
                2. Main Objective
                3. Methodology
                4. Key Results
                5. Limitations
                6. Conclusions
                7. Simple Explanation for students

                Make the response clear and well structured.

                ARTICLE:
                {limited_text}
                """

                # Gemini response
                response = model.generate_content(prompt)

                summary = response.text

                # =========================
                # DISPLAY RESULTS
                # =========================

                st.subheader("📄 AI Summary")

                st.write(summary)

                # =========================
                # SAVE TO MONGODB
                # =========================

                document = {
                    "filename": uploaded_file.name,
                    "summary": summary
                }

                collection.insert_one(document)

                st.success("Summary saved to MongoDB ✅")

            except Exception as e:

                st.error(f"Error: {str(e)}")