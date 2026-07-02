<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useSpeech } from '@/composables/useSpeech'
import { useApi } from '@/composables/useApi'
import DialogueItem from '@/components/DialogueItem.vue'
import { useInterviewStore } from '@/stores/interview'

interface Dialogue {
  id: string
  question: string
  answer: string
  is_valid: boolean
  rule: string
  created_at: string
}

const router = useRouter()
const { isListening, currentText, state, isSupported, startListening, stopListening, forceStop, error: speechError } = useSpeech()
const { submitTranscript, getDialogues, processQuestionStream, error: apiError } = useApi()
const store = useInterviewStore()

const statusMessage = ref('准备中...')
const showEndConfirm = ref(false)
const dialoguesContainer = ref<HTMLElement | null>(null)
const dialogues = ref<Dialogue[]>([])

onMounted(async () => {
  if (!isSupported()) {
    statusMessage.value = '浏览器不支持语音识别，请使用 Chrome 或 Edge 浏览器'
    return
  }

  statusMessage.value = '正在启动语音识别...'

  const speechOk = await startListening({
    onResult: handleSpeechResult,
    onError: (err) => {
      statusMessage.value = '识别错误: ' + err
    }
  })

  if (!speechOk) {
    statusMessage.value = '语音识别启动失败: ' + (speechError.value || '未知错误')
    return
  }

  statusMessage.value = '🎤 正在监听面试官提问...'
})

onUnmounted(() => {
  stopListening()
})

async function handleSpeechResult(result: { text: string; isFinal: boolean; confidence: number }) {
  if (!result.text || result.text.trim().length === 0) return

  if (!result.isFinal) return

  const text = result.text.trim()
  console.log('识别完成:', text)

  const response = await submitTranscript(text)

  if (response?.data?.is_valid) {
    const dialogue = response.data
    dialogues.value.push(dialogue)
    autoScroll()
    statusMessage.value = '✅ 问题已识别，正在生成回答...'

    if (!store.isConfigured) {
      const idx = dialogues.value.findIndex(d => d.id === dialogue.id)
      if (idx !== -1) {
        dialogues.value[idx].answer = '请先在首页配置火山引擎API Key'
      }
      statusMessage.value = '⚠️ 未配置API Key，无法调用大模型'
      return
    }

    await processQuestionStream(
      {
        question: text,
        ark_api_key: store.apiKey,
        model_id: store.modelId,
        kb_id: store.kbId,
        kb_api_key: store.kbApiKey
      },
      (chunk) => {
        const idx = dialogues.value.findIndex(d => d.id === dialogue.id)
        if (idx !== -1) {
          dialogues.value[idx].answer += chunk
          autoScroll()
        }
      },
      (knowledgeUsed) => {
        const idx = dialogues.value.findIndex(d => d.id === dialogue.id)
        if (idx !== -1) {
          if (!dialogues.value[idx].answer) {
            dialogues.value[idx].answer = '生成失败'
          }
        }
        statusMessage.value = '🎤 正在监听面试官提问...'
      },
      (error) => {
        const idx = dialogues.value.findIndex(d => d.id === dialogue.id)
        if (idx !== -1) {
          dialogues.value[idx].answer = '生成失败: ' + error
        }
        statusMessage.value = '⚠️ 生成失败，请重试'
      }
    )
  } else {
    console.log('问题判断跳过:', response?.data?.reason)
  }
}

function autoScroll() {
  nextTick(() => {
    if (dialoguesContainer.value) {
      dialoguesContainer.value.scrollTop = dialoguesContainer.value.scrollHeight
    }
  })
}

function confirmEndInterview() {
  showEndConfirm.value = true
}

function endInterview() {
  stopListening()
  router.push('/')
}

function cancelEnd() {
  showEndConfirm.value = false
}

async function handleManualComplete() {
  const result = forceStop()
  if (result) {
    await handleSpeechResult(result)
    
    statusMessage.value = '🎤 正在监听面试官提问...'
    const speechOk = await startListening({
      onResult: handleSpeechResult,
      onError: (err) => {
        statusMessage.value = '识别错误: ' + err
      }
    })
    
    if (!speechOk) {
      statusMessage.value = '语音识别重启失败: ' + (speechError.value || '未知错误')
    }
  }
}

