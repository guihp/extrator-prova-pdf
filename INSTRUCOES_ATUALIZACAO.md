# 📋 Instruções de Atualização

## ✅ Funcionalidades Adicionadas

### 1. **Logs Detalhados**
- Cada etapa do processamento agora registra logs detalhados
- Logs incluem timestamp, etapa atual e progresso
- Logs são salvos no banco de dados e exibidos no frontend

### 2. **Barra de Progresso**
- Progresso de 0% a 100% para cada prova
- Atualização em tempo real durante o processamento

### 3. **Botão de Cancelar**
- Botão para cancelar todas as tarefas pendentes
- Botão individual para cancelar cada tarefa
- Confirmação antes de cancelar

### 4. **Exibição de Logs no Frontend**
- Seção dedicada para logs de processamento
- Logs formatados com estilo de terminal
- Scroll automático para ver logs mais recentes

## 🔧 Atualização do Banco de Dados

Execute o script SQL para adicionar as novas colunas:

```bash
# Conecte ao PostgreSQL e execute:
psql -h 72.60.146.143 -p 5435 -U postgres -d postgres -f ATUALIZAR_BANCO_ETAPA.sql
```

Ou execute manualmente:

```sql
ALTER TABLE provas 
ADD COLUMN IF NOT EXISTS etapa TEXT,
ADD COLUMN IF NOT EXISTS progresso INTEGER DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_provas_status ON provas(status);
CREATE INDEX IF NOT EXISTS idx_provas_progresso ON provas(progresso);
```

## 🚀 Como Usar

### Backend
1. **Reinicie o Celery Worker:**
   ```bash
   pkill -9 -f "celery.*worker"
   cd backend && source venv/bin/activate
   celery -A app.tasks worker --loglevel=info --pool=solo
   ```

2. **Reinicie o FastAPI (se necessário):**
   ```bash
   # O FastAPI já deve estar rodando, mas se precisar:
   cd backend && source venv/bin/activate
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend
1. **Reinicie o servidor de desenvolvimento:**
   ```bash
   cd frontend
   npm run dev
   ```

## 📊 Novos Endpoints

### `POST /provas/cancelar-pendentes`
Cancela todas as tarefas pendentes.

**Resposta:**
```json
{
  "message": "X tarefas canceladas",
  "provas_atualizadas": X,
  "erros": null
}
```

### `POST /provas/{prova_id}/cancelar`
Cancela uma tarefa específica.

**Resposta:**
```json
{
  "message": "Tarefa cancelada com sucesso",
  "prova_id": 123
}
```

## 🎨 Interface

### Botão "Cancelar Todas"
- Aparece quando há provas pendentes
- Mostra quantas provas estão pendentes
- Cancela todas as tarefas ativas no Celery

### Botão de Cancelar Individual (✕)
- Aparece ao lado de cada prova em processamento
- Cancela apenas aquela tarefa específica
- Atualiza o status para "cancelado"

### Seção de Logs
- Aparece quando você expande uma prova
- Mostra as últimas 10 mensagens de log
- Formato de terminal (fundo escuro, texto claro)
- Scroll automático

### Barra de Progresso
- Mostra o progresso de 0% a 100%
- Atualiza em tempo real
- Cor verde quando completa

## 🔍 Logs Detalhados

Os logs incluem:
- **Timestamp** de cada ação
- **Etapa atual** (1/9, 2/9, etc.)
- **Descrição detalhada** do que está sendo executado
- **Progresso** numérico
- **Resultados** de cada estratégia
- **Erros** com traceback completo

### Exemplo de Log:
```
[19:15:30] 🚀 Iniciando processamento da prova 123 (Task ID: abc-123)
[19:15:32] 🔍 [ETAPA 1/9] Extraindo texto de imagens com OCR...
[19:15:35] ✅ OCR concluído: 5 páginas processadas
[19:15:36] 📄 [ETAPA 2/9] Extraindo conteúdo do PDF (texto + imagens)...
[19:15:38] ✅ PDF extraído: 10 páginas, 15 imagens encontradas
[19:15:40] 🔍 [ETAPA 3/9] Extraindo questões com múltiplas estratégias...
[19:15:42] 📝 [3.1] Estratégia 1: Regex por página...
[19:15:43]    ✅ Regex: 25 questões encontradas
...
```

## ⚠️ Notas Importantes

1. **Cancelamento de Tarefas:**
   - O cancelamento tenta parar a tarefa no Celery
   - Se a tarefa já estiver muito avançada, pode não parar imediatamente
   - O status será atualizado para "cancelado" no banco

2. **Logs:**
   - Os logs são limitados às últimas 10 mensagens para não sobrecarregar o banco
   - Logs antigos são substituídos por novos

3. **Progresso:**
   - O progresso é calculado baseado nas etapas do processamento
   - Pode não ser 100% preciso devido à natureza assíncrona

## 🐛 Troubleshooting

### Se os logs não aparecerem:
1. Verifique se o banco foi atualizado com as novas colunas
2. Verifique se o Celery Worker foi reiniciado
3. Verifique os logs do Celery para erros

### Se o cancelamento não funcionar:
1. Verifique se o Celery Worker está rodando
2. Tente cancelar manualmente via terminal:
   ```bash
   celery -A app.tasks control revoke <task_id> --terminate
   ```

### Se a barra de progresso não atualizar:
1. Verifique se o frontend está atualizando a cada 5 segundos
2. Verifique o console do navegador para erros
3. Verifique se o campo `progresso` foi adicionado ao banco




