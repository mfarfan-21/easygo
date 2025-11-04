"""
OpenAI Service with Retry Logic and Circuit Breaker
Handles OpenAI API calls with automatic retry and circuit breaker protection
"""

from typing import Optional, Dict, Any
import asyncio
from datetime import datetime, timedelta
from openai import AsyncOpenAI
import os


class CircuitBreaker:
    """Simple circuit breaker for OpenAI API"""
    
    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timedelta(seconds=timeout_seconds)
        self.failures = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def record_success(self):
        """Record successful API call"""
        self.failures = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """Record failed API call"""
        self.failures += 1
        self.last_failure_time = datetime.now()
        
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
    
    def can_execute(self) -> bool:
        """Check if request can be executed"""
        if self.state == "CLOSED":
            return True
        
        if self.state == "OPEN":
            # Check if timeout has passed
            if self.last_failure_time and datetime.now() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        
        # HALF_OPEN state
        return True
    
    def get_state(self) -> str:
        """Get current circuit breaker state"""
        return self.state


class OpenAIServiceWithRetry:
    """OpenAI service with retry logic and circuit breaker"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, timeout_seconds=60)
        
        # Configuration
        self.MAX_RETRIES = 3
        self.BASE_DELAY = 1  # seconds
        self.MAX_DELAY = 10  # seconds
        
        # Models
        self.DEFAULT_MODEL = "gpt-4-turbo-preview"
        self.FALLBACK_MODEL = "gpt-3.5-turbo"
    
    async def exponential_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        delay = min(self.BASE_DELAY * (2 ** attempt), self.MAX_DELAY)
        return delay
    
    async def chat_completion_with_retry(
        self,
        messages: list,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        use_fallback: bool = True
    ) -> Dict[str, Any]:
        """
        Make chat completion request with retry logic and circuit breaker
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to gpt-4-turbo-preview)
            temperature: Temperature for generation
            max_tokens: Max tokens to generate
            use_fallback: If True, will try fallback model on failure
        
        Returns:
            Dict with 'content', 'model', 'usage' keys
        
        Raises:
            Exception if all retries fail
        """
        
        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            raise Exception(
                f"Circuit breaker is OPEN. OpenAI API is temporarily unavailable. "
                f"Please try again in a few moments."
            )
        
        model = model or self.DEFAULT_MODEL
        last_exception = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                # Make API call
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Success - reset circuit breaker
                self.circuit_breaker.record_success()
                
                return {
                    "content": response.choices[0].message.content,
                    "model": response.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "finish_reason": response.choices[0].finish_reason
                }
            
            except Exception as e:
                last_exception = e
                error_message = str(e).lower()
                
                # Check if it's a retryable error
                is_retryable = any(err in error_message for err in [
                    "rate limit",
                    "timeout",
                    "connection",
                    "503",
                    "500",
                    "502",
                    "429"
                ])
                
                if not is_retryable:
                    # Non-retryable error (e.g., invalid request)
                    self.circuit_breaker.record_failure()
                    raise e
                
                # Record failure
                self.circuit_breaker.record_failure()
                
                # Last attempt and use_fallback enabled
                if attempt == self.MAX_RETRIES - 1 and use_fallback and model != self.FALLBACK_MODEL:
                    print(f"Trying fallback model: {self.FALLBACK_MODEL}")
                    model = self.FALLBACK_MODEL
                    # Reset attempts for fallback
                    attempt = 0
                    continue
                
                # Not last attempt - wait and retry
                if attempt < self.MAX_RETRIES - 1:
                    delay = await self.exponential_backoff(attempt)
                    print(f"OpenAI API error (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")
                    print(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
        
        # All retries failed
        raise Exception(f"OpenAI API failed after {self.MAX_RETRIES} attempts: {last_exception}")
    
    async def get_cv_suggestions(
        self,
        job_description: str,
        experience_years: int
    ) -> Dict[str, Any]:
        """Get CV suggestions based on job description"""
        
        messages = [
            {
                "role": "system",
                "content": "Eres un experto en optimización de CVs y reclutamiento."
            },
            {
                "role": "user",
                "content": f"""
Basándote en esta descripción de trabajo, genera sugerencias para un CV con {experience_years} años de experiencia:

{job_description}

Proporciona:
1. 5 habilidades clave que debe incluir
2. 3 logros cuantificables que sería ideal tener
3. 2 palabras clave importantes para ATS

Formato JSON:
{{
    "skills": ["skill1", "skill2", ...],
    "achievements": ["achievement1", "achievement2", "achievement3"],
    "keywords": ["keyword1", "keyword2"]
}}
"""
            }
        ]
        
        return await self.chat_completion_with_retry(
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )
    
    async def optimize_cv_section(
        self,
        section_content: str,
        job_description: str,
        section_type: str
    ) -> Dict[str, Any]:
        """Optimize a CV section based on job description"""
        
        messages = [
            {
                "role": "system",
                "content": "Eres un experto en optimización de CVs profesionales."
            },
            {
                "role": "user",
                "content": f"""
Optimiza esta sección de CV ({section_type}) para que se ajuste mejor a esta oferta de trabajo:

DESCRIPCIÓN DEL TRABAJO:
{job_description}

SECCIÓN ACTUAL:
{section_content}

Proporciona una versión optimizada que:
1. Use palabras clave relevantes
2. Sea concisa y impactante
3. Destaque logros cuantificables
4. Sea compatible con sistemas ATS

Devuelve solo el texto optimizado, sin explicaciones adicionales.
"""
            }
        ]
        
        return await self.chat_completion_with_retry(
            messages=messages,
            temperature=0.6,
            max_tokens=1000
        )
    
    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            "state": self.circuit_breaker.get_state(),
            "failures": self.circuit_breaker.failures,
            "threshold": self.circuit_breaker.failure_threshold,
            "last_failure": self.circuit_breaker.last_failure_time.isoformat() if self.circuit_breaker.last_failure_time else None
        }


# Global OpenAI service instance
openai_service = OpenAIServiceWithRetry()
