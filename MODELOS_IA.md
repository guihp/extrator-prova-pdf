# 🤖 Modelos de IA Utilizados

## 📊 Modelos Configurados

### Gemini (Google)

**Ordem de Preferência (tentativa automática):**
1. `gemini-2.0-flash-exp` - Mais recente (experimental, mais rápido)
2. `gemini-1.5-pro` - Mais poderoso e estável (recomendado para qualidade)
3. `gemini-1.5-flash` - Mais rápido (boa qualidade)
4. `gemini-1.0-pro` - Fallback estável
5. `gemini-pro` - Último fallback

**Características:**
- ✅ Suporta até 1M tokens (Gemini 1.5+)
- ✅ Melhor para análise de documentos longos
- ✅ Excelente para processamento de imagens
- ✅ Gratuito com limites generosos

**Uso no Sistema:**
- Análise estrutural de provas
- Mapeamento de imagens às questões
- Identificação de questões numeradas

### OpenAI (ChatGPT)

**Ordem de Preferência (detecção automática):**
1. `gpt-4o` - Mais recente e melhor (recomendado)
   - ✅ Suporta JSON mode (`response_format`)
   - ✅ Melhor qualidade de extração
   - ✅ Mais rápido que gpt-4
   
2. `gpt-4-turbo` - Versão turbo
   - ✅ Suporta JSON mode
   - ✅ Boa qualidade
   
3. `gpt-4` - Fallback
   - ❌ Não suporta JSON mode
   - ✅ Boa qualidade
   
4. `gpt-3.5-turbo` - Último fallback
   - ✅ Suporta JSON mode
   - ⚠️ Qualidade menor

**Características:**
- ✅ JSON Mode disponível (gpt-4o, gpt-4-turbo, gpt-3.5-turbo)
- ✅ Garante JSON válido quando suportado
- ✅ Excelente para extração estruturada

**Uso no Sistema:**
- Extração de questões (múltiplas estratégias)
- Validação e refinamento de questões
- Fallback quando Gemini não está disponível

## 🔄 Detecção Automática

O sistema detecta automaticamente:
1. **Melhor modelo Gemini disponível** - Tenta modelos mais recentes primeiro
2. **Melhor modelo OpenAI disponível** - Testa disponibilidade e suporta JSON mode
3. **Fallback automático** - Se um modelo falhar, tenta o próximo

## 📈 Melhorias com Modelos Recentes

### Gemini 2.0 / 1.5 Pro:
- ✅ Melhor compreensão de contexto
- ✅ Melhor processamento de imagens
- ✅ Suporte a documentos muito longos
- ✅ Respostas mais precisas

### GPT-4o:
- ✅ JSON Mode (garante JSON válido)
- ✅ Melhor qualidade de extração
- ✅ Menos erros de parsing
- ✅ Respostas mais consistentes

## ⚙️ Configuração

Os modelos são configurados automaticamente no `__init__` do `AIAnalyzer`:

```python
# Gemini: Tenta modelos mais recentes primeiro
model_names = [
    'gemini-2.0-flash-exp',  # Mais recente
    'gemini-1.5-pro',        # Mais poderoso
    'gemini-1.5-flash',      # Mais rápido
    'gemini-1.0-pro',        # Fallback
    'gemini-pro'             # Último fallback
]

# OpenAI: Detecta melhor modelo disponível
openai_models = [
    'gpt-4o',           # Mais recente (JSON mode ✅)
    'gpt-4-turbo',      # Turbo (JSON mode ✅)
    'gpt-4',            # Fallback (JSON mode ❌)
    'gpt-3.5-turbo'     # Último fallback (JSON mode ✅)
]
```

## 🎯 Recomendações

### Para Melhor Qualidade:
- **Gemini:** `gemini-1.5-pro` (mais estável e poderoso)
- **OpenAI:** `gpt-4o` (melhor qualidade + JSON mode)

### Para Melhor Performance:
- **Gemini:** `gemini-1.5-flash` ou `gemini-2.0-flash-exp` (mais rápido)
- **OpenAI:** `gpt-4o` (rápido e de alta qualidade)

### Para Economia:
- **Gemini:** Qualquer versão (todas têm limites generosos)
- **OpenAI:** `gpt-3.5-turbo` (mais barato, ainda suporta JSON mode)

## 📝 Notas

- O sistema tenta automaticamente os modelos mais recentes
- Se um modelo não estiver disponível, usa o próximo da lista
- JSON mode é usado automaticamente quando suportado (garante JSON válido)
- Logs mostram qual modelo foi configurado na inicialização




