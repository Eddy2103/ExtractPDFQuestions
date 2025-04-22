import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd

st.set_page_config(page_title="MCQ PDF Extractor", layout="wide")
st.title("📄 Multiple Choice Question Extractor from PDF")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    # Read the text from the PDF
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()

    # Pattern for extracting question blocks
    pattern = re.compile(
        r"Question\s+#(\d+)\s*\n(.*?)(?=\nA\.)\nA\.\s*(.*?)\nB\.\s*(.*?)\nC\.\s*(.*?)\nD\.\s*(.*?)\n+Correct Answer\s*:\s*([A-D])",
        re.DOTALL
    )

    matches = pattern.findall(text)

    data = []
    for match in matches:
        question_number, question_text, a, b, c, d, correct = match
        data.append({
            "Question Number": question_number.strip(),
            "Question": question_text.strip().replace("\n", " "),
            "A": a.strip(),
            "B": b.strip(),
            "C": c.strip(),
            "D": d.strip(),
            "Correct Answer": correct.strip()
        })

    if data:
        df = pd.DataFrame(data)
        st.success(f"✅ Extracted {len(df)} questions.")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name="extracted_questions.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️ No questions matched the expected format. Please check your PDF formatting.")
