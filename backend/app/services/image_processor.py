from PIL import Image
import imagehash
import hashlib
from typing import List, Dict, Optional, Tuple
import io


class ImageProcessor:
    def __init__(self):
        self.supported_formats = ['PNG', 'JPEG', 'JPG']
        self.min_image_size = 50  # Tamanho mínimo em pixels
        self.similarity_threshold = 95  # Similaridade mínima para considerar duplicata (%)
    
    def process_image(self, image_bytes: bytes, format: str = 'PNG') -> bytes:
        """Processa e otimiza imagem"""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            
            # Converter para RGB se necessário
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Salvar como PNG
            output = io.BytesIO()
            img.save(output, format='PNG', optimize=True)
            return output.getvalue()
        except Exception as e:
            print(f"Erro ao processar imagem: {e}")
            return image_bytes
    
    def get_image_dimensions(self, image_bytes: bytes) -> Dict[str, int]:
        """Obtém dimensões da imagem"""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            return {"width": img.width, "height": img.height}
        except Exception as e:
            print(f"Erro ao obter dimensões: {e}")
            return {"width": 0, "height": 0}
    
    def calculate_hash_md5(self, image_bytes: bytes) -> str:
        """Calcula hash MD5 da imagem para detecção de duplicatas exatas"""
        return hashlib.md5(image_bytes).hexdigest()
    
    def calculate_perceptual_hash(self, image_bytes: bytes) -> Optional[str]:
        """Calcula perceptual hash (pHash) para detecção de similaridade visual"""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            # Converter para RGB se necessário
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calcular perceptual hash (hash_size=8 gera hash de 16 caracteres)
            phash = imagehash.phash(img, hash_size=8)
            hash_str = str(phash)
            # Garantir que não exceda 32 caracteres (limite do banco)
            return hash_str[:32] if len(hash_str) > 32 else hash_str
        except Exception as e:
            print(f"Erro ao calcular perceptual hash: {e}")
            return None
    
    def calculate_dhash(self, image_bytes: bytes) -> Optional[str]:
        """Calcula difference hash (dHash) para detecção de similaridade"""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            dhash = imagehash.dhash(img, hash_size=16)
            return str(dhash)
        except Exception as e:
            print(f"Erro ao calcular dHash: {e}")
            return None
    
    def calculate_similarity(self, hash1: str, hash2: str) -> float:
        """Calcula similaridade entre dois hashes (0-100%)"""
        try:
            h1 = imagehash.hex_to_hash(hash1)
            h2 = imagehash.hex_to_hash(hash2)
            # Distância de Hamming
            distance = h1 - h2
            # Converter para porcentagem de similaridade
            max_distance = len(hash1) * 4  # Aproximado para hash_size=16
            similarity = (1 - distance / max_distance) * 100
            return max(0, min(100, similarity))
        except Exception as e:
            print(f"Erro ao calcular similaridade: {e}")
            return 0.0
    
    def is_image_too_small(self, image_bytes: bytes) -> bool:
        """Verifica se a imagem é muito pequena (provavelmente ícone)"""
        try:
            dimensions = self.get_image_dimensions(image_bytes)
            return dimensions["width"] < self.min_image_size or dimensions["height"] < self.min_image_size
        except:
            return True
    
    def is_header_footer_image(self, bbox: Optional[Dict], page_height: float = 800) -> bool:
        """Verifica se a imagem está em posição de cabeçalho ou rodapé"""
        if not bbox:
            return False
        
        # Normalizar altura da página (assumir ~800px como padrão)
        y0_normalized = bbox.get("y0", 0) / page_height if page_height > 0 else 0
        y1_normalized = bbox.get("y1", 0) / page_height if page_height > 0 else 0
        
        # Cabeçalho: primeiros 15% da página
        # Rodapé: últimos 15% da página
        is_header = y1_normalized < 0.15
        is_footer = y0_normalized > 0.85
        
        return is_header or is_footer


image_processor = ImageProcessor()

