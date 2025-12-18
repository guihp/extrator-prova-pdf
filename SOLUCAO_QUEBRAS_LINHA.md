# Solução para Quebras de Linha no Texto Formatado

## Problema
O texto formatado enviado pelo n8n contém quebras de linha (`\n`), mas quando exibido no frontend, essas quebras não aparecem visualmente.

## Solução Implementada

### ✅ No Frontend (Já Corrigido)

A solução foi implementada em duas partes:

1. **CSS** (`QuestoesFormatadas.css`):
   - Adicionado `white-space: pre-line` na classe `.questao-texto`
   - Isso faz o HTML respeitar quebras de linha (`\n`) no texto

2. **React Component** (`QuestoesFormatadas.tsx`):
   - Criada função `renderTextoComQuebras()` que:
     - Divide o texto por `\n`
     - Renderiza cada linha com um `<br />` entre elas
   - Garante que mesmo que o CSS não funcione, as quebras aparecem

### 📋 No n8n (Recomendação)

Para garantir que as quebras de linha sejam preservadas corretamente, no n8n:

#### Opção 1: Usar quebras de linha reais (Recomendado)
No nó que prepara o texto para o banco de dados:
- Se você tem o texto em uma variável, use quebras de linha reais (Enter) em vez da string `"\n"`
- Ou use a função para substituir: `replace(/\r?\n/g, '\n')`

#### Opção 2: Converter string "\n" em quebra real
No nó antes de salvar no banco:
- Use uma expressão para converter: `{{ $json.texto.replace(/\\n/g, '\n') }}`
- Isso converte a string literal `"\n"` em uma quebra de linha real

#### Exemplo no n8n (Postgres Update):
No campo `texto_formatado`:
```javascript
{{ $json.texto.replace(/\\n/g, '\n') }}
// ou simplesmente use $json.texto se já vier com quebras reais
```

## Como Funciona Agora

1. **n8n envia** → texto com `\n` (seja string literal ou quebra real)
2. **Banco de dados** → armazena como TEXT com quebras
3. **Backend (FastAPI)** → retorna JSON (quebras preservadas como `\n`)
4. **Frontend (React)** → função `renderTextoComQuebras()` converte `\n` em `<br />`
5. **CSS** → `white-space: pre-line` também preserva quebras como fallback

## Testando

1. Verifique se o texto no banco tem quebras de linha reais:
   ```sql
   SELECT id, texto_formatado FROM questoes WHERE formatado = true LIMIT 1;
   ```

2. No frontend, as questões formatadas devem mostrar:
   - Cada linha em uma nova linha
   - Alternativas (A, B, C, D) cada uma em sua própria linha

## Nota Técnica

O banco PostgreSQL preserva quebras de linha normalmente. O problema geralmente está em:
- **n8n** enviando `\n` como string literal (2 caracteres: `\` + `n`)
- **Frontend** não renderizando `\n` em HTML (HTML ignora whitespace por padrão)

A solução cobre ambos os casos! ✅

