from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # PostgreSQL - pode usar URL completa ou variáveis individuais
    postgres_url: Optional[str] = None
    postgres_host: Optional[str] = None
    postgres_port: int = 5432
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None
    
    # Google Gemini
    gemini_api_key: str
    
    # OpenAI
    openai_api_key: str
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Configurações
    upload_dir: str = "uploads"
    images_dir: str = "images"
    max_file_size: int = 10485760  # 10MB
    base_url: str = "http://localhost:8000"  # URL base para servir imagens
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_postgres_url(self) -> str:
        """Retorna a URL de conexão PostgreSQL"""
        # Se URL completa fornecida, usa ela
        if self.postgres_url:
            # Converter postgres:// para postgresql:// se necessário
            return self.postgres_url.replace("postgres://", "postgresql://", 1)
        
        # Caso contrário, monta a partir das variáveis individuais
        if not all([self.postgres_host, self.postgres_user, self.postgres_password, self.postgres_db]):
            raise ValueError("Forneça POSTGRES_URL completa ou todas as variáveis individuais (host, user, password, db)")
        
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


settings = Settings()

