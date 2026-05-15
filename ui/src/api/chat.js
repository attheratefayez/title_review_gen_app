import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
})

export function sendMessage(text) {
  return api.post('/api/chat', { message: text })
}

export function getChatHistory() {
  return api.get('/api/chat/history')
}
