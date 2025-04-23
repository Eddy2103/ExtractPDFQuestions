import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
import tabula
import tempfile
import os

st.title("PDF to CSV Converter")

def extract_text_from_pdf(pdf_file):
    """Extract text from text-based PDFs"""
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_tables_from_pdf(pdf_file):
    """Extract tables from PDF using tabula"""
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(pdf_file.getvalue())
        tmp_file_path = tmp_file.name
    
    try:
        # Read all tables from the PDF
        dfs = tabula.read_pdf(tmp_file_path, pages='all', multiple_tables=True)
    finally:
        # Clean up the temporary file
        os.unlink(tmp_file_path)
    
    return dfs

def main():
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    
    if uploaded_file is not None:
        st.success("File uploaded successfully!")
        
        # Try extracting tables first
        try:
            dfs = extract_tables_from_pdf(uploaded_file)
            
            if len(dfs) > 0:
                st.success(f"Found {len(dfs)} table(s) in the PDF")
                
                for i, df in enumerate(dfs):
                    st.subheader(f"Table {i+1}")
                    st.write(df)
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"Download Table {i+1} as CSV",
                        data=csv,
                        file_name=f"table_{i+1}.csv",
                        mime='text/csv',
                    )
            else:
                st.warning("No tables found in PDF. Trying text extraction...")
                text = extract_text_from_pdf(uploaded_file)
                if text.strip():
                    st.subheader("Extracted Text")
                    st.text(text)
                    
                    # Convert text to single-column DataFrame
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    df = pd.DataFrame(lines, columns=["Text"])
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Text as CSV",
                        data=csv,
                        file_name="extracted_text.csv",
                        mime='text/csv',
                    )
                else:
                    st.error("No text could be extracted from the PDF.")
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
