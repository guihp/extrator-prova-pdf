from app.services.pdf_extractor import pdf_extractor
from app.services.ai_analyzer import ai_analyzer
from app.services.ocr_service import ocr_service
from typing import List, Dict
import re


class QuestionExtractor:
    """Serviço especializado para extração de questões com múltiplas estratégias"""
    
    def __init__(self):
        pass
    
    def extract_questoes_by_page(self, pages_text: List[Dict], ocr_text_by_page: Dict[str, str] = None) -> List[Dict]:
        """
        Extrai questões processando cada página individualmente
        Melhor para manter contexto e rastreamento de posição
        """
        all_questoes = []
        
        for page_info in pages_text:
            page_num = page_info.get("page", 1)
            page_text = page_info.get("text", "")
            
            # Adicionar texto do OCR se disponível
            if ocr_text_by_page and str(page_num) in ocr_text_by_page:
                ocr_text = ocr_text_by_page[str(page_num)]
                if ocr_text:
                    page_text = f"{page_text}\n\n[OCR]\n{ocr_text}"
            
            if not page_text.strip():
                continue
            
            # Tentar extrair questões da página usando regex
            questoes_regex = pdf_extractor.identify_questoes_numbers(page_text)
            
            for numero, pos_in_page, texto in questoes_regex:
                # Calcular posição global no documento
                # Soma posições das páginas anteriores
                global_offset = sum(
                    len(p.get("text", "")) + 2  # +2 para quebras de linha
                    for p in pages_text
                    if p.get("page", 0) < page_num
                )
                
                all_questoes.append({
                    "numero": numero,
                    "texto": texto,
                    "posicao_inicio": global_offset + pos_in_page,
                    "posicao_fim": global_offset + pos_in_page + len(texto),
                    "pagina": page_num
                })
        
        return all_questoes
    
    def extract_with_ai_by_page(self, pages_text: List[Dict], ocr_text_by_page: Dict[str, str] = None) -> List[Dict]:
        """
        Extrai questões usando IA, processando páginas em grupos menores
        para melhor contexto
        """
        all_questoes = []
        pages_per_chunk = 3  # Processar 3 páginas por vez
        
        for i in range(0, len(pages_text), pages_per_chunk):
            chunk_pages = pages_text[i:i + pages_per_chunk]
            chunk_text_parts = []
            
            for page_info in chunk_pages:
                page_num = page_info.get("page", 1)
                page_text = page_info.get("text", "")
                
                # Adicionar OCR se disponível
                if ocr_text_by_page and str(page_num) in ocr_text_by_page:
                    ocr_text = ocr_text_by_page[str(page_num)]
                    if ocr_text:
                        page_text = f"{page_text}\n\n[OCR]\n{ocr_text}"
                
                chunk_text_parts.append(f"[Página {page_num}]\n{page_text}")
            
            chunk_text = "\n\n".join(chunk_text_parts)
            
            # Tentar extrair com ChatGPT
            try:
                questoes_chunk = ai_analyzer.extract_questoes_with_chatgpt(chunk_text)
                all_questoes.extend(questoes_chunk)
            except Exception as e:
                print(f"Erro ao extrair questões do chunk {i//pages_per_chunk + 1}: {e}")
                # Fallback para regex
                questoes_regex = pdf_extractor.identify_questoes_numbers(chunk_text)
                for numero, pos, texto in questoes_regex:
                    all_questoes.append({
                        "numero": numero,
                        "texto": texto,
                        "posicao_inicio": pos,
                        "posicao_fim": pos + len(texto)
                    })
        
        return all_questoes
    
    def merge_and_deduplicate_questoes(self, questoes_list: List[List[Dict]]) -> List[Dict]:
        """
        Mescla múltiplas listas de questões e remove duplicatas
        Mantém a questão com mais texto quando há duplicatas
        """
        merged = {}
        
        for questoes in questoes_list:
            for questao in questoes:
                numero = questao.get("numero")
                if not numero:
                    continue
                
                if numero not in merged:
                    merged[numero] = questao
                else:
                    # Se já existe, manter a que tem mais texto
                    existing = merged[numero]
                    if len(questao.get("texto", "")) > len(existing.get("texto", "")):
                        merged[numero] = questao
        
        # Ordenar por número
        return sorted(merged.values(), key=lambda x: x.get("numero", 0))


question_extractor = QuestionExtractor()




