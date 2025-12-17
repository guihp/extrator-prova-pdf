from celery import Celery
from app.config import settings
import sys

celery_app = Celery(
    "analize_pdf",
    broker=settings.redis_url,
    backend=settings.redis_url
)

# No macOS, usar 'solo' pool em vez de 'prefork' para evitar SIGSEGV
# 'solo' é single-threaded mas mais estável no macOS
pool_type = 'solo' if sys.platform == 'darwin' else 'prefork'

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_pool=pool_type,
    worker_prefetch_multiplier=1,  # Importante para solo pool
)

# Importar tarefas para que sejam registradas
from app.tasks.process_pdf import process_pdf_task

