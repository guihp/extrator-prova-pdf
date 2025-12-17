from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import router
from app.services.database import init_db
import os

app = FastAPI(title="Sistema de Análise de PDFs", version="1.0.0")

# CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Criar diretórios necessários
os.makedirs("uploads", exist_ok=True)
os.makedirs("images", exist_ok=True)

# Servir imagens estaticamente
app.mount("/images", StaticFiles(directory="images"), name="images")

# Inicializar banco de dados (cria tabelas se não existirem)
init_db()


@app.get("/")
async def root():
    return {"message": "Sistema de Análise de PDFs API"}


@app.get("/health")
async def health():
    return {"status": "ok"}

