import pytesseract
from PIL import Image
import io
from typing import List, Dict
import fitz


class OCRService:
    def __init__(self):
        # Configurar caminho do tesseract se necessário
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'  # macOS
        pass
    
    def extract_text_from_image_bytes(self, image_bytes: bytes) -> str:
        """Extrai texto de uma imagem usando OCR"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Converter para RGB se necessário
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # OCR com configuração otimizada para português
            text = pytesseract.image_to_string(
                image,
                lang='por+eng',  # Português e Inglês
                config='--psm 6'  # Assume um único bloco de texto uniforme
            )
            return text.strip()
        except Exception as e:
            print(f"Erro no OCR: {e}")
            return ""
    
    def extract_text_from_pdf_images(self, pdf_path: str) -> Dict[str, str]:
        """Extrai texto de todas as imagens do PDF usando OCR"""
        ocr_text_by_page = {}
        doc = None
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                page_ocr_text = []
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        
                        # Extrair texto da imagem
                        ocr_text = self.extract_text_from_image_bytes(image_bytes)
                        if ocr_text:
                            page_ocr_text.append(ocr_text)
                    except Exception as e:
                        print(f"Erro ao fazer OCR da imagem {img_index} da página {page_num + 1}: {e}")
                        continue
                
                if page_ocr_text:
                    ocr_text_by_page[str(page_num + 1)] = "\n".join(page_ocr_text)
        
        finally:
            if doc:
                doc.close()
        
        return ocr_text_by_page


ocr_service = OCRService()




