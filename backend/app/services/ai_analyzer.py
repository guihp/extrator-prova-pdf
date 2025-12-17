import google.generativeai as genai
from openai import OpenAI
from app.config import settings
from typing import List, Dict, Optional
import json
import re


class AIAnalyzer:
    def __init__(self):
        # Configurar Gemini (tentar modelos mais recentes primeiro)
        self.gemini_model = None
        self.gemini_model_name = None
        try:
            genai.configure(api_key=settings.gemini_api_key)
            # Tentar modelos mais recentes primeiro (ordem de preferência)
            # Gemini 2.0 é experimental, Gemini 1.5 Pro é mais estável e poderoso
            model_names = [
                'gemini-3.0-pro',        # Mais recente (se disponível)
                'gemini-2.5-pro',        # Versão 2.5 Pro (se disponível)
                'gemini-2.0-flash-exp',  # Mais recente experimental
                'gemini-1.5-pro',        # Mais poderoso e estável
                'gemini-1.5-flash',      # Mais rápido
                'gemini-1.0-pro',        # Fallback
                'gemini-pro'              # Último fallback
            ]
            for model_name in model_names:
                try:
                    # Testar se o modelo funciona criando o objeto
                    test_model = genai.GenerativeModel(model_name)
                    self.gemini_model = test_model
                    self.gemini_model_name = model_name
                    print(f"✅ Modelo Gemini configurado: {model_name}")
                    break
                except Exception as e:
                    print(f"⚠️ Modelo {model_name} não disponível: {e}")
                    continue
            
            if self.gemini_model is None:
                print("⚠️ Nenhum modelo Gemini disponível. Usando apenas ChatGPT.")
        except Exception as e:
            print(f"⚠️ Gemini não configurado: {e}. Usando apenas ChatGPT.")
        
        # Configurar OpenAI (sempre necessário)
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        
        # Modelos OpenAI disponíveis (ordem de preferência)
        # gpt-4o é o mais recente e melhor, gpt-4-turbo suporta response_format
        self.openai_models = [
            'gpt-4o',           # Mais recente e melhor (suporta response_format)
            'gpt-4-turbo',      # Versão turbo (suporta response_format)
            'gpt-4',            # Fallback (não suporta response_format)
            'gpt-3.5-turbo'     # Último fallback (suporta response_format)
        ]
        self.current_openai_model = None
        self.supports_json_mode = False
        self._detect_best_openai_model()
    
    def _detect_best_openai_model(self):
        """Detecta o melhor modelo OpenAI disponível que suporta JSON mode"""
        # Modelos que suportam response_format (JSON mode)
        json_mode_models = ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo']
        
        for model_name in self.openai_models:
            try:
                # Testar se o modelo está disponível fazendo uma chamada simples
                test_response = self.openai_client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                self.current_openai_model = model_name
                self.supports_json_mode = model_name in json_mode_models
                print(f"✅ Modelo OpenAI configurado: {model_name} (JSON mode: {'✅' if self.supports_json_mode else '❌'})")
                return
            except Exception as e:
                print(f"⚠️ Modelo {model_name} não disponível: {e}")
                continue
        
        # Fallback para gpt-4 se nenhum funcionar
        self.current_openai_model = 'gpt-4'
        self.supports_json_mode = False
        print(f"⚠️ Usando fallback: {self.current_openai_model}")
    
    def analyze_structure_with_gemini(self, text: str, images_info: List[Dict]) -> Dict:
        """Usa Gemini para analisar a estrutura e identificar questões"""
        if self.gemini_model is None:
            raise Exception("Gemini não está configurado")
        
        # Limitar tamanho do texto (Gemini 1.5+ suporta até 1M tokens, mas limitamos para performance)
        text_limited = text[:50000] if len(text) > 50000 else text
        
        prompt = f"""Você é um especialista em análise de provas de concursos públicos e exames (ENAM, ENEM, etc.).

Analise o texto abaixo e identifique TODAS as questões numeradas.

TEXTO DA PROVA:
{text_limited}

INSTRUÇÕES DETALHADAS:
1. Identifique TODAS as questões que começam com números (1, 2, 3, 4, etc.)
2. Para cada questão, extraia:
   - numero: número da questão (obrigatório)
   - texto: texto COMPLETO da questão incluindo:
     * Enunciado completo
     * Todas as alternativas (A), B), C), D), E) ou a), b), c), d), e))
     * Qualquer texto relacionado até a próxima questão
   - posicao_inicio: posição aproximada no texto (número de caracteres do início)
   - posicao_fim: posição final aproximada

FORMATO DE RESPOSTA (JSON VÁLIDO):
{{
  "questoes": [
    {{
      "numero": 1,
      "texto": "Texto completo da questão 1 com todas as alternativas A) B) C) D) E)",
      "posicao_inicio": 0,
      "posicao_fim": 500
    }},
    {{
      "numero": 2,
      "texto": "Texto completo da questão 2...",
      "posicao_inicio": 501,
      "posicao_fim": 1000
    }}
  ]
}}

CRÍTICO: Retorne APENAS JSON válido, sem markdown, sem texto adicional, sem explicações."""
        
        try:
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Limpar resposta (remover markdown code blocks se houver)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            return result
        except Exception as e:
            print(f"Erro ao analisar com Gemini: {e}")
            return {"questoes": []}
    
    def extract_questoes_with_chatgpt(self, full_text: str) -> List[Dict]:
        """Usa ChatGPT para extrair questões diretamente (quando Gemini falha)"""
        # Processar em chunks se o texto for muito grande
        max_chunk_size = 12000
        chunks = []
        
        if len(full_text) > max_chunk_size:
            # Dividir em chunks mantendo contexto
            words = full_text.split()
            current_chunk = []
            current_size = 0
            
            for word in words:
                word_size = len(word) + 1  # +1 para espaço
                if current_size + word_size > max_chunk_size and current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [word]
                    current_size = word_size
                else:
                    current_chunk.append(word)
                    current_size += word_size
            
            if current_chunk:
                chunks.append(" ".join(current_chunk))
        else:
            chunks = [full_text]
        
        all_questoes = []
        
        for chunk_idx, chunk_text in enumerate(chunks):
            # Limitar tamanho do chunk para evitar truncamento
            chunk_max_size = 8000  # Reduzir para garantir que não exceda limites
            chunk_text_limited = chunk_text[:chunk_max_size] if len(chunk_text) > chunk_max_size else chunk_text
            
            prompt = f"""Você é um especialista em análise de provas de concursos públicos e exames.

Analise o texto abaixo e identifique TODAS as questões numeradas.

TEXTO DA PROVA (parte {chunk_idx + 1} de {len(chunks)}):
{chunk_text_limited}

INSTRUÇÕES CRÍTICAS:
1. Identifique questões que começam com números (1, 2, 3, etc.)
2. Para cada questão, extraia:
   - numero: número da questão (obrigatório)
   - texto: texto COMPLETO mas LIMITADO a 2000 caracteres por questão
   - posicao_inicio: posição aproximada no texto
   - posicao_fim: posição final aproximada

REGRAS IMPORTANTES:
- Se o texto de uma questão for muito longo, trunque em 2000 caracteres
- ESCAPE todas as aspas duplas no texto usando \\"
- ESCAPE quebras de linha usando \\n
- NÃO inclua quebras de linha literais no JSON
- Garanta que todas as strings estejam entre aspas duplas
- NÃO corte strings no meio - se uma questão for muito longa, trunque ANTES de incluir no JSON

FORMATO DE RESPOSTA (JSON VÁLIDO):
{{
  "questoes": [
    {{
      "numero": 1,
      "texto": "Texto da questão 1 com alternativas A) B) C) D) E)",
      "posicao_inicio": 0,
      "posicao_fim": 500
    }}
  ]
}}

CRÍTICO: Retorne APENAS JSON válido. Todas as strings devem estar corretamente escapadas e fechadas."""
            
            try:
                # Preparar parâmetros da requisição
                request_params = {
                    "model": self.current_openai_model or "gpt-4o",
                    "messages": [
                        {"role": "system", "content": "Você é um especialista em análise de provas de concursos públicos. Retorne APENAS JSON válido, sem markdown, sem texto adicional. O JSON deve começar com { e terminar com }."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3
                }
                
                # Adicionar response_format se o modelo suportar (garante JSON válido)
                if self.supports_json_mode:
                    request_params["response_format"] = {"type": "json_object"}
                
                response = self.openai_client.chat.completions.create(**request_params)
                
                response_text = response.choices[0].message.content.strip()
                
                # Limpar resposta de markdown se houver
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    # Pode ser ```json ou apenas ```
                    parts = response_text.split("```")
                    if len(parts) >= 3:
                        response_text = parts[1].strip()
                        if response_text.startswith("json"):
                            response_text = response_text[4:].strip()
                
                # Limpar e corrigir JSON antes de parsear
                response_text_clean = response_text.strip()
                
                # Remover markdown se houver
                if "```json" in response_text_clean:
                    response_text_clean = response_text_clean.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text_clean:
                    parts = response_text_clean.split("```")
                    if len(parts) >= 3:
                        response_text_clean = parts[1].strip()
                        if response_text_clean.startswith("json"):
                            response_text_clean = response_text_clean[4:].strip()
                
                # Tentar corrigir JSON malformado
                try:
                    result = json.loads(response_text_clean)
                except json.JSONDecodeError as e:
                    print(f"⚠️ Erro ao parsear JSON do chunk {chunk_idx + 1}: {e}")
                    print(f"   Primeiros 500 caracteres: {response_text_clean[:500]}")
                    
                    # Tentar corrigir strings não terminadas
                    try:
                        # Encontrar todas as strings não terminadas e fechá-las
                        fixed_json = response_text_clean
                        
                        # Padrão: encontrar strings que começam com " mas não terminam antes de {
                        # Fechar strings não terminadas antes de fechar objetos
                        import re as regex_module
                        
                        # Tentar encontrar o JSON válido mais interno
                        json_match = regex_module.search(r'\{[^{}]*"questoes"[^{}]*\[.*?\].*?\}', fixed_json, regex_module.DOTALL)
                        if json_match:
                            try:
                                result = json.loads(json_match.group(0))
                            except:
                                pass
                        
                        # Se ainda não funcionou, tentar extrair questões manualmente
                        if 'result' not in locals():
                            # Extrair questões usando regex mais permissivo
                            questoes_matches = regex_module.findall(r'"numero"\s*:\s*(\d+).*?"texto"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', fixed_json, regex_module.DOTALL)
                            if questoes_matches:
                                questoes_fixed = []
                                for num, texto in questoes_matches:
                                    # Limpar texto e limitar tamanho
                                    texto_clean = texto.replace('\\"', '"').replace('\\n', '\n')[:2000]
                                    # Remover caracteres NUL e outros problemáticos
                                    texto_clean = texto_clean.replace('\x00', '').replace('\r', ' ')
                                    texto_clean = ''.join(char for char in texto_clean if ord(char) >= 32 or char in '\n\t')
                                    questoes_fixed.append({
                                        "numero": int(num),
                                        "texto": texto_clean,
                                        "posicao_inicio": 0,
                                        "posicao_fim": len(texto_clean)
                                    })
                                if questoes_fixed:
                                    result = {"questoes": questoes_fixed}
                                    print(f"   ✅ Extraídas {len(questoes_fixed)} questões usando regex")
                                else:
                                    print(f"   ⚠️ Não foi possível extrair questões válidas, pulando chunk")
                                    continue
                            else:
                                print(f"   ⚠️ Não foi possível extrair JSON válido, pulando chunk")
                                continue
                    except Exception as fix_error:
                        print(f"   ⚠️ Erro ao tentar corrigir JSON: {fix_error}, pulando chunk")
                        continue
                
                # Verificar se result foi definido
                if 'result' not in locals():
                    print(f"   ⚠️ Não foi possível processar chunk {chunk_idx + 1}, pulando")
                    continue
                
                questoes_chunk = result.get("questoes", [])
                
                # Ajustar posições relativas ao texto completo
                chunk_start_pos = full_text.find(chunk_text[:100]) if chunk_text else 0
                for questao in questoes_chunk:
                    if "posicao_inicio" in questao:
                        questao["posicao_inicio"] += chunk_start_pos
                    if "posicao_fim" in questao:
                        questao["posicao_fim"] += chunk_start_pos
                
                all_questoes.extend(questoes_chunk)
            except Exception as e:
                print(f"Erro ao extrair questões do chunk {chunk_idx + 1}: {e}")
                continue
        
        # Remover duplicatas por número de questão
        unique_questoes = {}
        for questao in all_questoes:
            numero = questao.get("numero")
            if numero and numero not in unique_questoes:
                unique_questoes[numero] = questao
            elif numero and numero in unique_questoes:
                # Manter a questão com mais texto
                existing = unique_questoes[numero]
                if len(questao.get("texto", "")) > len(existing.get("texto", "")):
                    unique_questoes[numero] = questao
        
        return list(unique_questoes.values())
    
    def validate_with_chatgpt(self, questoes: List[Dict], full_text: str) -> List[Dict]:
        """Usa ChatGPT para validar e refinar a extração"""
        if not questoes:
            return []
        
        # Processar TODAS as questões em lotes se necessário
        # Processar em lotes de 30 questões por vez para não exceder limites de token
        batch_size = 30
        all_validated = []
        
        for batch_start in range(0, len(questoes), batch_size):
            batch_end = min(batch_start + batch_size, len(questoes))
            questoes_batch = questoes[batch_start:batch_end]
            
            # Processar este lote
            text_sample = full_text[:10000] if len(full_text) > 10000 else full_text
            
            # Preparar questões do lote
            questoes_prepared = []
            for q in questoes_batch:
                q_copy = q.copy()
                # Truncar texto se muito longo (mas manter mais texto)
                if len(q_copy.get("texto", "")) > 2000:
                    q_copy["texto"] = q_copy["texto"][:1997] + "..."
                questoes_prepared.append(q_copy)
            
            # Preparar JSON das questões de forma segura
            questoes_json = json.dumps(questoes_prepared, ensure_ascii=False, indent=2)
            # Limitar tamanho do JSON se necessário (mas permitir mais)
            if len(questoes_json) > 8000:
                # Se ainda muito grande, reduzir número de questões no lote
                questoes_json = json.dumps(questoes_prepared[:20], ensure_ascii=False, indent=2)
        
            prompt = f"""Você é um especialista em validação de extração de questões de provas.

Valide e refine as questões extraídas abaixo. IMPORTANTE: Retorne TODAS as questões do lote, sem omitir nenhuma.

TEXTO DA PROVA (amostra):
{text_sample}

QUESTÕES EXTRAÍDAS (Lote {batch_start//batch_size + 1}):
{questoes_json}

INSTRUÇÕES:
1. Valide se TODAS as questões do lote foram identificadas e retornadas
2. Certifique-se que o texto está COMPLETO mas LIMITADO a 2000 caracteres por questão
3. ESCAPE todas as aspas duplas no texto usando \\"
4. ESCAPE quebras de linha usando \\n
5. Mantenha a ordem numérica EXATA das questões
6. Se uma questão tiver texto muito longo, trunque em 2000 caracteres ANTES de incluir no JSON
7. CRÍTICO: Retorne TODAS as questões do lote, não omita nenhuma

FORMATO DE RESPOSTA (JSON VÁLIDO):
{{
  "questoes": [
    {{
      "numero": 1,
      "texto": "Texto validado e completo da questão",
      "posicao_inicio": 0,
      "posicao_fim": 500
    }}
  ]
}}

CRÍTICO: Retorne APENAS JSON válido. Todas as strings devem estar corretamente escapadas. Retorne TODAS as questões do lote."""
            
            try:
                # Preparar parâmetros da requisição
                request_params = {
                    "model": self.current_openai_model or "gpt-4o",
                    "messages": [
                        {"role": "system", "content": "Você é um especialista em validação de extração de questões de provas. Retorne APENAS JSON válido, sem markdown, sem texto adicional. O JSON deve começar com { e terminar com }."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3
                }
                
                # Adicionar response_format se o modelo suportar (garante JSON válido)
                if self.supports_json_mode:
                    request_params["response_format"] = {"type": "json_object"}
                
                response = self.openai_client.chat.completions.create(**request_params)
                
                response_text = response.choices[0].message.content.strip()
                
                # Limpar resposta de markdown se houver
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    parts = response_text.split("```")
                    if len(parts) >= 3:
                        response_text = parts[1].strip()
                        if response_text.startswith("json"):
                            response_text = response_text[4:].strip()
                
                # Limpar e preparar JSON
                response_text_clean = response_text.strip()
                
                # Remover markdown
                if "```json" in response_text_clean:
                    response_text_clean = response_text_clean.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text_clean:
                    parts = response_text_clean.split("```")
                    if len(parts) >= 3:
                        response_text_clean = parts[1].strip()
                        if response_text_clean.startswith("json"):
                            response_text_clean = response_text_clean[4:].strip()
                
                # Tentar parsear JSON
                try:
                    result = json.loads(response_text_clean)
                except json.JSONDecodeError as e:
                    print(f"⚠️ Erro ao parsear JSON na validação (lote {batch_start//batch_size + 1}): {e}")
                    print(f"   Primeiros 500 caracteres: {response_text_clean[:500]}")
                    
                    # Tentar extrair questões manualmente
                    questoes_matches = re.findall(r'"numero"\s*:\s*(\d+).*?"texto"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', response_text_clean, re.DOTALL)
                    if questoes_matches:
                        questoes_fixed = []
                        for num, texto in questoes_matches:
                            texto_clean = texto.replace('\\"', '"').replace('\\n', '\n')[:2000]
                            # Limpar caracteres NUL e outros problemáticos
                            texto_clean = texto_clean.replace('\x00', '').replace('\r', ' ')
                            texto_clean = ''.join(char for char in texto_clean if ord(char) >= 32 or char in '\n\t')
                            questoes_fixed.append({
                                "numero": int(num),
                                "texto": texto_clean,
                                "posicao_inicio": 0,
                                "posicao_fim": len(texto_clean)
                            })
                        if questoes_fixed:
                            print(f"   ✅ Extraídas {len(questoes_fixed)} questões usando regex (lote {batch_start//batch_size + 1})")
                            all_validated.extend(questoes_fixed)
                            continue
                    
                    print(f"   ⚠️ Não foi possível extrair JSON válido para lote {batch_start//batch_size + 1}, usando questões originais")
                    all_validated.extend(questoes_prepared)
                    continue
                
                # Adicionar questões validadas do lote
                validated_batch = result.get("questoes", questoes_prepared)
                all_validated.extend(validated_batch)
                print(f"   ✅ Lote {batch_start//batch_size + 1}: {len(validated_batch)} questões validadas")
            
            except Exception as e:
                print(f"   ⚠️ Erro ao validar lote {batch_start//batch_size + 1} com ChatGPT: {e}")
                # Em caso de erro, usar questões originais do lote
                all_validated.extend(questoes_prepared)
                continue
        
        # Ordenar por número e retornar todas
        all_validated_sorted = sorted(all_validated, key=lambda x: x.get("numero", 0))
        print(f"✅ Validação completa: {len(all_validated_sorted)} questões validadas de {len(questoes)} originais")
        return all_validated_sorted
    
    def map_images_to_questoes(self, questoes: List[Dict], images: List[Dict], 
                                     pages_text: List[Dict]) -> List[Dict]:
        """Mapeia imagens às questões usando IA"""
        # Criar contexto para análise
        questoes_info = "\n".join([
            f"Questão {q['numero']}: página {self._get_page_for_position(q.get('posicao_inicio', 0), pages_text)}"
            for q in questoes
        ])
        
        images_info = "\n".join([
            f"Imagem {i+1}: página {img['page']}, posição Y: {img.get('bbox', {}).get('y0', 0) if img.get('bbox') else 'desconhecida'}"
            for i, img in enumerate(images)
        ])
        
        prompt = f"""Você é um especialista em análise de documentos acadêmicos e mapeamento de imagens.

Com base nas informações abaixo, associe cada imagem à questão mais provável.

QUESTÕES IDENTIFICADAS:
{questoes_info}

IMAGENS ENCONTRADAS:
{images_info}

INSTRUÇÕES:
1. Analise a página e posição de cada imagem
2. Associe a imagem à questão que está na mesma página ou página próxima
3. Considere a posição vertical (Y) da imagem em relação ao texto da questão
4. Se não houver associação clara, deixe questao_numero como null

FORMATO DE RESPOSTA (JSON VÁLIDO):
{{
  "associacoes": [
    {{"imagem_index": 0, "questao_numero": 1}},
    {{"imagem_index": 1, "questao_numero": null}}
  ]
}}

CRÍTICO: Retorne APENAS JSON válido, sem markdown, sem texto adicional."""
        
        try:
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text.strip()
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            associacoes = result.get("associacoes", [])
            
            # Aplicar associações
            for assoc in associacoes:
                img_index = assoc.get("imagem_index")
                questao_numero = assoc.get("questao_numero")
                
                if img_index < len(images):
                    # Encontrar questão pelo número
                    questao_id = None
                    if questao_numero:
                        for q in questoes:
                            if q.get("numero") == questao_numero:
                                questao_id = q.get("id")
                                break
                    
                    images[img_index]["questao_id"] = questao_id
                    images[img_index]["questao_numero"] = questao_numero
            
            return images
        except Exception as e:
            print(f"Erro ao mapear imagens: {e}")
            return images
    
    def _get_page_for_position(self, position: int, pages_text: List[Dict]) -> int:
        """Determina em qual página está uma posição de texto"""
        current_pos = 0
        for page in pages_text:
            page_length = len(page["text"])
            if position < current_pos + page_length:
                return page["page"]
            current_pos += page_length + 2  # +2 para quebras de linha
        return len(pages_text)


ai_analyzer = AIAnalyzer()

