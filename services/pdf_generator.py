from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime
import os


def generate_cv_pdf(cv_data: dict, optimized_content: dict = None) -> BytesIO:
    """
    Genera un PDF profesional del CV usando ReportLab.
    
    Args:
        cv_data: Datos originales del CV
        optimized_content: Contenido optimizado por GPT-4 (opcional)
    
    Returns:
        BytesIO con el PDF generado
    """
    buffer = BytesIO()
    
    # Crear documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Contenedor para los elementos del PDF
    story = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#4F46E5'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#6B7280'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#4F46E5'),
        spaceAfter=6,
        spaceBefore=12,
        borderWidth=0,
        borderColor=colors.HexColor('#E5E7EB'),
        borderPadding=0,
        fontName='Helvetica-Bold',
        borderRadius=None,
        backColor=None,
        leftIndent=0,
        rightIndent=0,
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        leading=14
    )
    
    job_title_style = ParagraphStyle(
        'JobTitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#1F2937'),
        fontName='Helvetica-Bold',
        spaceAfter=2
    )
    
    # Obtener información personal
    personal = cv_data.get('personal_info', {})
    
    # Nombre
    story.append(Paragraph(personal.get('full_name', ''), title_style))
    
    # Información de contacto
    contact_parts = []
    if personal.get('email'):
        contact_parts.append(personal['email'])
    if personal.get('phone'):
        contact_parts.append(personal['phone'])
    if personal.get('location'):
        contact_parts.append(personal['location'])
    
    if contact_parts:
        story.append(Paragraph(' | '.join(contact_parts), subtitle_style))
    
    # Links (LinkedIn, Portfolio)
    links_parts = []
    if personal.get('linkedin'):
        links_parts.append(f"<link href='{personal['linkedin']}'>LinkedIn</link>")
    if personal.get('portfolio'):
        links_parts.append(f"<link href='{personal['portfolio']}'>Portfolio</link>")
    
    if links_parts:
        story.append(Paragraph(' | '.join(links_parts), subtitle_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Resumen profesional
    summary = None
    if optimized_content and optimized_content.get('summary'):
        summary = optimized_content['summary']
    elif personal.get('summary'):
        summary = personal['summary']
    
    if summary:
        story.append(Paragraph('PROFESSIONAL SUMMARY', heading_style))
        story.append(Paragraph(summary, body_style))
        story.append(Spacer(1, 0.1*inch))
    
    # Experiencia laboral
    experiences = cv_data.get('experiences', [])
    if experiences:
        story.append(Paragraph('PROFESSIONAL EXPERIENCE', heading_style))
        
        for i, exp in enumerate(experiences):
            # Título y empresa
            job_title = exp.get('job_title', '')
            company = exp.get('company', '')
            story.append(Paragraph(f"<b>{job_title}</b> - {company}", job_title_style))
            
            # Fechas y ubicación
            date_location = []
            start = exp.get('start_date', '')
            end = exp.get('end_date', 'Present')
            if start:
                date_location.append(f"{start} - {end}")
            if exp.get('location'):
                date_location.append(exp['location'])
            
            if date_location:
                story.append(Paragraph(' | '.join(date_location), 
                                     ParagraphStyle('DateLocation', parent=body_style, 
                                                  fontSize=9, textColor=colors.HexColor('#6B7280'))))
            
            # Descripción (usar optimizada si existe)
            description = exp.get('description', '')
            if optimized_content and 'experiences' in optimized_content:
                opt_exp = next((e for e in optimized_content['experiences'] 
                              if e.get('job_title') == job_title), None)
                if opt_exp:
                    description = opt_exp.get('description', description)
            
            if description:
                story.append(Paragraph(description, body_style))
            
            # Logros
            achievements = exp.get('achievements', [])
            if optimized_content and 'experiences' in optimized_content:
                opt_exp = next((e for e in optimized_content['experiences'] 
                              if e.get('job_title') == job_title), None)
                if opt_exp and opt_exp.get('achievements'):
                    achievements = opt_exp['achievements']
            
            if achievements:
                for achievement in achievements:
                    story.append(Paragraph(f"• {achievement}", body_style))
            
            if i < len(experiences) - 1:
                story.append(Spacer(1, 0.1*inch))
    
    # Educación
    education = cv_data.get('education', [])
    if education:
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph('EDUCATION', heading_style))
        
        for edu in education:
            degree = edu.get('degree', '')
            institution = edu.get('institution', '')
            story.append(Paragraph(f"<b>{degree}</b>", job_title_style))
            story.append(Paragraph(institution, body_style))
            
            grad_date = edu.get('graduation_date', '')
            if grad_date:
                story.append(Paragraph(f"Graduated: {grad_date}", 
                                     ParagraphStyle('GradDate', parent=body_style, 
                                                  fontSize=9, textColor=colors.HexColor('#6B7280'))))
            
            if edu.get('gpa'):
                story.append(Paragraph(f"GPA: {edu['gpa']}", body_style))
            
            if edu.get('honors'):
                story.append(Paragraph(f"Honors: {edu['honors']}", body_style))
            
            story.append(Spacer(1, 0.05*inch))
    
    # Habilidades
    skills = cv_data.get('skills', [])
    if skills:
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph('SKILLS', heading_style))
        
        # Ordenar habilidades si hay contenido optimizado
        if optimized_content and optimized_content.get('skills_order'):
            skills_order = optimized_content['skills_order']
            # Reordenar skills basándose en skills_order
            skills_dict = {s.get('name'): s for s in skills}
            ordered_skills = []
            for skill_name in skills_order:
                if skill_name in skills_dict:
                    ordered_skills.append(skills_dict[skill_name])
            # Agregar skills que no estén en el orden
            for skill in skills:
                if skill not in ordered_skills:
                    ordered_skills.append(skill)
            skills = ordered_skills
        
        skills_text = ' • '.join([s.get('name', '') for s in skills if s.get('name')])
        story.append(Paragraph(skills_text, body_style))
    
    # Idiomas
    languages = cv_data.get('languages', [])
    if languages:
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph('LANGUAGES', heading_style))
        
        languages_text = ' • '.join([
            f"{lang.get('name', '')} ({lang.get('proficiency', '')})" 
            for lang in languages if lang.get('name')
        ])
        story.append(Paragraph(languages_text, body_style))
    
    # Construir PDF
    doc.build(story)
    
    # Devolver el buffer al inicio para leerlo
    buffer.seek(0)
    return buffer


def save_pdf_file(buffer: BytesIO, filename: str, output_dir: str = "generated_cvs") -> str:
    """
    Guarda el PDF en el sistema de archivos.
    
    Args:
        buffer: BytesIO con el contenido del PDF
        filename: Nombre del archivo
        output_dir: Directorio de salida
    
    Returns:
        Ruta del archivo guardado
    """
    # Crear directorio si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Generar nombre único con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"cv_{timestamp}_{filename}.pdf"
    filepath = os.path.join(output_dir, safe_filename)
    
    # Guardar archivo
    with open(filepath, 'wb') as f:
        f.write(buffer.getvalue())
    
    return filepath
