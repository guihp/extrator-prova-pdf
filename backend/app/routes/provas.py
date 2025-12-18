from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from typing import List, Dict
import os
import uuid
import httpx
from app.services.db_service import db_service
from app.services.export_service import export_service
from app.tasks.process_pdf import process_pdf_task
from app.tasks import celery_app
from app.models.schemas import ProvaResponse, QuestaoResponse, ImagemResponse, ProvaCompletaResponse, QuestaoFormatadaResponse
from app.config import settings

router = APIRouter()


@router.post("/upload", response_model=Dict)
async def upload_pdf(file: UploadFile = File(...)):
    """Endpoint para upload de PDF"""
    # Validar tipo de arquivo
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são permitidos")
    
    # Validar tamanho
    contents = await file.read()
    if len(contents) > settings.max_file_size:
        raise HTTPException(status_code=400, detail="Arquivo muito grande")
    
    # Salvar arquivo temporário
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.pdf"
    file_path = os.path.join(settings.upload_dir, filename)
    
    os.makedirs(settings.upload_dir, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Criar registro no banco
    prova = db_service.create_prova(
        nome=file.filename,
        arquivo_original=file.filename
    )
    
    if not prova:
        raise HTTPException(status_code=500, detail="Erro ao criar prova no banco")
    
    # Enfileirar tarefa de processamento
    process_pdf_task.delay(prova["id"], file_path)
    
    return {
        "message": "PDF enviado com sucesso",
        "prova_id": prova["id"],
        "status": "processando"
    }


@router.get("/", response_model=List[ProvaResponse])
async def list_provas():
    """Lista todas as provas"""
    provas = db_service.list_provas()
    return provas


@router.get("/{prova_id}", response_model=ProvaCompletaResponse)
async def get_prova_completa(prova_id: int):
    """Busca uma prova completa com questões e imagens"""
    prova = db_service.get_prova(prova_id)
    if not prova:
        raise HTTPException(status_code=404, detail="Prova não encontrada")
    
    questoes = db_service.get_questoes_by_prova(prova_id)
    imagens = db_service.get_imagens_by_prova(prova_id)
    
    return {
        "prova": prova,
        "questoes": questoes,
        "imagens": imagens
    }


@router.get("/{prova_id}/questoes", response_model=List[QuestaoResponse])
async def get_questoes(prova_id: int):
    """Busca questões de uma prova"""
    questoes = db_service.get_questoes_by_prova(prova_id)
    return questoes


@router.get("/{prova_id}/imagens", response_model=List[ImagemResponse])
async def get_imagens(prova_id: int):
    """Busca imagens de uma prova"""
    imagens = db_service.get_imagens_by_prova(prova_id)
    return imagens


@router.get("/questoes/{questao_id}", response_model=QuestaoResponse)
async def get_questao_individual(questao_id: int):
    """Busca uma questão individual por ID"""
    questao = db_service.get_questao(questao_id)
    if not questao:
        raise HTTPException(status_code=404, detail="Questão não encontrada")
    return questao


@router.get("/questoes/formatadas/listar", response_model=List[QuestaoFormatadaResponse])
async def listar_questoes_formatadas():
    """Lista todas as questões formatadas (formatado = 'true')"""
    questoes = db_service.get_questoes_formatadas()
    return questoes


@router.post("/questoes/formatar", response_model=Dict)
async def formatar_questoes():
    """Chama o webhook para formatar questões não formatadas"""
    try:
        webhook_url = "https://n8n-dwok8s4ocwwosgsso4ooo0c8.flowera.com.br/webhook/formatar-perguntas-prova-pdf"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, timeout=30.0)
            response.raise_for_status()
            
            count = db_service.get_questoes_nao_formatadas_count()
            
            return {
                "message": "Webhook chamado com sucesso",
                "questoes_nao_formatadas": count,
                "status": "sucesso"
            }
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Erro ao chamar webhook: {e.response.text}"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro de conexão com webhook: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao formatar questões: {str(e)}"
        )


@router.get("/{prova_id}/exportar/pdf")
async def exportar_prova_pdf(prova_id: int):
    """Exporta todas as questões de uma prova em PDF"""
    prova = db_service.get_prova(prova_id)
    if not prova:
        raise HTTPException(status_code=404, detail="Prova não encontrada")
    
    questoes = db_service.get_questoes_by_prova(prova_id)
    imagens = db_service.get_imagens_by_prova(prova_id)
    
    if not questoes:
        raise HTTPException(status_code=404, detail="Nenhuma questão encontrada para esta prova")
    
    pdf_buffer = export_service.export_to_pdf(
        questoes=questoes,
        imagens=imagens,
        prova_nome=prova.get("nome", "Prova")
    )
    
    filename = f"{prova.get('nome', 'prova').replace('.pdf', '')}_questoes.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/{prova_id}/exportar/word")
