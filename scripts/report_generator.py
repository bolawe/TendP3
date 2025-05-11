from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from openai import OpenAI
import os

client = OpenAI()

def analyze_tender_content(text):
    """Extract key sections using AI"""
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": """You are a tender analysis expert. Extract:
            1. PROJECT_TITLE
            2. KEY_REQUIREMENTS (bulleted list)
            3. TECHNICAL_SPECS (table-ready format)
            4. METHODOLOGY_REQUIREMENTS (focus on technical processes)"""},
            {"role": "user", "content": text}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

def create_technical_doc(analysis, filename):
    doc = Document()
    
    # Cover Page
    doc.add_heading('TECHNICAL PROPOSAL', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().add_run("For: " + analysis.get("PROJECT_TITLE", "")).bold = True
    doc.add_page_break()
    
    # Methodology Section (Emphasized)
    doc.add_heading('Technical Methodology', 1)
    for req in analysis.get("METHODOLOGY_REQUIREMENTS", "").split('\n'):
        if req.strip():
            p = doc.add_paragraph(style='ListBullet')
            p.add_run(req.strip()).bold = True
    
    # Technical Specs Table
    doc.add_heading('Compliance Matrix', 1)
    table = doc.add_table(rows=1, cols=3)
    table.style = 'LightShading-Accent1'
    table.cell(0,0).text = "Requirement"
    table.cell(0,1).text = "Our Approach"
    table.cell(0,2).text = "Compliance"
    
    # Save
    doc.save(f"outputs/{filename}_report.docx")

def generate_reports():
    for file in os.listdir("outputs"):
        if file.endswith("_cleaned.txt"):
            with open(f"outputs/{file}", "r") as f:
                text = f.read()
            
            analysis = analyze_tender_content(text)
            create_technical_doc(parse_ai_response(analysis), 
                               os.path.splitext(file)[0])

def parse_ai_response(text):
    """Convert AI response to structured dict"""
    sections = {}
    current_section = None
    for line in text.split('\n'):
        if line.startswith(('1.', '2.', '3.', '4.')):
            current_section = line.split('.')[1].strip().upper()
            sections[current_section] = []
        elif current_section and line.strip():
            sections[current_section].append(line.strip())
    return sections

if __name__ == "__main__":
    generate_reports()