function getPhaseClass() {
  switch (state.value) {
    case 'listening': return 'status-listening'
    case 'recognizing': return 'status-recognizing'
    case 'starting': return 'status-starting'
    case 'error': return 'status-error'
    default: return 'bg-white/10 text-white/60 border-white/20'
  }
}

function getPhaseIcon() {
  switch (state.value) {
    case 'listening': return '🎤'
    case 'recognizing': return '🔍'
    case 'starting': return '⏳'
    case 'error': return '❌'
    default: return '⚪'
  }
}
</script>

<template>
  <div class="flex flex-col h-screen">
    <header class="glass-card mx-4 mt-4 mb-2 px-6 py-4 flex items-center justify-between shrink-0">
      <div class="flex items-center gap-3">
        <span class="text-2xl">🐯</span>
        <h1 class="text-xl font-bold text-white">面试虎</h1>
      </div>

      <div
        class="status-badge"
        :class="getPhaseClass()"
      >
        <span>{{ getPhaseIcon() }}</span>
        <span>{{ statusMessage }}</span>
      </div>

      <button
        @click="confirmEndInterview"
        class="btn-danger px-4 py-2 text-sm rounded-xl"
      >
        结束面试
      </button>
    </header>

    <main
      ref="dialoguesContainer"
      class="flex-1 overflow-y-auto px-4 pb-4"
    >
      <div
        v-if="dialogues.length === 0"
        class="flex flex-col items-center justify-center h-full text-white/50"
      >
        <div class="text-8xl mb-6 animate-pulse-soft">🎤</div>
        <p class="text-xl font-semibold mb-3 text-white">面试已就绪</p>
        <p class="text-sm text-white/40">请确保设备麦克风已开启，系统将自动识别面试官提问</p>
        <p class="text-xs text-white/30 mt-4">💡 识别过程中点击"完成"按钮可手动提交</p>
      </div>

      <div class="max-w-6xl mx-auto">
        <template v-for="item in dialogues" :key="item.id">
          <DialogueItem :item="item" />
        </template>
      </div>
    </main>

    <footer class="glass-card mx-4 mb-4 px-6 py-4 shrink-0">
      <div class="flex items-center gap-3 max-w-4xl mx-auto">
        <div class="flex-1 px-4 py-3 bg-white/5 backdrop-blur-sm rounded-xl text-sm min-h-[48px] flex items-center border border-white/10">
          <span v-if="currentText" class="text-white/70 italic">{{ currentText }}...</span>
          <span v-else-if="state === 'listening'" class="text-white/30">等待识别中...</span>
          <span v-else-if="state === 'recognizing'" class="text-white/40">正在识别...</span>
          <span v-else-if="state === 'error'" class="text-error">{{ speechError }}</span>
          <span v-else class="text-white/30">准备中...</span>
        </div>

        <button
          v-if="isListening && currentText"
          @click="handleManualComplete"
          class="btn-accent px-5 py-3 text-sm font-medium rounded-xl shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all"
          title="手动完成识别"
        >
          ✅ 完成
        </button>

        <button
          v-if="dialogues.length > 0"
          @click="dialogues = []"
          class="px-4 py-3 text-sm text-white/60 hover:text-white hover:bg-white/10 rounded-xl transition-all"
          title="清空对话"
        >
          🗑️ 清空
        </button>
      </div>
    </footer>

    <div
      v-if="showEndConfirm"
      class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      @click.self="cancelEnd"
    >
      <div class="glass-card-light w-full max-w-sm p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-2">结束面试？</h3>
        <p class="text-sm text-gray-500 mb-6">
          面试对话记录将被保留，你可以在首页查看历史记录。
        </p>
        <div class="flex gap-3">
          <button
            @click="cancelEnd"
            class="flex-1 px-4 py-3 rounded-xl border border-gray-300 text-gray-700 font-medium hover:bg-gray-50 transition-all"
          >
            继续面试
          </button>
          <button
            @click="endInterview"
            class="flex-1 btn-danger py-3 rounded-xl"
          >
            确认结束
          </button>
        </div>
      </div>
    </div>
  </div>
</template>