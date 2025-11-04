import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def optimize_cv_content(job_description: str, cv_data: dict) -> Dict:
    """
    Utiliza GPT-4 para optimizar el contenido del CV basándose en la descripción del trabajo.
    
    Args:
        job_description: Descripción del puesto de trabajo objetivo
        cv_data: Datos del CV del usuario
    
    Returns:
        Dict con contenido optimizado y sugerencias
    """
    try:
        # Construir prompt para GPT-4
        prompt = f"""
Eres un experto en recursos humanos y redacción de CVs. Tu tarea es optimizar un CV para que coincida perfectamente con la siguiente descripción de trabajo, sin inventar información falsa.

DESCRIPCIÓN DEL TRABAJO:
{job_description}

INFORMACIÓN DEL CANDIDATO:
Nombre: {cv_data.get('personal_info', {}).get('full_name', 'N/A')}
Email: {cv_data.get('personal_info', {}).get('email', 'N/A')}
Resumen actual: {cv_data.get('personal_info', {}).get('summary', 'Sin resumen')}

EXPERIENCIA LABORAL:
{format_experiences(cv_data.get('experiences', []))}

EDUCACIÓN:
{format_education(cv_data.get('education', []))}

HABILIDADES:
{', '.join([s.get('name', '') for s in cv_data.get('skills', [])])}

IDIOMAS:
{format_languages(cv_data.get('languages', []))}

INSTRUCCIONES:
1. Reescribe el resumen profesional para destacar las habilidades más relevantes para el puesto
2. Ajusta las descripciones de experiencia laboral para enfatizar logros relevantes al puesto
3. Reordena y destaca las habilidades más importantes para este trabajo
4. Proporciona 3-5 sugerencias específicas para mejorar el CV
5. NO inventes información falsa - solo reescribe y reorganiza lo existente

FORMATO DE RESPUESTA:
Devuelve un JSON válido con esta estructura:
{{
    "summary": "Resumen profesional optimizado...",
    "experiences": [
        {{
            "job_title": "título original",
            "company": "empresa original",
            "description": "descripción optimizada...",
            "achievements": ["logro 1", "logro 2"]
        }}
    ],
    "skills_order": ["habilidad más relevante", "segunda más relevante", ...],
    "suggestions": [
        "Sugerencia específica 1",
        "Sugerencia específica 2",
        "Sugerencia específica 3"
    ]
}}
"""

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "Eres un experto en optimización de CVs y ATS (Applicant Tracking Systems). Respondes siempre en formato JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )

        import json
        optimized_content = json.loads(response.choices[0].message.content)
        
        return {
            "success": True,
            "optimized_content": optimized_content,
            "suggestions": optimized_content.get("suggestions", [])
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestions": []
        }


def format_experiences(experiences: List[dict]) -> str:
    """Formatea la lista de experiencias para el prompt"""
    if not experiences:
        return "Sin experiencia registrada"
    
    formatted = []
    for exp in experiences:
        formatted.append(
            f"- {exp.get('job_title', 'N/A')} en {exp.get('company', 'N/A')} "
            f"({exp.get('start_date', 'N/A')} - {exp.get('end_date', 'Present')})\n"
            f"  Descripción: {exp.get('description', 'N/A')}"
        )
    return "\n".join(formatted)


def format_education(education: List[dict]) -> str:
    """Formatea la lista de educación para el prompt"""
    if not education:
        return "Sin educación registrada"
    
    formatted = []
    for edu in education:
        formatted.append(
            f"- {edu.get('degree', 'N/A')} en {edu.get('institution', 'N/A')} "
            f"(Graduación: {edu.get('graduation_date', 'N/A')})"
        )
    return "\n".join(formatted)


def format_languages(languages: List[dict]) -> str:
    """Formatea la lista de idiomas para el prompt"""
    if not languages:
        return "Sin idiomas registrados"
    
    return ", ".join([
        f"{lang.get('name', 'N/A')} ({lang.get('proficiency', 'N/A')})"
        for lang in languages
    ])


def generate_cv_suggestions(job_description: str) -> List[str]:
    """
    Genera sugerencias generales para mejorar el CV basándose en la descripción del trabajo.
    """
    try:
        prompt = f"""
Basándote en esta descripción de trabajo, proporciona 5 sugerencias concretas sobre qué debería incluir un candidato en su CV:

DESCRIPCIÓN DEL TRABAJO:
{job_description}

Devuelve un JSON con formato:
{{
    "suggestions": [
        "Sugerencia 1",
        "Sugerencia 2",
        "Sugerencia 3",
        "Sugerencia 4",
        "Sugerencia 5"
    ]
}}
"""

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "Eres un experto en recursos humanos. Respondes en formato JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
            response_format={"type": "json_object"}
        )

        import json
        result = json.loads(response.choices[0].message.content)
        return result.get("suggestions", [])

    except Exception as e:
        return [f"Error al generar sugerencias: {str(e)}"]
