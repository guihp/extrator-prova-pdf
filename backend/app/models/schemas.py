from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProvaCreate(BaseModel):
    nome: str
    arquivo_original: str


class ProvaResponse(BaseModel):
    id: int
    nome: str
    arquivo_original: str
    status: str
    etapa: Optional[str] = None
    progresso: Optional[int] = None
    criado_em: datetime

    class Config:
        from_attributes = True


class QuestaoResponse(BaseModel):
    id: int
    prova_id: int
    numero: int
    texto: str
    ordem: int
    texto_formatado: Optional[str] = ""
    formatado: bool = False

    class Config:
        from_attributes = True


class QuestaoFormatadaResponse(BaseModel):
    id: int
    prova_id: int
    prova_id_display: Optional[int] = None
    prova_nome: Optional[str] = None
    numero: int
    texto: str
    ordem: int
    texto_formatado: Optional[str] = ""
    formatado: bool = False

    class Config:
        from_attributes = True


class ImagemResponse(BaseModel):
    id: int
    prova_id: int
    questao_id: Optional[int]
    caminho_arquivo: str
    posicao_pagina: int

    class Config:
        from_attributes = True


class ProvaCompletaResponse(BaseModel):
    prova: ProvaResponse
    questoes: List[QuestaoResponse]
    imagens: List[ImagemResponse]

