<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useSpeech } from '@/composables/useSpeech'
import { useApi } from '@/composables/useApi'
import DialogueItem from '@/components/DialogueItem.vue'
import TigerLogo from '@/components/TigerLogo.vue'
import VoiceWave from '@/components/VoiceWave.vue'
import { useInterviewStore } from '@/stores/interview'
import { 
  Mic, 
  Search, 
  Clock, 
  XCircle, 
  Circle, 
  CheckCircle, 
  Trash2, 
  PhoneOff,
  Pause,
  Play
} from 'lucide-vue-next'

interface Dialogue {
  id: string
  question: string
  answer: string
  is_valid: boolean
  rule: string
  created_at: string
}

interface InterimDialogue {
  id: string
  question: string
}

const router = useRouter()
const { isListening, currentText, state, isSupported, startListening, stopListening, forceStop, resumeListening, pauseRecognition, error: speechError } = useSpeech()
const { submitTranscript, getDialogues, processQuestionStream, updateDialogue, getConfig, clearDialogues, error: apiError } = useApi()
const store = useInterviewStore()

const statusMessage = ref('准备中...')
const showEndConfirm = ref(false)
const showClearConfirm = ref(false)
const dialoguesContainer = ref<HTMLElement | null>(null)
const dialogues = ref<Dialogue[]>([])
const interimDialogue = ref<InterimDialogue | null>(null)
const backendConfigured = ref(false)
const isPaused = ref(false)

let sessionId = sessionStorage.getItem('interview_session_id') || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
sessionStorage.setItem('interview_session_id', sessionId)

onMounted(async () => {
  if (!isSupported()) {
    statusMessage.value = '浏览器不支持语音识别，请使用 Chrome 或 Edge 浏览器'
    return
  }

  const configRes = await getConfig()
  backendConfigured.value = configRes?.data?.ark_api_key_configured || false
  if (configRes?.data) {
    if (!store.apiKey) {
      store.saveConfig({
        apiKey: '',
        kbId: configRes.data.kb_id || '',
        kbApiKey: '',
        modelId: configRes.data.model_id || ''
      })
    }
  }

  const savedDialogues = await getDialogues(sessionId)
    if (savedDialogues?.data?.dialogues) {
      dialogues.value = savedDialogues.data.dialogues
      autoScroll()
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

  statusMessage.value = '正在监听面试官提问...'
})

onUnmounted(() => {
  stopListening()
})

async function handleSpeechResult(result: { text: string; isFinal: boolean; confidence: number }) {
  if (!result.text || result.text.trim().length === 0) return

  const text = result.text.trim()

  if (!result.isFinal) {
    interimDialogue.value = {
      id: 'interim-' + Date.now(),
      question: text
    }
    autoScroll()
    return
  }

  interimDialogue.value = null
  console.log('识别完成:', text)

  resumeListening()

  const response = await submitTranscript(text, sessionId)

  if (response?.data?.is_valid) {
    const dialogue = response.data
    dialogues.value.push(dialogue)
    autoScroll()
    statusMessage.value = '问题已识别，正在生成回答...'

    if (!store.isConfigured && !backendConfigured.value) {
      const idx = dialogues.value.findIndex(d => d.id === dialogue.id)
      if (idx !== -1) {
        dialogues.value[idx].answer = '请先在首页配置火山引擎API Key'
      }
      statusMessage.value = '未配置API Key，无法调用大模型'
      return
    }

    processQuestionStream(
      {
        question: text,
        ark_api_key: store.apiKey,
        model_id: store.modelId,
        kb_id: store.kbId,
        kb_api_key: store.kbApiKey,
        kb_provider: store.kbProvider
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
          updateDialogue(dialogue.id, dialogues.value[idx].answer)
        }
        statusMessage.value = '正在监听面试官提问...'
      },
      (error) => {
        const idx = dialogues.value.findIndex(d => d.id === dialogue.id)
        if (idx !== -1) {
          dialogues.value[idx].answer = '生成失败: ' + error
        }
        statusMessage.value = '生成失败，请重试'
      }
    )
  } else {
    interimDialogue.value = null
    console.log('语音输入跳过:', response?.data?.reason)
  }
}

