import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// 管理后台鉴权——所有写操作需要携带 API Key
api.interceptors.request.use((config) => {
  if (['post', 'put', 'delete', 'patch'].includes(config.method)) {
    config.headers['x-admin-key'] = 'admin-lingshan-2024'
  }
  return config
})

export async function askQuestion(question, history = []) {
  const { data } = await api.post('/chat/ask', { question, history })
  return data
}

/**
 * 流式问答 — 返回 ReadableStream reader
 * 用法:
 *   for await (const event of askQuestionStream(question, history)) {
 *     if (event.token) { ... }
 *     if (event.done) { ... }
 *   }
 */
export async function* askQuestionStream(question, history = []) {
  const resp = await fetch('/api/chat/ask/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, history }),
  })

  if (!resp.ok) {
    throw new Error(`Stream error: ${resp.status}`)
  }

  const reader = resp.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          yield JSON.parse(line.slice(6))
        } catch {
          // skip malformed
        }
      }
    }
  }
}

export async function synthesizeSpeech(text, voice = 'zh-CN-XiaoxiaoNeural') {
  const body = { text }
  if (voice) body.voice = voice
  const { data } = await api.post('/tts/synthesize', body)
  return data
}

export async function getVoices() {
  const { data } = await api.get('/tts/voices')
  return data
}

export async function getRecommendation(params) {
  const { data } = await api.post('/recommend', params)
  return data
}

export default api
