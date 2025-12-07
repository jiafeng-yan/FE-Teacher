import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const chatAPI = {
  sendMessage: async (userId, message, conversationId = null) => {
    const response = await api.post('/api/chat', {
      user_id: userId,
      message,
      conversation_id: conversationId,
    })
    return response.data
  },
}

export const uploadAPI = {
  uploadDocument: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
}

export const progressAPI = {
  getProgress: async (userId) => {
    const response = await api.get(`/api/progress/${userId}`)
    return response.data
  },
  updateProgress: async (userId, update) => {
    const response = await api.post(`/api/progress/${userId}`, update)
    return response.data
  },
}

export const knowledgeAPI = {
  getInfo: async () => {
    const response = await api.get('/api/knowledge/info')
    return response.data
  },
  search: async (query, k = 5) => {
    const response = await api.post('/api/knowledge/search', null, {
      params: { query, k },
    })
    return response.data
  },
  getChunkSettings: async () => {
    const response = await api.get('/api/knowledge/chunk-settings')
    return response.data
  },
  updateChunkSettings: async (chunkSize, chunkOverlap) => {
    const response = await api.post('/api/knowledge/chunk-settings', {
      chunk_size: chunkSize,
      chunk_overlap: chunkOverlap,
    })
    return response.data
  },
  reindex: async (chunkSize, chunkOverlap, confirm = false) => {
    const response = await api.post('/api/knowledge/reindex', {
      chunk_size: chunkSize,
      chunk_overlap: chunkOverlap,
      confirm,
    })
    return response.data
  },
}

export default api

