import os
from openai import OpenAI
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def init_openai_client():
    """Initialize OpenAI client with version-compatible syntax"""
    try:
        return OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    except KeyError:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    except Exception as e:
        raise RuntimeError(f"OpenAI initialization failed: {str(e)}")

def generate_report(client, text):
    """Generate structured report content"""
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": """Extract:
            1. PROJECT_TITLE
            2. KEY_REQUIREMENTS (bullets)
            3. TECHNICAL_SPECS (table format)
            4. METHODOLOGY (technical steps)"""},
            {"role": "user", "content": text[:15000]}
        ],
        temperature=0.3
    )
    return parse_response(response.choices[0].message.content)

def parse_response(text):
    """Parse AI response into sections"""
    sections = {}
    current = None
    for line in text.split('\n'):
        if line.startswith(('1.', '2.', '3.', '4.')):
            current = line.split('.')[1].strip().upper()
            sections[current] = []
        elif current and line.strip():
            sections[current].append(line.strip())
    return sections

def create_doc(analysis, filename):
    """Generate Word document"""
    doc = Document()
    
    # Cover Page
    doc.add_heading('TECHNICAL PROPOSAL', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"For: {analysis.get('PROJECT_TITLE', [''])[0]}")
    doc.add_page_break()
    
    # Methodology Section
    doc.add_heading('Technical Methodology', 1)
    for step in analysis.get('METHODOLOGY', []):
        doc.add_paragraph(step, style='ListBullet')
    
    doc.save(f"outputs/{filename}_report.docx")

if __name__ == "__main__":
    try:
        client = init_openai_client()
        for file in os.listdir("outputs"):
            if file.endswith("_cleaned.txt"):
                with open(f"outputs/{file}") as f:
                    analysis = generate_report(client, f.read())
                    create_doc(analysis, file.replace('_cleaned.txt', ''))
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)
