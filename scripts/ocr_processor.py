import pytesseract
from pdf2image import convert_from_path
import os
import re

def clean_text(text):
    """Improve OCR output quality"""
    text = re.sub(r'\s+', ' ', text)  # Remove excessive whitespace
    text = re.sub(r'[^\w\s.,:;-]', '', text)  # Remove special chars
    return text.strip()

def process_documents():
    os.makedirs("outputs", exist_ok=True)
    
    for file in os.listdir("inputs"):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
            print(f"Processing {file}...")
            try:
                # PDF handling
                if file.endswith('.pdf'):
                    images = convert_from_path(f"inputs/{file}")
                    text = "\n".join([pytesseract.image_to_string(img) for img in images])
                # Image handling
                else:
                    text = pytesseract.image_to_string(f"inputs/{file}")
                
                # Save cleaned text
                clean_file = f"{os.path.splitext(file)[0]}_cleaned.txt"
                with open(f"outputs/{clean_file}", "w") as f:
                    f.write(clean_text(text))
                    
            except Exception as e:
                print(f"Error processing {file}: {str(e)}")

if __name__ == "__main__":
    process_documents()
