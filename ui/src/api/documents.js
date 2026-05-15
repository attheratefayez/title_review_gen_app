import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
})

export function uploadDocument(file) {
  const form = new FormData()
  form.append('file', file)
  return api.post('/api/documents/upload', form)
}

export function generateReview(documentId) {
  return api.post(`/api/documents/${documentId}/generate`)
}

export function getReview(documentId) {
  return api.get(`/api/documents/${documentId}/review`)
}

export function saveReview(documentId, content) {
  return api.put(`/api/documents/${documentId}/review`, { content })
}
