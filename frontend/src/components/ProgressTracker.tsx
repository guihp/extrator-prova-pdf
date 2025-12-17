import { useState } from 'react'
import { Prova, getProvaCompleta, cancelarTarefasPendentes, cancelarTarefa } from '../services/api'
import './ProgressTracker.css'

interface ProgressTrackerProps {
  provas: Prova[]
}

const ProgressTracker = ({ provas }: ProgressTrackerProps) => {
  const [expandedProva, setExpandedProva] = useState<number | null>(null)
  const [provaDetalhes, setProvaDetalhes] = useState<{ [key: number]: any }>({})
  const [loading, setLoading] = useState<{ [key: number]: boolean }>({})
  const [cancelling, setCancelling] = useState(false)

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'concluido':
        return '#4caf50'
      case 'processando':
      case 'extraindo':
      case 'analisando':
      case 'mapeando_imagens':
      case 'salvando_imagens':
        return '#ff9800'
      case 'erro':
        return '#f44336'
      default:
        return '#666'
    }
  }

  const getStatusLabel = (status: string) => {
    const labels: { [key: string]: string } = {
      processando: 'Processando',
      extraindo: 'Extraindo conteúdo',
      analisando: 'Analisando com IA',
      mapeando_imagens: 'Mapeando imagens',
      salvando_imagens: 'Salvando imagens',
      concluido: 'Concluído',
      erro: 'Erro',
    }
    return labels[status] || status
  }

  const handleToggleProva = async (provaId: number) => {
    if (expandedProva === provaId) {
      setExpandedProva(null)
      return
    }

    setExpandedProva(provaId)
    setLoading({ ...loading, [provaId]: true })

    try {
      const detalhes = await getProvaCompleta(provaId)
      setProvaDetalhes({ ...provaDetalhes, [provaId]: detalhes })
    } catch (error) {
      console.error('Erro ao carregar detalhes:', error)
    } finally {
      setLoading({ ...loading, [provaId]: false })
    }
  }

  const handleCancelarTodas = async () => {
    if (!confirm('Tem certeza que deseja cancelar todas as tarefas pendentes?')) {
      return
    }

    setCancelling(true)
    try {
      const result = await cancelarTarefasPendentes()
      alert(result.message)
      window.location.reload()
    } catch (error: any) {
      alert(`Erro ao cancelar tarefas: ${error.response?.data?.detail || error.message}`)
    } finally {
      setCancelling(false)
    }
  }

  const handleCancelarTarefa = async (provaId: number, event: React.MouseEvent) => {
    event.stopPropagation()
    if (!confirm('Tem certeza que deseja cancelar esta tarefa?')) {
      return
    }

    try {
      const result = await cancelarTarefa(provaId)
      alert(result.message)
      window.location.reload()
    } catch (error: any) {
      alert(`Erro ao cancelar tarefa: ${error.response?.data?.detail || error.message}`)
    }
  }

  const provasPendentes = provas.filter(p => 
    ['processando', 'extraindo', 'analisando', 'filtrando_imagens', 'mapeando_imagens', 'salvando_imagens'].includes(p.status)
  )

  return (
    <div className="progress-tracker">
      {provasPendentes.length > 0 && (
        <div className="cancel-all-section">
          <button
            className="cancel-all-button"
            onClick={handleCancelarTodas}
            disabled={cancelling}
          >
            {cancelling ? 'Cancelando...' : `❌ Cancelar Todas (${provasPendentes.length} pendentes)`}
          </button>
        </div>
      )}
      
      {provas.map((prova) => (
        <div key={prova.id} className="prova-card">
          <div
            className="prova-header"
            onClick={() => handleToggleProva(prova.id)}
          >
            <div className="prova-info">
              <h3>{prova.nome}</h3>
              <p className="prova-meta">
                {new Date(prova.criado_em).toLocaleString('pt-BR')}
              </p>
            </div>
            <div className="prova-status">
              {prova.progresso !== null && prova.progresso !== undefined && (
                <div className="progress-bar-container">
                  <div className="progress-bar">
                    <div 
                      className="progress-bar-fill" 
                      style={{ width: `${prova.progresso}%` }}
                    />
                  </div>
                  <span className="progress-text">{prova.progresso}%</span>
                </div>
              )}
              <span
                className="status-badge"
                style={{ backgroundColor: getStatusColor(prova.status) }}
              >
                {getStatusLabel(prova.status)}
              </span>
              {['processando', 'extraindo', 'analisando', 'filtrando_imagens', 'mapeando_imagens', 'salvando_imagens'].includes(prova.status) && (
                <button
                  className="cancel-button"
                  onClick={(e) => handleCancelarTarefa(prova.id, e)}
                  title="Cancelar tarefa"
                >
                  ✕
                </button>
              )}
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                className={`expand-icon ${expandedProva === prova.id ? 'expanded' : ''}`}
              >
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </div>
          </div>

          {expandedProva === prova.id && (
            <div className="prova-details">
              {prova.etapa && (
                <div className="etapa-section">
                  <h4>📋 Logs de Processamento</h4>
                  <div className="etapa-logs">
                    {prova.etapa.split('\n').map((linha: string, idx: number) => (
                      <div key={idx} className="log-line">{linha}</div>
                    ))}
                  </div>
                </div>
              )}
              {loading[prova.id] ? (
                <p>Carregando detalhes...</p>
              ) : provaDetalhes[prova.id] ? (
                <div className="details-content">
                  <div className="detail-section">
                    <h4>Questões ({provaDetalhes[prova.id].questoes.length})</h4>
                    <div className="questoes-list">
                      {provaDetalhes[prova.id].questoes.map((questao: any) => (
                        <div key={questao.id} className="questao-item">
                          <strong>Questão {questao.numero}:</strong>
                          <p>{questao.texto.substring(0, 200)}...</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="detail-section">
                    <h4>Imagens ({provaDetalhes[prova.id].imagens.length})</h4>
                    <div className="imagens-grid">
                      {provaDetalhes[prova.id].imagens.map((imagem: any) => (
                        <div key={imagem.id} className="imagem-item">
                          <img
                            src={imagem.caminho_arquivo}
                            alt={`Imagem página ${imagem.posicao_pagina}`}
                            onError={(e) => {
                              ;(e.target as HTMLImageElement).style.display = 'none'
                            }}
                          />
                          <p>Página {imagem.posicao_pagina}</p>
                          {imagem.questao_id && (
                            <span className="questao-tag">
                              Questão {provaDetalhes[prova.id].questoes.find((q: any) => q.id === imagem.questao_id)?.numero || '?'}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <p>Nenhum detalhe disponível</p>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

export default ProgressTracker

