import os
from openai import OpenAI
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def init_openai_client():
    """Safe OpenAI client initialization"""
    try:
        # Explicitly use the new client syntax
        return OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    except Exception as e:
        print(f"❌ OpenAI initialization failed: {str(e)}")
        raise

def generate_report(client, text):
    """Generate structured report content"""
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": """Extract key tender sections:
                - PROJECT_TITLE
                - TECHNICAL_REQUIREMENTS
                - METHODOLOGY_FOCUS
                - COMPLIANCE_ITEMS"""},
                {"role": "user", "content": text[:15000]}
            ],
            temperature=0.3
        )
        return parse_response(response.choices[0].message.content)
    except Exception as e:
        print(f"❌ Report generation failed: {str(e)}")
        raise

def parse_response(text):
    """Parse AI response into structured data"""
    sections = {}
    current_section = None
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('- '):
            if current_section:
                sections[current_section].append(line[2:])
        else:
            current_section = line.replace(':', '').upper()
            sections[current_section] = []
    
    return sections

def create_word_doc(analysis, filename):
    """Generate professional Word document"""
    doc = Document()
    
    # Cover Page
    title = doc.add_paragraph()
    title_run = title.add_run("TECHNICAL PROPOSAL")
    title_run.font.size = Pt(24)
    title_run.bold = True
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    if analysis.get('PROJECT_TITLE'):
        doc.add_paragraph(f"Project: {analysis['PROJECT_TITLE'][0]}")
    
    doc.add_page_break()
    
    # Methodology Section
    if analysis.get('METHODOLOGY_FOCUS'):
        doc.add_heading('Technical Methodology', 1)
        for item in analysis['METHODOLOGY_FOCUS']:
            doc.add_paragraph(item, style='ListBullet')
    
    # Compliance Section
    if analysis.get('COMPLIANCE_ITEMS'):
        doc.add_heading('Compliance Matrix', 1)
        table = doc.add_table(rows=1, cols=2)
        table.style = 'LightShading-Accent1'
        hdr = table.rows[0].cells
        hdr[0].text = "Requirement"
        hdr[1].text = "Our Solution"
        
        for item in analysis['COMPLIANCE_ITEMS']:
            row = table.add_row().cells
            row[0].text = item
            row[1].text = "Compliant"  # Replace with actual solutions
    
    doc.save(f"outputs/{filename}_report.docx")

if __name__ == "__main__":
    try:
        client = init_openai_client()
        os.makedirs("outputs", exist_ok=True)
        
        for file in os.listdir("outputs"):
            if file.endswith("_cleaned.txt"):
                print(f"📄 Processing {file}...")
                with open(f"outputs/{file}", 'r') as f:
                    analysis = generate_report(client, f.read())
                    create_word_doc(analysis, file.replace('_cleaned.txt', ''))
                
    except Exception as e:
        print(f"⛔ Critical error: {str(e)}")
        exit(1)