async def exportar_prova_word(prova_id: int):
    """Exporta todas as questões de uma prova em Word (DOCX)"""
    prova = db_service.get_prova(prova_id)
    if not prova:
        raise HTTPException(status_code=404, detail="Prova não encontrada")
    
    questoes = db_service.get_questoes_by_prova(prova_id)
    imagens = db_service.get_imagens_by_prova(prova_id)
    
    if not questoes:
        raise HTTPException(status_code=404, detail="Nenhuma questão encontrada para esta prova")
    
    word_buffer = export_service.export_to_word(
        questoes=questoes,
        imagens=imagens,
        prova_nome=prova.get("nome", "Prova")
    )
    
    filename = f"{prova.get('nome', 'prova').replace('.pdf', '')}_questoes.docx"
    
    return StreamingResponse(
        word_buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/questoes/{questao_id}/exportar/pdf")
async def exportar_questao_pdf(questao_id: int):
    """Exporta uma questão individual em PDF"""
    questao = db_service.get_questao(questao_id)
    if not questao:
        raise HTTPException(status_code=404, detail="Questão não encontrada")
    
    # Buscar imagens relacionadas
    imagens = db_service.get_imagens_by_prova(questao.get("prova_id"))
    imagens_questao = [img for img in imagens if img.get("questao_id") == questao_id]
    
    pdf_buffer = export_service.export_questao_individual_pdf(
        questao=questao,
        imagens=imagens_questao
    )
    
    filename = f"questao_{questao.get('numero', questao_id)}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/questoes/{questao_id}/exportar/word")
async def exportar_questao_word(questao_id: int):
    """Exporta uma questão individual em Word (DOCX)"""
    questao = db_service.get_questao(questao_id)
    if not questao:
        raise HTTPException(status_code=404, detail="Questão não encontrada")
    
    # Buscar imagens relacionadas
    imagens_questao = db_service.get_imagens_by_questao(questao_id)
    
    word_buffer = export_service.export_questao_individual_word(
        questao=questao,
        imagens=imagens_questao
    )
    
    filename = f"questao_{questao.get('numero', questao_id)}.docx"
    
    return StreamingResponse(
        word_buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.post("/cancelar-pendentes", response_model=Dict)
async def cancelar_tarefas_pendentes():
    """Cancela todas as tarefas pendentes"""
    try:
        # Buscar todas as provas com status pendente/processando
        provas = db_service.list_provas()
        provas_pendentes = [p for p in provas if p.get("status") in ["processando", "extraindo", "analisando", "filtrando_imagens", "mapeando_imagens", "salvando_imagens"]]
        
        canceladas = 0
        erros = []
        
        # Buscar tarefas ativas no Celery
        try:
            inspect = celery_app.control.inspect()
            active_tasks = inspect.active()
            
            if active_tasks:
                for worker, tasks in active_tasks.items():
                    for task in tasks:
                        task_name = task.get("name", "")
                        if "process_pdf_task" in task_name:
                            task_id = task.get("id")
                            try:
                                # Revogar e terminar a tarefa
                                celery_app.control.revoke(task_id, terminate=True, signal='SIGKILL')
                                canceladas += 1
                                print(f"✅ Tarefa {task_id} cancelada")
                            except Exception as e:
                                erros.append(f"Erro ao cancelar task {task_id}: {e}")
        except Exception as e:
            erros.append(f"Erro ao inspecionar tarefas ativas: {e}")
        
        # Atualizar status das provas pendentes
        for prova in provas_pendentes:
            try:
                db_service.update_prova_status(
                    prova["id"], 
                    "cancelado",
                    etapa="Tarefa cancelada pelo usuário",
                    progresso=0
                )
            except Exception as e:
                erros.append(f"Erro ao atualizar prova {prova['id']}: {e}")
        
        return {
            "message": f"{canceladas} tarefas canceladas, {len(provas_pendentes)} provas atualizadas",
            "tarefas_canceladas": canceladas,
            "provas_atualizadas": len(provas_pendentes),
            "erros": erros if erros else None
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao cancelar tarefas: {str(e)}")


@router.post("/{prova_id}/cancelar", response_model=Dict)
async def cancelar_tarefa(prova_id: int):
    """Cancela uma tarefa específica"""
    try:
        task_cancelada = False
        task_id_encontrado = None
        
        # Buscar tarefas ativas
        try:
            inspect = celery_app.control.inspect()
            active_tasks = inspect.active()
            
            if active_tasks:
                for worker, tasks in active_tasks.items():
                    for task in tasks:
                        task_name = task.get("name", "")
                        task_args = task.get("args", [])
                        # Verificar se é a tarefa desta prova
                        if "process_pdf_task" in task_name and len(task_args) > 0 and task_args[0] == prova_id:
                            task_id_encontrado = task.get("id")
                            try:
                                # Revogar e terminar a tarefa
                                celery_app.control.revoke(task_id_encontrado, terminate=True, signal='SIGKILL')
                                task_cancelada = True
                                print(f"✅ Tarefa {task_id_encontrado} cancelada para prova {prova_id}")
                            except Exception as e:
                                print(f"⚠️ Erro ao cancelar task {task_id_encontrado}: {e}")
                                # Continuar mesmo se falhar, para atualizar o status
        except Exception as e:
            print(f"⚠️ Erro ao inspecionar tarefas: {e}")
            # Continuar para atualizar o status mesmo se não conseguir cancelar a tarefa
        
        # Atualizar status da prova (sempre, mesmo se não encontrar a tarefa)
        try:
            db_service.update_prova_status(
                prova_id,
                "cancelado",
                etapa="Tarefa cancelada pelo usuário",
                progresso=0
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao atualizar status da prova: {str(e)}")
        
        return {
            "message": "Tarefa cancelada com sucesso" if task_cancelada else "Status atualizado para cancelado (tarefa pode já ter finalizado)",
            "prova_id": prova_id,
            "task_cancelada": task_cancelada,
            "task_id": task_id_encontrado
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao cancelar tarefa: {str(e)}")

