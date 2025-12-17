"""
Serviço para limpeza e correção de texto extraído de PDFs
Corrige problemas comuns de OCR e encoding
"""
import re
import unicodedata
from typing import Optional


class TextCleaner:
    """Serviço para limpar e corrigir textos extraídos de PDFs"""
    
    # Mapeamento de erros comuns do OCR
    OCR_CORRECTIONS = {
        # Números dentro de palavras (problema comum do OCR)
        r'tambe(\d+)m': 'também',
        r'podere(\d+)': 'poderá',
        r'mate(\d+)ria': 'matéria',
        r'Justie(\d+)a': 'Justiça',
        r'Antf(\d+)nio': 'Antônio',
        r'importunae(\d+)e(\d+)o': 'importunação',
        r'ne(\d+)o': 'não',
        r'Superior': 'Superior',  # Manter correto
        r'judicial': 'judicial',  # Manter correto
        r'entendimento': 'entendimento',  # Manter correto
        
        # Outros erros comuns do OCR
        r'(\d+)': '',  # Remove números soltos no meio de palavras (cuidado!)
        r'(\w)(\d+)(\w)': r'\1\3',  # Remove números entre letras
        
        # Caracteres especiais mal interpretados
        r'ã': 'ã',
        r'á': 'á',
        r'à': 'à',
        r'â': 'â',
        r'é': 'é',
        r'ê': 'ê',
        r'í': 'í',
        r'ó': 'ó',
        r'ô': 'ô',
        r'õ': 'õ',
        r'ú': 'ú',
        r'ü': 'ü',
        r'ç': 'ç',
        r'Ã': 'Ã',
        r'Á': 'Á',
        r'À': 'À',
        r'Â': 'Â',
        r'É': 'É',
        r'Ê': 'Ê',
        r'Í': 'Í',
        r'Ó': 'Ó',
        r'Ô': 'Ô',
        r'Õ': 'Õ',
        r'Ú': 'Ú',
        r'Ü': 'Ü',
        r'Ç': 'Ç',
    }
    
    # Padrões específicos para correção
    SPECIFIC_CORRECTIONS = {
        'tambe9m': 'também',
        'tambe8m': 'também',
        'tambe7m': 'também',
        'tambe6m': 'também',
        'tambe5m': 'também',
        'tambe4m': 'também',
        'tambe3m': 'também',
        'tambe2m': 'também',
        'tambe1m': 'também',
        'tambe0m': 'também',
        'podere1': 'poderá',
        'podere2': 'poderá',
        'podere3': 'poderá',
        'podere4': 'poderá',
        'podere5': 'poderá',
        'podere6': 'poderá',
        'podere7': 'poderá',
        'podere8': 'poderá',
        'podere9': 'poderá',
        'podere0': 'poderá',
        'mate9ria': 'matéria',
        'mate8ria': 'matéria',
        'mate7ria': 'matéria',
        'mate6ria': 'matéria',
        'mate5ria': 'matéria',
        'mate4ria': 'matéria',
        'mate3ria': 'matéria',
        'mate2ria': 'matéria',
        'mate1ria': 'matéria',
        'mate0ria': 'matéria',
        'Justie7a': 'Justiça',
        'Justie8a': 'Justiça',
        'Justie9a': 'Justiça',
        'Justie6a': 'Justiça',
        'Justie5a': 'Justiça',
        'Justie4a': 'Justiça',
        'Justie3a': 'Justiça',
        'Justie2a': 'Justiça',
        'Justie1a': 'Justiça',
        'Justie0a': 'Justiça',
        'Antf4nio': 'Antônio',
        'Antf5nio': 'Antônio',
        'Antf6nio': 'Antônio',
        'Antf7nio': 'Antônio',
        'Antf8nio': 'Antônio',
        'Antf9nio': 'Antônio',
        'Antf3nio': 'Antônio',
        'Antf2nio': 'Antônio',
        'Antf1nio': 'Antônio',
        'Antf0nio': 'Antônio',
        'importunae7e3o': 'importunação',
        'importunae8e4o': 'importunação',
        'importunae9e5o': 'importunação',
        'importunae6e2o': 'importunação',
        'ne3o': 'não',
        'ne4o': 'não',
        'ne5o': 'não',
        'ne6o': 'não',
        'ne7o': 'não',
        'ne8o': 'não',
        'ne9o': 'não',
        'ne2o': 'não',
        'ne1o': 'não',
        'ne0o': 'não',
    }
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Limpa e corrige texto extraído de PDF/OCR
        
        Args:
            text: Texto a ser limpo
            
        Returns:
            Texto limpo e corrigido
        """
        if not text:
            return ""
        
        # 1. Normalizar encoding (NFD -> NFC)
        try:
            text = unicodedata.normalize('NFC', text)
        except:
            pass
        
        # 2. Remover caracteres NUL e outros problemáticos
        text = text.replace('\x00', '').replace('\r', ' ')
        
        # 3. Remover caracteres de controle (exceto \n e \t)
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        # 4. Aplicar correções específicas (mais precisas)
        for wrong, correct in TextCleaner.SPECIFIC_CORRECTIONS.items():
            text = text.replace(wrong, correct)
            # Também tentar com variações de maiúsculas
            text = text.replace(wrong.capitalize(), correct.capitalize())
            text = text.replace(wrong.upper(), correct.upper())
        
        # 5. Corrigir padrões específicos primeiro
        text = re.sub(r'\be0\b', 'ao', text, flags=re.IGNORECASE)  # "e0" isolado -> "ao"
        text = re.sub(r'(\w+)e0(\s)', r'\1ao\2', text, flags=re.IGNORECASE)  # "e0 " -> "ao "
        text = re.sub(r'(\w+)e0(\w)', r'\1ao\2', text, flags=re.IGNORECASE)  # "e0" no meio -> "ao"
        
        # 6. Corrigir padrões comuns de números no meio de palavras
        # Padrão: letra + número + letra (ex: "tambe9m" -> "também")
        patterns_to_fix = [
            (r'(\w{2,})9(\w{2,})', r'\1m\2'),  # "tambe9m" -> "também"
            (r'(\w{2,})7(\w{2,})', r'\1ç\2'),  # "Justie7a" -> "Justiça"
            (r'(\w{2,})4(\w{2,})', r'\1ã\2'),  # "Antf4nio" -> "Antônio"
            (r'(\w{2,})3(\w{2,})', r'\1ã\2'),  # "ne3o" -> "não"
            (r'(\w{2,})1(\w{2,})', r'\1á\2'),  # "podere1" -> "poderá"
        ]
        
        for pattern, replacement in patterns_to_fix:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # 7. Normalizar espaços múltiplos
        text = re.sub(r'\s+', ' ', text)
        
        # 8. Limpar espaços no início e fim
        text = text.strip()
        
        # 9. Corrigir quebras de linha duplas
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    @staticmethod
    def clean_and_validate(text: str) -> Optional[str]:
        """
        Limpa texto e valida se está válido
        
        Returns:
            Texto limpo ou None se inválido
        """
        if not text:
            return None
        
        cleaned = TextCleaner.clean_text(text)
        
        # Validar se o texto ainda tem conteúdo válido
        if len(cleaned.strip()) < 3:
            return None
        
        return cleaned


text_cleaner = TextCleaner()

