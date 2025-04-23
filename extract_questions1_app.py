import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re

st.set_page_config(page_title="PDF MCQ Extractor", layout="wide")
st.title("📄 Extract MCQs from PDF and Save to CSV")

uploaded_file = st.file_uploader("Upload your PDF file", type=["pdf"])

if uploaded_file:
    # Extract text from PDF
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()

    # Regex pattern to match your updated format
    pattern = re.compile(
        r"Question\s+#(\d+)\s*Topic\s+\d+\s*\n+([\s\S]*?)\nA\.\s*(.*?)\nB\.\s*(.*?)\nC\.\s*(.*?)\nD\.\s*(.*?)\n+Correct Answer:\s*([A-D])",
        re.MULTILINE
    )

    matches = pattern.findall(text)

    data = []
    for match in matches:
        q_num, question, a, b, c, d, correct = match
        data.append({
            "Question Number": q_num.strip(),
            "Question": question.strip().replace("\n", " "),
            "A": a.strip(),
            "B": b.strip(),
            "C": c.strip(),
            "D": d.strip(),
            "Correct Answer": correct.strip()
        })

    if data:
        df = pd.DataFrame(data)
        st.success(f"✅ Extracted {len(df)} questions")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", data=csv, file_name="mcq_output.csv", mime="text/csv")
    else:
        st.warning("No matching questions found. Make sure the PDF uses the expected format.")
