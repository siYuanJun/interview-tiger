// 面试状态管理 Pinia Store - TASK-016
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { DEFAULT_MODEL_ID, DEFAULT_KB_ID } from '@/constants'

export interface DialogueItem {
  id: string
  question: string
  answer: string
  timestamp: number
  status: 'generating' | 'done'
  knowledgeUsed: boolean
}

export type InterviewPhase = 'idle' | 'listening' | 'thinking' | 'answering'

export const useInterviewStore = defineStore('interview', () => {
  // --- 面试状态 ---
  const phase = ref<InterviewPhase>('idle')
  const isInterviewActive = ref(false)

  // --- 对话列表 ---
  const dialogues = ref<DialogueItem[]>([])

  // --- 音频状态 ---
  const isRecording = ref(false)
  const isSpeechSupported = ref(true)

  // --- 配置 ---
  const apiKey = ref(localStorage.getItem('ark_api_key') || '')
  const kbId = ref(localStorage.getItem('kb_id') || DEFAULT_KB_ID)
  const kbApiKey = ref(localStorage.getItem('kb_api_key') || '')
  const modelId = ref(localStorage.getItem('model_id') || DEFAULT_MODEL_ID)
  const kbProvider = ref(localStorage.getItem('kb_provider') || DEFAULT_KB_PROVIDER)

  // --- 计算属性 ---
  const dialogueCount = computed(() => dialogues.value.length)
  const isConfigured = computed(() => !!apiKey.value)
  const lastDialogue = computed(() =>
    dialogues.value.length > 0 ? dialogues.value[dialogues.value.length - 1] : null
  )

  // --- 对话操作 ---
  function addDialogue(question: string) {
    const id = `dialogue-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
    const item: DialogueItem = {
      id,
      question,
      answer: '',
      timestamp: Date.now(),
      status: 'generating',
      knowledgeUsed: false
    }
    dialogues.value.push(item)
    return item
  }

  function updateAnswer(dialogueId: string, chunk: string) {
    const item = dialogues.value.find(d => d.id === dialogueId)
    if (item) {
      item.answer += chunk
    }
  }

  function completeDialogue(dialogueId: string, knowledgeUsed: boolean = false) {
    const item = dialogues.value.find(d => d.id === dialogueId)
    if (item) {
      item.status = 'done'
      item.knowledgeUsed = knowledgeUsed
    }
  }

  function clearDialogues() {
    dialogues.value = []
  }

  // --- 面试控制 ---
  function startInterview() {
    isInterviewActive.value = true
    phase.value = 'listening'
  }

  function endInterview() {
    isInterviewActive.value = false
    phase.value = 'idle'
    isRecording.value = false
  }

  function setPhase(newPhase: InterviewPhase) {
    phase.value = newPhase
  }

  // --- 配置操作 ---
  function saveConfig(config: { apiKey: string; kbId: string; kbApiKey: string; modelId: string; kbProvider?: string }) {
    apiKey.value = config.apiKey
    kbId.value = config.kbId
    kbApiKey.value = config.kbApiKey
    modelId.value = config.modelId
    kbProvider.value = config.kbProvider || DEFAULT_KB_PROVIDER

    localStorage.setItem('ark_api_key', config.apiKey)
    localStorage.setItem('kb_id', config.kbId)
    localStorage.setItem('kb_api_key', config.kbApiKey)
    localStorage.setItem('model_id', config.modelId)
    localStorage.setItem('kb_provider', kbProvider.value)
  }

  // --- 导出对话 ---
  function exportDialogues(format: 'json' | 'txt' | 'markdown' = 'markdown'): string {
    if (format === 'json') {
      return JSON.stringify(dialogues.value, null, 2)
    }
    if (format === 'txt') {
      return dialogues.value
        .map(d => `Q: ${d.question}\nA: ${d.answer}\n---`)
        .join('\n\n')
    }
    // markdown
    return dialogues.value
      .map(d => `### Q: ${d.question}\n\n${d.answer}\n\n---`)
      .join('\n\n')
  }

  return {
    phase,
    isInterviewActive,
    dialogues,
    isRecording,
    isSpeechSupported,
    apiKey,
    kbId,
    kbApiKey,
    modelId,
    kbProvider,
    dialogueCount,
    isConfigured,
    lastDialogue,
    addDialogue,
    updateAnswer,
    completeDialogue,
    clearDialogues,
    startInterview,
    endInterview,
    setPhase,
    saveConfig,
    exportDialogues
  }
})
