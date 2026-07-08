// API 调用 Composable - TASK-012
import axios, { type AxiosInstance } from 'axios'
import { ref } from 'vue'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export function useApi() {
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const client: AxiosInstance = axios.create({
    baseURL: BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json'
    }
  })

  // 请求拦截器
  client.interceptors.request.use(
    (config) => {
      isLoading.value = true
      error.value = null
      return config
    },
    (err) => {
      isLoading.value = false
      return Promise.reject(err)
    }
  )

  // 响应拦截器
  client.interceptors.response.use(
    (response) => {
      isLoading.value = false
      return response
    },
    (err) => {
      isLoading.value = false
      error.value = err.response?.data?.message || err.message || '请求失败'
      return Promise.reject(err)
    }
  )

  // 健康检查
  async function healthCheck(): Promise<boolean> {
    try {
      const res = await client.get<ApiResponse>('/health')
      return res.data.code === 0
    } catch {
      return false
    }
  }

  // 保存配置
  async function saveConfig(config: {
    ark_api_key: string
    kb_id: string
    model_id: string
  }): Promise<boolean> {
    try {
      const res = await client.post<ApiResponse>('/config', config)
      return res.data.code === 0
    } catch {
      return false
    }
  }

  // 获取配置状态
  async function getConfig(): Promise<ApiResponse | null> {
    try {
      const res = await client.get<ApiResponse>('/config')
      return res.data
    } catch {
      return null
    }
  }

  // 处理问题（非流式）
  async function processQuestion(params: {
    question: string
    ark_api_key: string
    model_id: string
    kb_id?: string
    kb_api_key?: string
    kb_provider?: string
  }): Promise<ApiResponse<{ answer: string; knowledge_used: boolean }> | null> {
    try {
      const res = await client.post<ApiResponse<{ answer: string; knowledge_used: boolean }>>(
        '/question',
        { ...params, stream: false }
      )
      return res.data
    } catch {
      return null
    }
  }

  // 处理问题（流式SSE）
  async function processQuestionStream(
    params: {
      question: string
      ark_api_key: string
      model_id: string
      kb_id?: string
      kb_api_key?: string
      kb_provider?: string
    },
    onChunk: (chunk: string) => void,
    onDone: (knowledgeUsed: boolean) => void,
    onError: (error: string) => void
  ): Promise<void> {
    try {
      const response = await fetch(`${BASE_URL}/question/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...params, stream: true })
      })

      if (!response.ok) {
        onError(`请求失败: ${response.status}`)
        return
      }

      const reader = response.body?.getReader()
      if (!reader) {
        onError('无法读取响应流')
        return
      }

      const decoder = new TextDecoder()
      let buffer = ''

      let knowledgeUsed = false

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              // 兼容旧版后端 [DONE] 信号
              onDone(false)
              return
            }
            try {
              const parsed = JSON.parse(data)
              if (parsed.type === 'chunk') {
                onChunk(parsed.content)
              } else if (parsed.type === 'done') {
                knowledgeUsed = parsed.knowledge_used || false
                onDone(knowledgeUsed)
              } else if (parsed.type === 'error') {
                onError(parsed.message || '生成失败')
              }
              // status 类型的消息忽略（仅用于调试）
            } catch {
              // 忽略解析错误
            }
          }
        }
      }

      // 流自然结束但未收到 done 信号时的兜底
      onDone(knowledgeUsed)
    } catch (e: any) {
      onError(e.message || '网络错误')
    }
  }

  // 提交识别文本
  async function submitTranscript(text: string, sessionId?: string): Promise<ApiResponse | null> {
    try {
      const res = await client.post<ApiResponse>('/transcript', { text, session_id: sessionId })
      return res.data
    } catch {
      return null
    }
  }

  // 获取对话列表
  async function getDialogues(sessionId?: string): Promise<ApiResponse<{ dialogues: any[] }> | null> {
    try {
      const params = sessionId ? { session_id: sessionId } : {}
      const res = await client.get<ApiResponse<{ dialogues: any[] }>>('/dialogues', { params })
      return res.data
    } catch {
      return null
    }
  }

  // 清空对话列表
  async function clearDialogues(sessionId?: string): Promise<boolean> {
    try {
      const params = sessionId ? { session_id: sessionId } : {}
      const res = await client.delete<ApiResponse>('/dialogues', { params })
      return res.data.code === 0
    } catch {
      return false
    }
  }

  // 更新对话回答
  async function updateDialogue(dialogueId: string, answer: string): Promise<ApiResponse | null> {
    try {
      const res = await client.put<ApiResponse>(`/dialogues/${dialogueId}`, { answer })
      return res.data
    } catch (err) {
      console.error('保存回答失败:', err)
      return null
    }
  }

  return {
    isLoading,
    error,
    client,
    healthCheck,
    saveConfig,
    getConfig,
    processQuestion,
    processQuestionStream,
    submitTranscript,
    getDialogues,
    clearDialogues,
    updateDialogue
  }
}