function autoScroll() {
  nextTick(() => {
    nextTick(() => {
      if (dialoguesContainer.value) {
        dialoguesContainer.value.scrollTop = dialoguesContainer.value.scrollHeight
      }
    })
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

function confirmClear() {
  showClearConfirm.value = true
}

function cancelClear() {
  showClearConfirm.value = false
}

async function handleClearDialogues() {
  const success = await clearDialogues(sessionId)
  if (success) {
    dialogues.value = []
    showClearConfirm.value = false
  }
}

async function togglePause() {
  if (isPaused.value) {
    const speechOk = await resumeListening()
    if (speechOk) {
      isPaused.value = false
      statusMessage.value = '正在监听面试官提问...'
    }
  } else {
    pauseRecognition()
    isPaused.value = true
    statusMessage.value = '已暂停，点击恢复继续面试'
  }
}

async function handleManualComplete() {
  interimDialogue.value = null
  const result = forceStop()
  if (result) {
    await handleSpeechResult(result)
    
    statusMessage.value = '正在监听面试官提问...'
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
    default: return 'bg-muted/30 text-foreground/60 border-border/30'
  }
}

function getPhaseIcon() {
  switch (state.value) {
    case 'listening': return Mic
    case 'recognizing': return Search
    case 'starting': return Clock
    case 'error': return XCircle
    default: return Circle
  }
}
</script>

<template>
  <div class="flex flex-col h-screen bg-background relative overflow-hidden">
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-primary/5 via-transparent to-accent/5"></div>
      <div class="absolute top-1/4 left-1/4 w-[400px] h-[400px] bg-primary/10 rounded-full blur-[150px] animate-pulse-neon"></div>
      <div class="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-accent/10 rounded-full blur-[150px] animate-pulse-neon" style="animation-delay: 1s"></div>
    </div>

    <header class="glass-card-strong mx-4 mt-4 mb-2 px-6 py-4 flex items-center justify-between shrink-0 z-10">
      <div class="flex items-center gap-3">
        <TigerLogo :size="50" :radius="22" :glow="false" />
        <h1 class="text-xl font-bold font-heading">
          <span class="text-white glow-text-primary">面试虎</span>
        </h1>
      </div>

      <div
        class="status-badge"
        :class="getPhaseClass()"
      >
        <component :is="getPhaseIcon()" class="w-4 h-4" />
        <span>{{ statusMessage }}</span>
      </div>

      <button
        @click="confirmEndInterview"
        class="bg-gradient-to-r from-red-500 to-red-600 text-white px-5 py-2.5 rounded-xl font-medium text-sm hover:shadow-lg hover:shadow-red-500/30 transition-all duration-300 flex items-center gap-2"
      >
        <PhoneOff class="w-4 h-4" />
        结束面试
      </button>
    </header>

    <main
      ref="dialoguesContainer"
      class="flex-1 overflow-y-auto px-4 pb-4 z-10"
    >
      <div
        v-if="dialogues.length === 0"
        class="flex flex-col items-center justify-center h-full"
      >
        <div class="mb-8">
          <VoiceWave :size="144" :status="state" />
        </div>
        <p class="text-2xl font-bold text-white font-heading mb-3">面试已就绪</p>
        <p class="text-sm text-foreground/50 text-center max-w-md">请确保设备麦克风已开启，系统将自动识别面试官提问</p>
        <p class="text-xs text-foreground/30 mt-4">识别过程中点击"完成"按钮可手动提交</p>
      </div>

      <div class="max-w-[95vw] md:max-w-5xl lg:max-w-7xl mx-auto">
        <template v-for="item in dialogues" :key="item.id">
          <DialogueItem :item="item" />
        </template>

        <div
          v-if="interimDialogue"
          class="flex gap-4 mb-4 animate-fade-in"
        >
          <div class="flex-1">
            <div class="dialogue-bubble-user relative">
              <div class="absolute -top-1 -right-1 w-3 h-3 bg-primary rounded-full animate-pulse"></div>
              <p class="text-sm text-white">{{ interimDialogue.question }}</p>
              <p class="text-xs text-white/50 mt-2 flex items-center gap-1">
                <Search class="w-3 h-3" />
                正在识别中...
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>

    <footer class="glass-card-strong mx-4 mb-4 px-6 py-4 shrink-0 z-10">
      <div class="flex items-center gap-4 max-w-4xl mx-auto">
        <div class="flex-1 px-5 py-3 bg-[rgba(30,27,75,0.6)] backdrop-blur-sm rounded-xl text-sm min-h-[52px] flex items-center border border-[rgba(123,58,237,0.2)]">
          <span v-if="currentText" class="text-foreground/70 italic">{{ currentText }}...</span>
          <span v-else-if="state === 'listening'" class="text-foreground/30">等待识别中...</span>
          <span v-else-if="state === 'recognizing'" class="text-foreground/40">正在识别...</span>
          <span v-else-if="state === 'error'" class="text-red-400">{{ speechError }}</span>
          <span v-else class="text-foreground/30">准备中...</span>
        </div>

        <button
          v-if="isListening && currentText"
          @click="handleManualComplete"
          class="bg-gradient-to-r from-[#60a5fa] to-[#c084fc] text-white px-5 py-3 text-sm font-semibold rounded-xl hover:shadow-lg hover:shadow-[rgba(123,58,237,0.3)] transition-all duration-300 flex items-center gap-2"
          title="手动完成识别"
        >
          <CheckCircle class="w-4 h-4" />
          完成
        </button>

        <button
          v-if="dialogues.length > 0"
          @click="confirmClear"
          class="btn-secondary-glass px-5 py-3 text-sm flex items-center gap-2"
          title="清空对话"
        >
          <Trash2 class="w-4 h-4" />
          清空
        </button>

        <button
          @click="togglePause"
          :class="[
            'px-5 py-3 text-sm font-medium rounded-xl flex items-center gap-2 transition-all duration-300',
            isPaused 
              ? 'bg-gradient-to-r from-[#60a5fa] to-[#c084fc] text-white hover:shadow-lg hover:shadow-[rgba(123,58,237,0.3)]' 
              : 'btn-secondary-glass'
          ]"
          :title="isPaused ? '恢复面试' : '暂停面试'"
        >
          <Play v-if="isPaused" class="w-4 h-4" />
          <Pause v-else class="w-4 h-4" />
          {{ isPaused ? '恢复' : '暂停' }}
        </button>
      </div>
    </footer>

    <div
      v-if="showEndConfirm"
      class="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4"
      @click.self="cancelEnd"
    >
      <div class="glass-card-strong w-full max-w-sm p-7 animate-slide-in-right">
        <h3 class="text-lg font-semibold text-white font-heading mb-3">结束面试？</h3>
        <p class="text-sm text-foreground/60 mb-7">面试对话记录将被保留，你可以在首页查看历史记录。</p>
        <div class="flex gap-4">
          <button
            @click="cancelEnd"
            class="flex-1 btn-secondary-glass py-3"
          >
            继续面试
          </button>
          <button
            @click="endInterview"
            class="flex-1 bg-gradient-to-r from-red-500 to-red-600 text-white py-3 rounded-xl font-medium hover:shadow-lg hover:shadow-red-500/30 transition-all duration-300"
          >
            确认结束
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="showClearConfirm"
      class="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4"
      @click.self="cancelClear"
    >
      <div class="glass-card-strong w-full max-w-sm p-7 animate-slide-in-right">
        <h3 class="text-lg font-semibold text-white font-heading mb-3">清空对话？</h3>
        <p class="text-sm text-foreground/60 mb-7">此操作将删除当前会话的所有对话记录，且无法恢复。</p>
        <div class="flex gap-4">
          <button
            @click="cancelClear"
            class="flex-1 btn-secondary-glass py-3"
          >
            取消
          </button>
          <button
            @click="handleClearDialogues"
            class="flex-1 bg-gradient-to-r from-red-500 to-red-600 text-white py-3 rounded-xl font-medium hover:shadow-lg hover:shadow-red-500/30 transition-all duration-300"
          >
            确认清空
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
