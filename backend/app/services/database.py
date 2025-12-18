from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, BigInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from app.config import settings
from typing import Optional

Base = declarative_base()


class Prova(Base):
    __tablename__ = "provas"
    
    id = Column(BigInteger, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    arquivo_original = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="processando")
    etapa = Column(Text, nullable=True)  # Etapa atual do processamento (logs detalhados)
    progresso = Column(Integer, nullable=True, default=0)  # Progresso de 0 a 100
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    questoes = relationship("Questao", back_populates="prova", cascade="all, delete-orphan")
    imagens = relationship("Imagem", back_populates="prova", cascade="all, delete-orphan")


class Questao(Base):
    __tablename__ = "questoes"
    
    id = Column(BigInteger, primary_key=True, index=True)
    prova_id = Column(BigInteger, ForeignKey("provas.id", ondelete="CASCADE"), nullable=False)
    numero = Column(Integer, nullable=False)
    texto = Column(Text, nullable=False)
    ordem = Column(Integer, nullable=False)
    texto_formatado = Column(Text, nullable=False, default="")
    formatado = Column(Boolean, nullable=False, default=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    prova = relationship("Prova", back_populates="questoes")
    imagens = relationship("Imagem", back_populates="questao")


class Imagem(Base):
    __tablename__ = "imagens"
    
    id = Column(BigInteger, primary_key=True, index=True)
    prova_id = Column(BigInteger, ForeignKey("provas.id", ondelete="CASCADE"), nullable=False)
    questao_id = Column(BigInteger, ForeignKey("questoes.id", ondelete="SET NULL"), nullable=True)
    caminho_arquivo = Column(Text, nullable=False)
    posicao_pagina = Column(Integer, nullable=False)
    hash_imagem = Column(String(64), nullable=True)  # MD5 hash
    perceptual_hash = Column(String(64), nullable=True)  # Perceptual hash (pode ter até 64 caracteres)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    prova = relationship("Prova", back_populates="imagens")
    questao = relationship("Questao", back_populates="imagens")


# Criar engine e session
engine = create_engine(settings.get_postgres_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Retorna uma sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Cria as tabelas no banco de dados"""
    Base.metadata.create_all(bind=engine)

