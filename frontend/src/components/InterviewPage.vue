<script setup lang="ts">
// 面试页面主组件 - TASK-014
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useRecorder } from '@/composables/useRecorder'
import { useSpeech } from '@/composables/useSpeech'
import { useApi } from '@/composables/useApi'
import { useInterviewStore } from '@/stores/interview'
import { validateQuestion } from '@/utils/questionJudge'
import DialogueItem from '@/components/DialogueItem.vue'

const router = useRouter()
const store = useInterviewStore()
const { isRecording, startRecording, stopRecording, error: recorderError } = useRecorder()
const { isListening, currentText, finalText, isSupported, startListening, stopListening } = useSpeech()
const { processQuestionStream, error: apiError } = useApi()

const statusMessage = ref('准备中...')
const showEndConfirm = ref(false)
const dialoguesContainer = ref<HTMLElement | null>(null)

// 页面加载时自动开始面试流程
onMounted(async () => {
  if (!store.isConfigured) {
    statusMessage.value = '请先配置API Key'
    return
  }

  // 检测语音支持
  if (!isSupported()) {
    store.isSpeechSupported = false
    store.setPhase('idle')
    statusMessage.value = '浏览器不支持语音识别，请使用Chrome浏览器'
    return
  }

  // 开始录音
  statusMessage.value = '正在请求麦克风权限...'
  const ok = await startRecording()
  if (!ok) {
    statusMessage.value = '麦克风权限获取失败: ' + (recorderError.value || '未知错误')
    return
  }

  // 开始语音识别
  statusMessage.value = '正在启动语音识别...'
  store.startInterview()
  store.setPhase('listening')
  statusMessage.value = '🎤 正在监听面试官提问...'

  startListening({
    onResult: handleSpeechResult,
    onError: (err) => {
      statusMessage.value = '识别错误: ' + err
    }
  })

  isRecording.value = true
})

onUnmounted(() => {
  stopListening()
  stopRecording()
})

// 处理语音识别结果
async function handleSpeechResult(result: { text: string; isFinal: boolean; confidence: number }) {
  if (!result.text || result.text.trim().length === 0) return

  // 仅处理最终结果
  if (!result.isFinal) return

  const text = result.text.trim()

  // 判断是否为有效问题
  const validation = validateQuestion(text)
  if (!validation.isValid) {
    console.log('问题判断跳过:', validation.reason, text)
    return
  }

  // 创建对话记录
  const dialogue = store.addDialogue(text)
  store.setPhase('thinking')

  // 更新状态消息
  if (store.kbId && store.kbApiKey) {
    statusMessage.value = '📚 正在检索知识库...'
  }

  // 调用API获取回答
  await processQuestionStream(
    {
      question: text,
      ark_api_key: store.apiKey,
      model_id: store.modelId,
      kb_id: store.kbId || undefined,
      kb_api_key: store.kbApiKey || undefined
    },
    // onChunk
    (chunk) => {
      store.updateAnswer(dialogue.id, chunk)
      autoScroll()
    },
    // onDone
    (knowledgeUsed) => {
      store.completeDialogue(dialogue.id, knowledgeUsed)
      store.setPhase('listening')
      statusMessage.value = '🎤 正在监听面试官提问...'
      autoScroll()
    },
    // onError
    (error) => {
      store.updateAnswer(dialogue.id, `[错误] ${error}`)
      store.completeDialogue(dialogue.id)
      store.setPhase('listening')
      statusMessage.value = '识别出错，正在重试...'
    }
  )

  store.setPhase('answering')
  statusMessage.value = '🤖 正在生成回答建议...'
}

// 自动滚动到最新对话
function autoScroll() {
  nextTick(() => {
    if (dialoguesContainer.value) {
      dialoguesContainer.value.scrollTop = dialoguesContainer.value.scrollHeight
    }
  })
}

// 结束面试
function confirmEndInterview() {
  showEndConfirm.value = true
}

function endInterview() {
  stopListening()
  stopRecording()
  store.endInterview()
  router.push('/')
}

function cancelEnd() {
  showEndConfirm.value = false
}

