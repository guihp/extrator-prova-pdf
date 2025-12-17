from app.tasks import celery_app
from app.services.pdf_extractor import pdf_extractor
from app.services.ai_analyzer import ai_analyzer
from app.services.db_service import db_service
from app.services.image_processor import image_processor
from app.services.ocr_service import ocr_service
from app.services.image_deduplicator import image_deduplicator
from app.services.question_extractor import question_extractor
import os
import traceback
from typing import Dict


@celery_app.task(bind=True)
def process_pdf_task(self, prova_id: int, pdf_path: str):
    """Tarefa Celery para processar PDF completo"""
    from datetime import datetime
    
    task_id = self.request.id
    log_messages = []
    
    def log_detalhado(mensagem: str, progresso: int = None):
        """Função auxiliar para log detalhado"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {mensagem}"
        print(log_msg)
        log_messages.append(log_msg)
        
        # Atualizar etapa no banco
        etapa_completa = "\n".join(log_messages[-10:])  # Últimas 10 mensagens
        prova_atual = db_service.get_prova(prova_id)
        status_atual = prova_atual["status"] if prova_atual else "processando"
        db_service.update_prova_status(
            prova_id, 
            status_atual,
            etapa=etapa_completa,
            progresso=progresso
        )
    
    try:
        
        # Verificar se a tarefa foi cancelada (será verificado periodicamente)
        
        # Atualizar status inicial
        db_service.update_prova_status(prova_id, "extraindo", etapa="Iniciando processamento...", progresso=5)
        log_detalhado(f"🚀 Iniciando processamento da prova {prova_id} (Task ID: {task_id})", 5)
        
        # 1. Extrair texto do OCR das imagens (se necessário)
        log_detalhado("🔍 [ETAPA 1/9] Extraindo texto de imagens com OCR...", 10)
        ocr_text_by_page = {}
        try:
            ocr_text_by_page = ocr_service.extract_text_from_pdf_images(pdf_path)
            log_detalhado(f"✅ OCR concluído: {len(ocr_text_by_page)} páginas processadas", 15)
        except Exception as e:
            log_detalhado(f"⚠️ Erro no OCR (continuando sem OCR): {e}", 15)
        
        # 2. Extrair conteúdo do PDF (texto + imagens)
        log_detalhado("📄 [ETAPA 2/9] Extraindo conteúdo do PDF (texto + imagens)...", 20)
        content = pdf_extractor.extract_full_content(pdf_path, ocr_text_by_page)
        log_detalhado(f"✅ PDF extraído: {content['total_pages']} páginas, {len(content['images'])} imagens encontradas", 25)
        
        # 3. Extrair questões usando múltiplas estratégias
        db_service.update_prova_status(prova_id, "analisando", etapa="Extraindo questões...", progresso=30)
        log_detalhado("🔍 [ETAPA 3/9] Extraindo questões com múltiplas estratégias...", 30)
        
        questoes_from_methods = []
        
        # Estratégia 1: Processamento por página com regex
        log_detalhado("📝 [3.1] Estratégia 1: Regex por página...", 32)
        questoes_regex = question_extractor.extract_questoes_by_page(
            content["pages_text"],
            ocr_text_by_page
        )
        questoes_from_methods.append(questoes_regex)
        log_detalhado(f"   ✅ Regex: {len(questoes_regex)} questões encontradas", 35)
        
        # Estratégia 2: IA por chunks de páginas
        log_detalhado("🤖 [3.2] Estratégia 2: IA por chunks (Gemini/ChatGPT)...", 38)
        try:
            questoes_ai = question_extractor.extract_with_ai_by_page(
                content["pages_text"],
                ocr_text_by_page
            )
            questoes_from_methods.append(questoes_ai)
            log_detalhado(f"   ✅ IA: {len(questoes_ai)} questões encontradas", 42)
        except Exception as e:
            log_detalhado(f"   ⚠️ Erro na extração por IA: {e}", 42)
        
        # Estratégia 3: ChatGPT no texto completo (fallback)
        log_detalhado("🤖 [3.3] Estratégia 3: ChatGPT texto completo...", 45)
        try:
            questoes_chatgpt = ai_analyzer.extract_questoes_with_chatgpt(content["full_text"])
            questoes_from_methods.append(questoes_chatgpt)
            log_detalhado(f"   ✅ ChatGPT: {len(questoes_chatgpt)} questões encontradas", 48)
        except Exception as e:
            log_detalhado(f"   ⚠️ Erro no ChatGPT: {e}", 48)
        
        # Mesclar e deduplicar resultados de todas as estratégias
        log_detalhado("🔄 Mesclando e deduplicando resultados...", 50)
        questoes_raw = question_extractor.merge_and_deduplicate_questoes(questoes_from_methods)
        log_detalhado(f"✅ Total: {len(questoes_raw)} questões únicas após mesclagem", 52)
        
        # 4. Validação e refinamento com ChatGPT
        log_detalhado("✨ [ETAPA 4/9] Validando e refinando questões com ChatGPT...", 55)
        if questoes_raw:
            try:
                questoes_validadas = ai_analyzer.validate_with_chatgpt(
                    questoes_raw,
                    content["full_text"]
                )
                log_detalhado(f"✅ Validação concluída: {len(questoes_validadas)} questões validadas", 58)
            except Exception as e:
                log_detalhado(f"⚠️ Erro na validação: {e}", 58)
                questoes_validadas = questoes_raw
        else:
            log_detalhado("⚠️ Nenhuma questão encontrada após todas as estratégias!", 58)
            questoes_validadas = []
        
        # 5. Criar questões no banco
        log_detalhado(f"💾 [ETAPA 5/9] Salvando {len(questoes_validadas)} questões no banco...", 60)
        questoes_criadas = []
        total_questoes = len(questoes_validadas)
        for ordem, questao in enumerate(questoes_validadas, start=1):
            # Verificar se foi cancelado (verificação periódica)
            
            progresso_questao = 60 + int((ordem / total_questoes) * 5) if total_questoes > 0 else 60
            # Limpar e corrigir texto usando o serviço de limpeza
            from app.services.text_cleaner import text_cleaner
            texto_limpo = text_cleaner.clean_text(questao.get("texto", ""))
            
            try:
                questao_db = db_service.create_questao(
                    prova_id=prova_id,
                    numero=questao.get("numero", ordem),
                    texto=texto_limpo,
                    ordem=ordem
                )
                if questao_db:
                    questoes_criadas.append(questao_db)
                    if ordem % 10 == 0 or ordem == total_questoes:
                        log_detalhado(f"   💾 Questão {ordem}/{total_questoes} salva", progresso_questao)
            except Exception as e:
                log_detalhado(f"⚠️ Erro ao salvar questão {questao.get('numero', ordem)}: {e}", progresso_questao)
                continue
        
        log_detalhado(f"✅ {len(questoes_criadas)} questões salvas no banco", 65)
        
        # 6. Filtrar imagens duplicadas
        log_detalhado(f"🖼️ [ETAPA 6/9] Filtrando imagens duplicadas ({len(content['images'])} imagens totais)...", 70)
        db_service.update_prova_status(prova_id, "filtrando_imagens", etapa="Filtrando imagens duplicadas...", progresso=70)
        images_filtered = image_deduplicator.filter_duplicate_images(
            content["images"],
            content["pages_text"]
        )
        log_detalhado(f"✅ {len(images_filtered)} imagens únicas após filtro (removidas {len(content['images']) - len(images_filtered)} duplicadas)", 75)
        
        # 7. Mapear imagens às questões
        log_detalhado("🔗 [ETAPA 7/9] Mapeando imagens às questões com IA...", 78)
        db_service.update_prova_status(prova_id, "mapeando_imagens", etapa="Mapeando imagens às questões...", progresso=78)
        images_mapped = ai_analyzer.map_images_to_questoes(
            questoes_criadas,
            images_filtered,
            content["pages_text"]
        )
        log_detalhado(f"✅ {len(images_mapped)} imagens mapeadas para questões", 80)
        
        # 8. Processar e salvar imagens
        log_detalhado(f"💾 [ETAPA 8/9] Salvando {len(images_mapped)} imagens...", 82)
        db_service.update_prova_status(prova_id, "salvando_imagens", etapa=f"Salvando {len(images_mapped)} imagens...", progresso=82)
        total_imagens = len(images_mapped)
        for img_index, img_data in enumerate(images_mapped):
            # Verificar se foi cancelado (verificação periódica)
            
            progresso_imagem = 82 + int((img_index / total_imagens) * 15) if total_imagens > 0 else 82
            if img_index % 5 == 0 or img_index == total_imagens - 1:
                log_detalhado(f"   💾 Imagem {img_index + 1}/{total_imagens} processada", progresso_imagem)
            # Processar imagem
            processed_image = image_processor.process_image(
                img_data["image_bytes"],
                img_data.get("ext", "PNG")
            )
            
            # Gerar nome do arquivo
            filename = f"prova_{prova_id}/imagem_{img_data['page']}_{img_index}.png"
            
            # Salvar imagem localmente
            image_url = db_service.save_image_file(
                processed_image,
                filename
            )
            
            # Criar registro no banco
            questao_id = img_data.get("questao_id")
            hash_imagem = img_data.get("md5_hash")
            perceptual_hash = img_data.get("perceptual_hash")
            
            db_service.create_imagem(
                prova_id=prova_id,
                questao_id=questao_id,
                caminho_arquivo=image_url,
                posicao_pagina=img_data["page"],
                hash_imagem=hash_imagem,
                perceptual_hash=perceptual_hash
            )
        
        # 9. Finalizar
        log_detalhado("🎉 [ETAPA 9/9] Processamento concluído com sucesso!", 100)
        db_service.update_prova_status(
            prova_id, 
            "concluido", 
            etapa=f"✅ Processamento concluído!\n{len(questoes_criadas)} questões extraídas\n{len(images_mapped)} imagens processadas",
            progresso=100
        )
        
        # Limpar arquivo temporário
        if os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
                log_detalhado("🗑️ Arquivo temporário removido", 100)
            except Exception as e:
                log_detalhado(f"⚠️ Erro ao remover arquivo temporário: {e}", 100)
        
        return {
            "status": "success",
            "prova_id": prova_id,
            "questoes_count": len(questoes_criadas),
            "imagens_count": len(images_mapped)
        }
    
    except Exception as e:
        # Log detalhado do erro
        error_trace = traceback.format_exc()
        error_msg = f"❌ ERRO CRÍTICO no processamento da prova {prova_id}:\n"
        error_msg += f"   Tipo: {type(e).__name__}\n"
        error_msg += f"   Mensagem: {str(e)}\n"
        error_msg += f"   Traceback:\n{error_trace}"
        
        print(error_msg)
        log_messages.append(error_msg)
        
        # Atualizar status de erro com detalhes
        try:
            etapa_erro = "\n".join(log_messages[-15:])  # Últimas 15 mensagens incluindo erro
            db_service.update_prova_status(
                prova_id, 
                "erro",
                etapa=etapa_erro,
                progresso=0
            )
        except Exception as db_error:
            print(f"⚠️ Erro ao atualizar status no banco: {db_error}")
        
        # Limpar arquivo em caso de erro
        if os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except:
                pass
        
        # Re-raise para que o Celery registre o erro
        raise e

