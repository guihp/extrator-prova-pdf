# 🔧 Correção do Erro SIGSEGV no macOS

## Problema
O Celery estava crashando com `signal 11 (SIGSEGV)` ao processar PDFs no macOS.

## Causa
O pool `prefork` do Celery não funciona bem no macOS com bibliotecas nativas como PyMuPDF (fitz).

## Solução Aplicada

1. **Mudança do pool do Celery para 'solo' no macOS**
   - O pool 'solo' é single-threaded mas muito mais estável no macOS
   - Evita problemas de fork/multiprocessing

2. **Melhor tratamento de erros no PDF extractor**
   - Try/finally para garantir fechamento do documento
   - Tratamento individual de imagens

## 🚀 Como Aplicar

**Reinicie o Celery Worker com o novo pool:**

```bash
cd /Volumes/HD/Codigos/AnalizePDF/backend
source venv/bin/activate
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

Ou simplesmente reinicie (o código já detecta macOS e usa 'solo' automaticamente):

```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

## ⚠️ Nota

O pool 'solo' processa uma tarefa por vez (não paralelo), mas é muito mais estável no macOS. Para produção em Linux, o sistema automaticamente usa 'prefork' (paralelo).

## ✅ Teste

Agora tente fazer upload de um PDF novamente. O erro SIGSEGV não deve mais ocorrer!