// 手动标记/取消标记问题（用户纠错）
function handleManualMark(text: string) {
  if (!text) return
  const dialogue = store.addDialogue(text)
  store.setPhase('thinking')
  statusMessage.value = '🤖 正在生成回答建议...'

  processQuestionStream(
    {
      question: text,
      ark_api_key: store.apiKey,
      model_id: store.modelId,
      kb_id: store.kbId || undefined,
      kb_api_key: store.kbApiKey || undefined
    },
    (chunk) => {
      store.updateAnswer(dialogue.id, chunk)
      autoScroll()
    },
    (knowledgeUsed) => {
      store.completeDialogue(dialogue.id, knowledgeUsed)
      store.setPhase('listening')
      statusMessage.value = '🎤 正在监听面试官提问...'
    },
    (error) => {
      store.updateAnswer(dialogue.id, `[错误] ${error}`)
      store.completeDialogue(dialogue.id)
      store.setPhase('listening')
    }
  )
}

// 获取阶段对应的样式
function getPhaseClass() {
  switch (store.phase) {
    case 'listening': return 'bg-green-50 text-green-700 border-green-200'
    case 'thinking': return 'bg-yellow-50 text-yellow-700 border-yellow-200'
    case 'answering': return 'bg-blue-50 text-blue-700 border-blue-200'
    default: return 'bg-gray-50 text-gray-700 border-gray-200'
  }
}
</script>

<template>
  <div class="flex flex-col h-screen bg-gray-50">
    <!-- 顶部状态栏 -->
    <header class="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shrink-0">
      <div class="flex items-center gap-3">
        <span class="text-xl">🐯</span>
        <h1 class="text-lg font-semibold text-gray-900">面试虎</h1>
      </div>

      <!-- 状态指示器 -->
      <div
        class="flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm"
        :class="getPhaseClass()"
      >
        <span
          class="w-2 h-2 rounded-full"
          :class="{
            'bg-green-500 animate-pulse': store.phase === 'listening',
            'bg-yellow-500 animate-pulse': store.phase === 'thinking',
            'bg-blue-500 animate-pulse': store.phase === 'answering',
            'bg-gray-400': store.phase === 'idle'
          }"
        ></span>
        <span>{{ statusMessage }}</span>
      </div>

      <!-- 结束按钮 -->
      <button
        @click="confirmEndInterview"
        class="btn-danger px-4 py-2 text-sm rounded-lg"
      >
        结束面试
      </button>
    </header>

    <!-- 对话展示区域 -->
    <main
      ref="dialoguesContainer"
      class="flex-1 overflow-y-auto p-4 lg:p-6"
    >
      <!-- 无对话时的提示 -->
      <div
        v-if="store.dialogues.length === 0"
        class="flex flex-col items-center justify-center h-full text-gray-400"
      >
        <div class="text-6xl mb-4">🎤</div>
        <p class="text-lg font-medium mb-2">面试已就绪</p>
        <p class="text-sm">请确保设备麦克风已开启，系统将自动识别面试官提问</p>
      </div>

      <!-- 对话列表 -->
      <template v-for="item in store.dialogues" :key="item.id">
        <DialogueItem :item="item" />
      </template>
    </main>

    <!-- 底部操作栏 -->
    <footer class="bg-white border-t border-gray-200 px-4 py-3 shrink-0">
      <div class="flex items-center gap-3 max-w-4xl mx-auto">
        <!-- 实时识别文本 -->
        <div class="flex-1 px-4 py-2 bg-gray-50 rounded-lg text-sm text-gray-500 min-h-[40px] flex items-center">
          <span v-if="currentText" class="text-gray-400 italic">{{ currentText }}...</span>
          <span v-else class="text-gray-300">等待识别中...</span>
        </div>

        <!-- 导出按钮 -->
        <button
          v-if="store.dialogueCount > 0"
          @click="store.exportDialogues('markdown')"
          class="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          title="导出对话记录"
        >
          📥 导出
        </button>
      </div>
    </footer>

    <!-- 结束确认弹窗 -->
    <div
      v-if="showEndConfirm"
      class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4"
      @click.self="cancelEnd"
    >
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-2">结束面试？</h3>
        <p class="text-sm text-gray-500 mb-6">
          面试对话记录将被保留，你可以在首页查看历史记录。
        </p>
        <div class="flex gap-3">
          <button
            @click="cancelEnd"
            class="flex-1 px-4 py-3 rounded-lg border border-gray-300 text-gray-700 font-medium hover:bg-gray-50 transition-colors"
          >
            继续面试
          </button>
          <button
            @click="endInterview"
            class="flex-1 btn-danger py-3 rounded-lg"
          >
            确认结束
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
