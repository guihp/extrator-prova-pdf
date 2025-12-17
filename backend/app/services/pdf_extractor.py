import pdfplumber
import fitz  # PyMuPDF
from PIL import Image
from typing import List, Dict, Tuple
import io
import re


class PDFExtractor:
    def __init__(self):
        # Múltiplos padrões para diferentes formatos de questões
        self.questao_patterns = [
            re.compile(r'^\s*(\d+)[\.\)]\s+', re.MULTILINE),  # 1. ou 1)
            re.compile(r'^\s*Questão\s+(\d+)[\.\):]\s*', re.MULTILINE | re.IGNORECASE),  # Questão 1. ou Questão 1:
            re.compile(r'^\s*Q\.?\s*(\d+)[\.\):]\s*', re.MULTILINE | re.IGNORECASE),  # Q.1 ou Q1:
            re.compile(r'^\s*(\d+)\s*[–\-]\s+', re.MULTILINE),  # 1 - ou 1 –
        ]
        
        # Padrão para alternativas
        self.alternativa_pattern = re.compile(r'^\s*([A-E])[\.\)]\s+', re.MULTILINE)
    
    def extract_text_by_page(self, pdf_path: str) -> List[Dict[str, any]]:
        """Extrai texto de cada página do PDF"""
        pages_text = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                pages_text.append({
                    "page": page_num,
                    "text": text,
                    "bbox": page.bbox
                })
        
        return pages_text
    
    def extract_images(self, pdf_path: str) -> List[Dict[str, any]]:
        """Extrai todas as imagens do PDF com suas posições"""
        images = []
        doc = None
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        # Obter posição da imagem na página
                        image_rects = page.get_image_rects(xref)
                        bbox = None
                        if image_rects:
                            bbox = {
                                "x0": image_rects[0].x0,
                                "y0": image_rects[0].y0,
                                "x1": image_rects[0].x1,
                                "y1": image_rects[0].y1
                            }
                        
                        images.append({
                            "page": page_num + 1,
                            "image_bytes": image_bytes,
                            "ext": image_ext,
                            "bbox": bbox,
                            "index": img_index
                        })
                    except Exception as e:
                        print(f"Erro ao extrair imagem {img_index} da página {page_num + 1}: {e}")
                        continue
        finally:
            if doc:
                doc.close()
        return images
    
    def identify_questoes_numbers(self, text: str) -> List[Tuple[int, int, str]]:
        """Identifica números de questões no texto usando múltiplos padrões"""
        all_matches = []
        
        # Coletar matches de todos os padrões
        for pattern in self.questao_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                numero = int(match.group(1))
                all_matches.append((match.start(), numero, match))
        
        # Ordenar por posição
        all_matches.sort(key=lambda x: x[0])
        
        # Remover duplicatas (mesma posição ou muito próximas)
        unique_matches = []
        last_pos = -1
        for pos, numero, match in all_matches:
            if pos - last_pos > 10:  # Pelo menos 10 caracteres de diferença
                unique_matches.append((pos, numero, match))
                last_pos = pos
        
        # Extrair texto de cada questão
        questoes = []
        for i, (start_pos, numero, match) in enumerate(unique_matches):
            # Determinar fim do texto da questão (até próxima questão ou fim)
            if i + 1 < len(unique_matches):
                end_pos = unique_matches[i + 1][0]
            else:
                end_pos = len(text)
            
            questao_texto = text[start_pos:end_pos].strip()
            
            # Validar que a questão tem conteúdo suficiente
            if len(questao_texto) > 20:  # Pelo menos 20 caracteres
                questoes.append((numero, start_pos, questao_texto))
        
        return questoes
    
    def extract_full_content(self, pdf_path: str, ocr_text_by_page: Dict[str, str] = None) -> Dict[str, any]:
        """Extrai todo o conteúdo do PDF: texto e imagens"""
        pages_text = self.extract_text_by_page(pdf_path)
        images = self.extract_images(pdf_path)
        
        # Combinar texto do PDF com texto do OCR
        full_text_parts = []
        for page in pages_text:
            page_text = page["text"]
            page_num = str(page["page"])
            
            # Adicionar texto do OCR se disponível
            if ocr_text_by_page and page_num in ocr_text_by_page:
                ocr_text = ocr_text_by_page[page_num]
                if ocr_text:
                    page_text = f"{page_text}\n\n[OCR]\n{ocr_text}"
            
            full_text_parts.append(page_text)
        
        full_text = "\n\n".join(full_text_parts)
        
        return {
            "full_text": full_text,
            "pages_text": pages_text,
            "images": images,
            "total_pages": len(pages_text)
        }


pdf_extractor = PDFExtractor()

