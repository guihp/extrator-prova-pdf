import { useState, useEffect } from 'react'
import UploadForm from './components/UploadForm'
import ProgressTracker from './components/ProgressTracker'
import { getProvas, Prova } from './services/api'
import './App.css'

function App() {
  const [provas, setProvas] = useState<Prova[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadProvas()
    // Atualizar lista a cada 5 segundos
    const interval = setInterval(loadProvas, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadProvas = async () => {
    try {
      const data = await getProvas()
      setProvas(data)
    } catch (error) {
      console.error('Erro ao carregar provas:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUploadSuccess = () => {
    loadProvas()
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Sistema de Análise de PDFs</h1>
        <p>Faça upload de provas em PDF para análise automática</p>
      </header>

      <main className="app-main">
        <div className="container">
          <UploadForm onUploadSuccess={handleUploadSuccess} />

          <div className="provas-section">
            <h2>Provas Processadas</h2>
            {loading ? (
              <p>Carregando...</p>
            ) : provas.length === 0 ? (
              <p className="empty-state">Nenhuma prova processada ainda.</p>
            ) : (
              <ProgressTracker provas={provas} />
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default App

