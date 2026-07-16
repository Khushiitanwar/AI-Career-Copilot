import pdfplumber
import io
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extracts text from a PDF file (either file path or file-like bytes object).
    """
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def generate_tailored_pdf(sections, output_path: str):
    """
    Generates a beautifully styled professional resume PDF.
    
    sections: list of dict, e.g.
    [
        {"title": "Header", "content": {"name": "John Doe", "email": "john@example.com", "phone": "123-456-7890", "location": "Bangalore", "links": "github.com/johndoe | linkedin.com/in/johndoe"}},
        {"title": "Professional Summary", "content": "Experienced machine learning engineer..."},
        {"title": "Skills", "content": "Python, PyTorch, LangChain, LangGraph, Qdrant, SQL, Docker, AWS"},
        {"title": "Work Experience", "content": [
            {"role": "AI Developer Intern", "company": "TechCorp", "dates": "Jan 2025 - Present", "description": ["Developed multi-agent systems using LangGraph", "Reduced latency by 20%"]},
            {"role": "Software Engineer", "company": "DevStudio", "dates": "Jun 2023 - Dec 2024", "description": ["Built REST APIs with FastAPI", "Managed SQL databases"]}
        ]},
        {"title": "Education", "content": [
            {"degree": "B.Tech in Computer Science", "school": "IIT Bangalore", "dates": "2020 - 2024", "description": "GPA: 9.2/10"}
        ]}
    ]
    """
    # Initialize document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles for Resume
    title_style = ParagraphStyle(
        'NameHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B'), # Slate 800
        alignment=1 # Centered
    )
    
    subtitle_style = ParagraphStyle(
        'SubHeader',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#64748B'), # Slate 500
        alignment=1 # Centered
    )
    
    section_heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0F172A'), # Slate 900
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'ResumeBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#334155'), # Slate 700
    )
    
    bullet_style = ParagraphStyle(
        'ResumeBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#334155'), # Slate 700
        leftIndent=15,
        firstLineIndent=-10,
        spaceBefore=1,
        spaceAfter=1
    )
    
    item_header_style = ParagraphStyle(
        'ItemHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )
    
    item_right_style = ParagraphStyle(
        'ItemRight',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#64748B'),
        alignment=2 # Right aligned
    )

    story = []
    
    # Generate Story Flow
    for sec in sections:
        title = sec.get("title", "")
        content = sec.get("content")
        
        if not content:
            continue
            
        if title == "Header":
            # Header section format
            name = content.get("name", "")
            email = content.get("email", "")
            phone = content.get("phone", "")
            location = content.get("location", "")
            links = content.get("links", "")
            
            story.append(Paragraph(name, title_style))
            story.append(Spacer(1, 4))
            
            # Combine contact details
            contact_parts = []
            if email: contact_parts.append(email)
            if phone: contact_parts.append(phone)
            if location: contact_parts.append(location)
            if links: contact_parts.append(links)
            
            contact_str = "  |  ".join(contact_parts)
            story.append(Paragraph(contact_str, subtitle_style))
            story.append(Spacer(1, 8))
            
            # Add line divider
            divider = Table([[""]], colWidths=[7.5 * inch])
            divider.setStyle(TableStyle([
                ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(divider)
            story.append(Spacer(1, 4))
            
        else:
            # Standard section header
            story.append(Paragraph(title, section_heading_style))
            
            # Add small underline for the section
            section_line = Table([[""]], colWidths=[7.5 * inch])
            section_line.setStyle(TableStyle([
                ('LINEBELOW', (0,0), (-1,-1), 0.75, colors.HexColor('#E2E8F0')),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(section_line)
            story.append(Spacer(1, 4))
            
            if isinstance(content, str):
                # Simple text/skills content
                story.append(Paragraph(content, body_style))
                story.append(Spacer(1, 6))
                
            elif isinstance(content, list):
                # List of items (jobs, degrees, projects)
                for item in content:
                    if isinstance(item, str):
                        story.append(Paragraph(f"&bull; {item}", bullet_style))
                    elif isinstance(item, dict):
                        # Job or Education Item
                        left_title = item.get("role") or item.get("degree") or item.get("title") or ""
                        company = item.get("company") or item.get("school") or item.get("organization") or ""
                        dates = item.get("dates") or item.get("date") or ""
                        
                        # Format item headers side-by-side using Table
                        header_left_txt = f"{left_title}"
                        if company:
                            header_left_txt += f" at {company}"
                            
                        item_header_tbl = Table(
                            [[Paragraph(header_left_txt, item_header_style), Paragraph(dates, item_right_style)]],
                            colWidths=[5.5 * inch, 2.0 * inch]
                        )
                        item_header_tbl.setStyle(TableStyle([
                            ('VALIGN', (0,0), (-1,-1), 'TOP'),
                            ('LEFTPADDING', (0,0), (-1,-1), 0),
                            ('RIGHTPADDING', (0,0), (-1,-1), 0),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                            ('TOPPADDING', (0,0), (-1,-1), 1),
                        ]))
                        story.append(item_header_tbl)
                        
                        # Add item description bullets or text
                        desc = item.get("description")
                        if isinstance(desc, str):
                            story.append(Paragraph(desc, body_style))
                        elif isinstance(desc, list):
                            for bullet in desc:
                                story.append(Paragraph(f"&bull; {bullet}", bullet_style))
                        
                        story.append(Spacer(1, 4))
                story.append(Spacer(1, 4))
                
    doc.build(story)
