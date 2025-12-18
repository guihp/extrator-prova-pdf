from sqlalchemy.orm import Session
from app.services.database import SessionLocal, Prova, Questao, Imagem
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
from app.config import settings


class DatabaseService:
    def __init__(self):
        pass
    
    def _get_db(self) -> Session:
        """Retorna uma nova sessão do banco"""
        return SessionLocal()
    
    def create_prova(self, nome: str, arquivo_original: str) -> Dict[str, Any]:
        """Cria uma nova prova no banco"""
        db = self._get_db()
        try:
            prova = Prova(
                nome=nome,
                arquivo_original=arquivo_original,
                status="processando"
            )
            db.add(prova)
            db.commit()
            db.refresh(prova)
            return self._prova_to_dict(prova)
        finally:
            db.close()
    
    def update_prova_status(self, prova_id: int, status: str, etapa: Optional[str] = None, progresso: Optional[int] = None):
        """Atualiza o status de uma prova com informações detalhadas"""
        db = self._get_db()
        try:
            prova = db.query(Prova).filter(Prova.id == prova_id).first()
            if prova:
                prova.status = status
                if etapa is not None:
                    prova.etapa = etapa
                if progresso is not None:
                    prova.progresso = progresso
                db.commit()
        finally:
            db.close()
    
    def create_questao(self, prova_id: int, numero: int, texto: str, ordem: int) -> Dict[str, Any]:
        """Cria uma questão"""
        db = self._get_db()
        try:
            questao = Questao(
                prova_id=prova_id,
                numero=numero,
                texto=texto,
                ordem=ordem
            )
            db.add(questao)
            db.commit()
            db.refresh(questao)
            return self._questao_to_dict(questao)
        finally:
            db.close()
    
    def create_imagem(self, prova_id: int, questao_id: Optional[int], 
                     caminho_arquivo: str, posicao_pagina: int,
                     hash_imagem: Optional[str] = None,
                     perceptual_hash: Optional[str] = None) -> Dict[str, Any]:
        """Cria registro de imagem"""
        db = self._get_db()
        try:
            imagem = Imagem(
                prova_id=prova_id,
                questao_id=questao_id,
                caminho_arquivo=caminho_arquivo,
                posicao_pagina=posicao_pagina,
                hash_imagem=hash_imagem,
                perceptual_hash=perceptual_hash
            )
            db.add(imagem)
            db.commit()
            db.refresh(imagem)
            return self._imagem_to_dict(imagem)
        finally:
            db.close()
    
    def save_image_file(self, image_bytes: bytes, filename: str) -> str:
        """Salva imagem localmente e retorna URL"""
        # Criar diretório se não existir
        images_dir = os.path.join(settings.images_dir, os.path.dirname(filename))
        os.makedirs(images_dir, exist_ok=True)
        
        # Salvar arquivo
        file_path = os.path.join(settings.images_dir, filename)
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        
        # Retornar URL relativa (será servida pelo FastAPI)
        return f"{settings.base_url}/images/{filename}"
    
    def get_prova(self, prova_id: int) -> Optional[Dict[str, Any]]:
        """Busca uma prova por ID"""
        db = self._get_db()
        try:
            prova = db.query(Prova).filter(Prova.id == prova_id).first()
            return self._prova_to_dict(prova) if prova else None
        finally:
            db.close()
    
    def get_questoes_by_prova(self, prova_id: int) -> List[Dict[str, Any]]:
        """Busca todas as questões de uma prova"""
        db = self._get_db()
        try:
            questoes = db.query(Questao).filter(
                Questao.prova_id == prova_id
            ).order_by(Questao.ordem).all()
            return [self._questao_to_dict(q) for q in questoes]
        finally:
            db.close()
    
    def get_questao(self, questao_id: int) -> Optional[Dict[str, Any]]:
        """Busca uma questão específica por ID"""
        db = self._get_db()
        try:
            questao = db.query(Questao).filter(Questao.id == questao_id).first()
            return self._questao_to_dict(questao) if questao else None
        finally:
            db.close()
    
    def get_imagens_by_prova(self, prova_id: int) -> List[Dict[str, Any]]:
        """Busca todas as imagens de uma prova"""
        db = self._get_db()
        try:
            imagens = db.query(Imagem).filter(
                Imagem.prova_id == prova_id
            ).order_by(Imagem.posicao_pagina).all()
            return [self._imagem_to_dict(img) for img in imagens]
        finally:
            db.close()
    
    def list_provas(self) -> List[Dict[str, Any]]:
        """Lista todas as provas"""
        db = self._get_db()
        try:
            provas = db.query(Prova).order_by(Prova.criado_em.desc()).all()
            return [self._prova_to_dict(p) for p in provas]
        finally:
            db.close()
    
    def _prova_to_dict(self, prova: Prova) -> Dict[str, Any]:
        """Converte modelo Prova para dict"""
        # Usar getattr com None como padrão para evitar erros se as colunas não existirem
        return {
            "id": prova.id,
            "nome": prova.nome,
            "arquivo_original": prova.arquivo_original,
            "status": prova.status,
            "etapa": getattr(prova, 'etapa', None),
            "progresso": getattr(prova, 'progresso', None),
            "criado_em": prova.criado_em.isoformat() if prova.criado_em else None,
            "atualizado_em": prova.atualizado_em.isoformat() if prova.atualizado_em else None
        }
    
    def _questao_to_dict(self, questao: Questao) -> Dict[str, Any]:
        """Converte modelo Questao para dict"""
        return {
            "id": questao.id,
            "prova_id": questao.prova_id,
            "numero": questao.numero,
            "texto": questao.texto,
            "ordem": questao.ordem,
            "texto_formatado": getattr(questao, 'texto_formatado', None) or "",
            "formatado": getattr(questao, 'formatado', False),
            "criado_em": questao.criado_em.isoformat() if questao.criado_em else None
        }
    
    def _imagem_to_dict(self, imagem: Imagem) -> Dict[str, Any]:
        """Converte modelo Imagem para dict"""
        return {
            "id": imagem.id,
            "prova_id": imagem.prova_id,
            "questao_id": imagem.questao_id,
            "caminho_arquivo": imagem.caminho_arquivo,
            "posicao_pagina": imagem.posicao_pagina,
            "hash_imagem": imagem.hash_imagem,
            "perceptual_hash": imagem.perceptual_hash,
            "criado_em": imagem.criado_em.isoformat() if imagem.criado_em else None
        }
    
    def get_imagens_by_questao(self, questao_id: int) -> List[Dict[str, Any]]:
        """Busca todas as imagens de uma questão"""
        db = self._get_db()
        try:
            imagens = db.query(Imagem).filter(
                Imagem.questao_id == questao_id
            ).order_by(Imagem.posicao_pagina).all()
            return [self._imagem_to_dict(img) for img in imagens]
        finally:
            db.close()
    
    def get_questoes_formatadas(self) -> List[Dict[str, Any]]:
        """Busca todas as questões formatadas (formatado = True) com informações da prova"""
        db = self._get_db()
        try:
            questoes = db.query(Questao, Prova).join(
                Prova, Questao.prova_id == Prova.id
            ).filter(
                Questao.formatado == True
            ).order_by(Questao.criado_em.desc()).all()
            
            result = []
            for questao, prova in questoes:
                questao_dict = self._questao_to_dict(questao)
                questao_dict["prova_nome"] = prova.nome
                questao_dict["prova_id_display"] = prova.id
                result.append(questao_dict)
            
            return result
        finally:
            db.close()
    
    def get_questoes_nao_formatadas_count(self) -> int:
        """Retorna a quantidade de questões não formatadas"""
        db = self._get_db()
        try:
            count = db.query(Questao).filter(
                Questao.formatado == False
            ).count()
            return count
        finally:
            db.close()
    
# Instância global
db_service = DatabaseService()

