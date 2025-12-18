import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface Prova {
  id: number
  nome: string
  arquivo_original: string
  status: string
  criado_em: string
  progresso?: number | null
  etapa?: string | null
}

export interface Questao {
  id: number
  prova_id: number
  numero: number
  texto: string
  ordem: number
  texto_formatado?: string
  formatado?: boolean
}

export interface QuestaoFormatada extends Questao {
  prova_nome?: string
  prova_id_display?: number
}

export interface Imagem {
  id: number
  prova_id: number
  questao_id: number | null
  caminho_arquivo: string
  posicao_pagina: number
}

export interface ProvaCompleta {
  prova: Prova
  questoes: Questao[]
  imagens: Imagem[]
}

export const uploadPDF = async (file: File): Promise<{ prova_id: number; status: string }> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await axios.post(`${API_BASE_URL}/provas/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return response.data
}

export const getProvas = async (): Promise<Prova[]> => {
  const response = await axios.get(`${API_BASE_URL}/provas/`)
  return response.data
}

export const getProvaCompleta = async (provaId: number): Promise<ProvaCompleta> => {
  const response = await axios.get(`${API_BASE_URL}/provas/${provaId}`)
  return response.data
}

export const getQuestoes = async (provaId: number): Promise<Questao[]> => {
  const response = await axios.get(`${API_BASE_URL}/provas/${provaId}/questoes`)
  return response.data
}

export const getImagens = async (provaId: number): Promise<Imagem[]> => {
  const response = await axios.get(`${API_BASE_URL}/provas/${provaId}/imagens`)
  return response.data
}

export const getQuestoesFormatadas = async (): Promise<QuestaoFormatada[]> => {
  const response = await axios.get(`${API_BASE_URL}/provas/questoes/formatadas/listar`)
  return response.data
}

export const formatarQuestoes = async (): Promise<{ message: string; questoes_nao_formatadas: number; status: string }> => {
  const response = await axios.post(`${API_BASE_URL}/provas/questoes/formatar`)
  return response.data
}

export const cancelarTarefasPendentes = async (): Promise<{ message: string; tarefas_canceladas: number; provas_atualizadas: number }> => {
  const response = await axios.post(`${API_BASE_URL}/provas/cancelar-pendentes`)
  return response.data
}

export const cancelarTarefa = async (provaId: number): Promise<{ message: string; prova_id: number }> => {
  const response = await axios.post(`${API_BASE_URL}/provas/${provaId}/cancelar`)
  return response.data
}

