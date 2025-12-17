import { useState, useRef } from 'react'
import { uploadPDF } from '../services/api'
import './UploadForm.css'

interface UploadFormProps {
  onUploadSuccess: () => void
}

const UploadForm = ({ onUploadSuccess }: UploadFormProps) => {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleFileSelect = (selectedFile: File) => {
    if (!selectedFile.name.endsWith('.pdf')) {
      setError('Por favor, selecione um arquivo PDF')
      return
    }
    setFile(selectedFile)
    setError(null)
    setSuccess(null)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      handleFileSelect(droppedFile)
    }
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      handleFileSelect(selectedFile)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!file) {
      setError('Por favor, selecione um arquivo')
      return
    }

    setUploading(true)
    setError(null)
    setSuccess(null)

    try {
      const result = await uploadPDF(file)
      setSuccess(`PDF enviado com sucesso! ID: ${result.prova_id}. Processando...`)
      setFile(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      onUploadSuccess()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao fazer upload do arquivo')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="upload-form-container">
      <form onSubmit={handleSubmit} className="upload-form">
        <div
          className={`upload-area ${isDragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileInputChange}
            style={{ display: 'none' }}
          />
          <div className="upload-content">
            {file ? (
              <>
                <svg
                  width="48"
                  height="48"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="16" y1="13" x2="8" y2="13" />
                  <line x1="16" y1="17" x2="8" y2="17" />
                  <polyline points="10 9 9 9 8 9" />
                </svg>
                <p className="file-name">{file.name}</p>
                <p className="file-size">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </>
            ) : (
              <>
                <svg
                  width="64"
                  height="64"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                <p className="upload-text">
                  Arraste um arquivo PDF aqui ou clique para selecionar
                </p>
                <p className="upload-hint">Apenas arquivos PDF são aceitos</p>
              </>
            )}
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <button
          type="submit"
          disabled={!file || uploading}
          className="submit-button"
        >
          {uploading ? 'Enviando...' : 'Enviar PDF'}
        </button>
      </form>
    </div>
  )
}

export default UploadForm

