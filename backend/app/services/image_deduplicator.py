from app.services.image_processor import image_processor
from typing import List, Dict, Set


class ImageDeduplicator:
    def __init__(self):
        self.processed_hashes: Set[str] = set()
        self.processed_perceptual_hashes: List[Dict] = []
    
    def filter_duplicate_images(self, images: List[Dict], pages_info: List[Dict] = None) -> List[Dict]:
        """
        Filtra imagens duplicadas usando múltiplas estratégias:
        1. Hash MD5 (duplicatas exatas)
        2. Perceptual hash (similaridade visual)
        3. Tamanho mínimo
        4. Posição (cabeçalho/rodapé)
        """
        filtered_images = []
        page_heights = {}
        
        # Mapear alturas das páginas
        if pages_info:
            for page_info in pages_info:
                page_num = page_info.get("page", 1)
                bbox = page_info.get("bbox")
                # bbox pode ser uma tupla (x0, y0, x1, y1) ou dict
                if bbox:
                    if isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
                        page_heights[page_num] = bbox[3] - bbox[1]  # y1 - y0
                    elif isinstance(bbox, dict) and "y1" in bbox and "y0" in bbox:
                        page_heights[page_num] = bbox["y1"] - bbox["y0"]
        
        for img_data in images:
            image_bytes = img_data.get("image_bytes")
            if not image_bytes:
                continue
            
            # 1. Filtrar imagens muito pequenas
            if image_processor.is_image_too_small(image_bytes):
                print(f"⚠️ Imagem {img_data.get('index', '?')} da página {img_data.get('page', '?')} muito pequena, ignorando")
                continue
            
            # 2. Filtrar imagens em cabeçalho/rodapé
            bbox = img_data.get("bbox")
            page_num = img_data.get("page", 1)
            page_height = page_heights.get(page_num, 800)
            
            if image_processor.is_header_footer_image(bbox, page_height):
                print(f"⚠️ Imagem {img_data.get('index', '?')} da página {page_num} está em cabeçalho/rodapé, ignorando")
                continue
            
            # 3. Verificar hash MD5 (duplicatas exatas)
            md5_hash = image_processor.calculate_hash_md5(image_bytes)
            if md5_hash in self.processed_hashes:
                print(f"⚠️ Imagem {img_data.get('index', '?')} da página {page_num} é duplicata exata (MD5), ignorando")
                continue
            
            # 4. Verificar similaridade visual (perceptual hash)
            perceptual_hash = image_processor.calculate_perceptual_hash(image_bytes)
            if perceptual_hash:
                is_duplicate = False
                for existing in self.processed_perceptual_hashes:
                    existing_hash = existing.get("perceptual_hash")
                    if existing_hash:
                        similarity = image_processor.calculate_similarity(perceptual_hash, existing_hash)
                        if similarity >= image_processor.similarity_threshold:
                            print(f"⚠️ Imagem {img_data.get('index', '?')} da página {page_num} é similar ({similarity:.1f}%) à imagem da página {existing.get('page', '?')}, ignorando")
                            is_duplicate = True
                            break
                
                if is_duplicate:
                    continue
                
                # Adicionar aos processados
                self.processed_perceptual_hashes.append({
                    "perceptual_hash": perceptual_hash,
                    "page": page_num,
                    "index": img_data.get("index", 0)
                })
            
            # 5. Adicionar hash MD5 aos processados
            self.processed_hashes.add(md5_hash)
            
            # 6. Adicionar metadados de hash à imagem
            img_data["md5_hash"] = md5_hash
            img_data["perceptual_hash"] = perceptual_hash
            
            filtered_images.append(img_data)
        
        print(f"✅ Filtradas {len(images) - len(filtered_images)} imagens duplicadas/irrelevantes de {len(images)} totais")
        return filtered_images


image_deduplicator = ImageDeduplicator()

