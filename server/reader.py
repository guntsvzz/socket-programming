
import os
import PyPDF2
import docx
import pytesseract
from pdf2image import convert_from_path

def reader(file_path):
    """
    Reads and extracts text from PDF or DOCX files, with OCR fallback for PDFs.
    """
    _, file_extension = os.path.splitext(file_path)
    text = ""
    
    try:
        if file_extension.lower() == '.pdf':
            with open(file_path, 'rb') as file:
                # Attempt to extract text with PyPDF2
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()#.replace(" ","")
                    if page_text:
                        text += page_text

        elif file_extension.lower() == '.docx':
            # Extract text from DOCX files
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + '\n'

        return {"content": text.strip() if text else "No text found"}
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

