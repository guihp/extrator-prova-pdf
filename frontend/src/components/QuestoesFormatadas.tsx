import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getQuestoesFormatadas, formatarQuestoes, QuestaoFormatada } from '../services/api'
import './QuestoesFormatadas.css'

const QuestoesFormatadas = () => {
  const [questoes, setQuestoes] = useState<QuestaoFormatada[]>([])
  const [loading, setLoading] = useState(true)
  const [formatando, setFormatando] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [expandedProvas, setExpandedProvas] = useState<Set<number>>(new Set())
  const navigate = useNavigate()

  // Função para renderizar texto com quebras de linha
  const renderTextoComQuebras = (texto: string) => {
    if (!texto) return null
    // Dividir por \n e renderizar com <br />
    return texto.split('\n').map((linha, index, array) => (
      <span key={index}>
        {linha}
        {index < array.length - 1 && <br />}
      </span>
    ))
  }

  useEffect(() => {
    loadQuestoes()
  }, [])

  const loadQuestoes = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getQuestoesFormatadas()
      setQuestoes(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao carregar questões formatadas')
      console.error('Erro ao carregar questões:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleFormatarQuestoes = async () => {
    if (!confirm('Tem certeza que deseja formatar todas as questões não formatadas? Isso acionará o webhook de formatação.')) {
      return
    }

    setFormatando(true)
    setError(null)
    
    try {
      const result = await formatarQuestoes()
      alert(`Webhook chamado com sucesso! ${result.questoes_nao_formatadas} questões ainda não formatadas.`)
      // Recarregar a lista após formatação
      setTimeout(() => {
        loadQuestoes()
      }, 2000)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao chamar webhook de formatação')
      console.error('Erro ao formatar questões:', err)
      alert(`Erro ao formatar questões: ${err.response?.data?.detail || err.message}`)
    } finally {
      setFormatando(false)
    }
  }

  // Função para expandir/recolher prova
  const handleToggleProva = (provaId: number) => {
    setExpandedProvas(prev => {
      const newSet = new Set(prev)
      if (newSet.has(provaId)) {
        newSet.delete(provaId)
      } else {
        newSet.add(provaId)
      }
      return newSet
    })
  }

  // Função para expandir/recolher todas as provas
  const handleToggleAllProvas = () => {
    const todasProvaIds = Object.keys(questoesPorProva).map(Number)
    const todasExpandidas = todasProvaIds.every(id => expandedProvas.has(id))
    
    if (todasExpandidas) {
      setExpandedProvas(new Set())
    } else {
      setExpandedProvas(new Set(todasProvaIds))
    }
  }

  // Agrupar questões por prova
  const questoesPorProva = questoes.reduce((acc, questao) => {
    const provaKey = questao.prova_nome || `Prova ${questao.prova_id}`
    const provaId = questao.prova_id_display || questao.prova_id
    if (!acc[provaId]) {
      acc[provaId] = {
        provaNome: provaKey,
        provaId: provaId,
        questoes: []
      }
    }
    acc[provaId].questoes.push(questao)
    return acc
  }, {} as Record<number, { provaNome: string; provaId: number; questoes: QuestaoFormatada[] }>)

  return (
    <div className="questoes-formatadas-page">
      <div className="page-header">
        <button className="back-button" onClick={() => navigate('/')}>
          ← Voltar
        </button>
        <div className="header-content">
          <h1>Questões Formatadas</h1>
          <p>Visualização de todas as questões que já foram formatadas</p>
        </div>
        <button
          className="format-button"
          onClick={handleFormatarQuestoes}
          disabled={formatando}
        >
          {formatando ? 'Formatando...' : '📝 Formatas Questões Não Formatadas'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="content">
        {loading ? (
          <div className="loading-state">
            <p>Carregando questões formatadas...</p>
          </div>
        ) : questoes.length === 0 ? (
          <div className="empty-state">
            <p>Nenhuma questão formatada encontrada.</p>
            <p>Clique no botão acima para formatar questões não formatadas.</p>
          </div>
        ) : (
          <div className="questoes-container">
            {Object.keys(questoesPorProva).length > 0 && (
              <div className="controls-bar">
                <button
                  className="toggle-all-button"
                  onClick={handleToggleAllProvas}
                >
                  {Object.keys(questoesPorProva).every(id => expandedProvas.has(Number(id)))
                    ? '🔽 Recolher Todas'
                    : '▶️ Expandir Todas'}
                </button>
              </div>
            )}
            {Object.values(questoesPorProva).map((grupo) => {
              const isExpanded = expandedProvas.has(grupo.provaId)
              return (
                <div key={grupo.provaId} className="prova-group">
                  <div 
                    className="prova-header-clickable"
                    onClick={() => handleToggleProva(grupo.provaId)}
                  >
                    <h2 className="prova-title">
                      📄 {grupo.provaNome} 
                      <span className="questoes-count">({grupo.questoes.length} questão{grupo.questoes.length !== 1 ? 'ões' : ''})</span>
                    </h2>
                    <svg
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      className={`expand-icon ${isExpanded ? 'expanded' : ''}`}
                    >
                      <polyline points="6 9 12 15 18 9" />
                    </svg>
                  </div>
                  {isExpanded && (
                    <div className="questoes-list">
                      {grupo.questoes.map((questao) => (
                        <div key={questao.id} className="questao-card">
                          <div className="questao-header">
                            <span className="questao-number">Questão {questao.numero}</span>
                            <span className="formatado-badge">✓ Formatada</span>
                          </div>
                          <div className="questao-texto">
                            {renderTextoComQuebras(
                              questao.texto_formatado && questao.texto_formatado.trim() !== '' 
                                ? questao.texto_formatado 
                                : questao.texto
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

export default QuestoesFormatadas

