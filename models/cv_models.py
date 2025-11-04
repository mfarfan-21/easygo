from pydantic import BaseModel, EmailStr
from typing import List, Optional


class PersonalInfo(BaseModel):
    """Información personal del usuario"""
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    summary: Optional[str] = None


class Experience(BaseModel):
    """Experiencia laboral"""
    job_title: str
    company: str
    location: Optional[str] = None
    start_date: str
    end_date: Optional[str] = "Present"
    description: str
    achievements: Optional[List[str]] = []


class Education(BaseModel):
    """Educación"""
    degree: str
    institution: str
    location: Optional[str] = None
    graduation_date: str
    gpa: Optional[str] = None
    honors: Optional[str] = None


class Skill(BaseModel):
    """Habilidad técnica o blanda"""
    name: str
    level: Optional[str] = None  # Beginner, Intermediate, Advanced, Expert


class Language(BaseModel):
    """Idioma"""
    name: str
    proficiency: str  # Native, Fluent, Advanced, Intermediate, Basic


class CVRequest(BaseModel):
    """Solicitud completa para generar un CV"""
    job_description: str
    personal_info: PersonalInfo
    experiences: List[Experience] = []
    education: List[Education] = []
    skills: List[Skill] = []
    languages: List[Language] = []
    additional_sections: Optional[dict] = {}  # Para certificaciones, proyectos, etc.


class CVResponse(BaseModel):
    """Respuesta con el CV optimizado"""
    success: bool
    message: str
    optimized_content: Optional[dict] = None
    pdf_url: Optional[str] = None
    suggestions: Optional[List[str]] = []
