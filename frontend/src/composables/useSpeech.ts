// 语音识别 Composable - TASK-005
// 引擎优先级：火山引擎 ASR > 浏览器 Web Speech API
import { ref, onUnmounted } from 'vue'
import { useVolcanoASR } from './useVolcanoASR'

type SpeechRecognition = any
type SpeechRecognitionEvent = any
type SpeechRecognitionErrorEvent = any

export interface SpeechResult {
  text: string
  isFinal: boolean
  confidence: number
}

export function useSpeech() {
  const isListening = ref(false)
  const currentText = ref('')
  const finalText = ref('')
  const error = ref<string | null>(null)

  let recognition: SpeechRecognition | null = null
  let volcanoASR: ReturnType<typeof useVolcanoASR> | null = null
  let useVolcano = false
  let volcanoFailed = false

  function isSupported(): boolean {
    // 至少有一种方式可用
    return !!(window.SpeechRecognition || window.webkitSpeechRecognition) ||
      !!(window.AudioContext || (window as any).webkitAudioContext)
  }

  async function startListening(options: {
    onResult?: (result: SpeechResult) => void
    onError?: (error: string) => void
  } = {}): Promise<boolean> {
    error.value = null
    volcanoFailed = false

    // 优先尝试火山引擎 ASR
    volcanoASR = useVolcanoASR()
    const ok = await volcanoASR.startListening({
      onResult: (r) => {
        currentText.value = volcanoASR!.currentText.value
        finalText.value = volcanoASR!.finalText.value
        isListening.value = volcanoASR!.isListening.value
        options.onResult?.({
          text: r.text,
          isFinal: r.isFinal,
          confidence: r.isFinal ? 1.0 : 0.5,
        })
      },
      onError: (err) => {
        error.value = err
        options.onError?.(err)
        volcanoFailed = true
      },
    })

    if (!ok) {
      volcanoASR = null
      volcanoFailed = true
      error.value = '火山引擎ASR连接失败，回退到浏览器语音识别'
      options.onError?.(error.value)
      // 回退到 Web Speech API
      return startWebSpeech(options)
    }

    useVolcano = true
    isListening.value = true
    return true
  }

  /** Web Speech API 降级方案 */
  function startWebSpeech(options: {
    onResult?: (result: SpeechResult) => void
    onError?: (error: string) => void
  } = {}): boolean {
    if (!(window.SpeechRecognition || window.webkitSpeechRecognition)) {
      error.value = '当前浏览器不支持语音识别，请使用 Chrome 或 Edge 浏览器'
      options.onError?.(error.value)
      return false
    }

    try {
      const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition
      const rec = new SpeechRecognitionAPI()
      recognition = rec

      rec.continuous = true
      rec.interimResults = true
      rec.lang = 'zh-CN'
      rec.maxAlternatives = 1

      rec.onresult = (event: SpeechRecognitionEvent) => {
        let interimText = ''
        let finalChunk = ''

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i]
          if (result.isFinal) {
            finalChunk += result[0].transcript
          } else {
            interimText += result[0].transcript
          }
        }

        if (finalChunk) {
          finalText.value += finalChunk + ' '
        }
        currentText.value = interimText

        options.onResult?.({
          text: finalChunk || interimText,
          isFinal: !!finalChunk,
          confidence: event.results[event.results.length - 1]?.[0]?.confidence || 0
        })
      }

      rec.onerror = (event: SpeechRecognitionErrorEvent) => {
        const errorMsg = `语音识别错误: ${event.error}`
        error.value = errorMsg
        options.onError?.(errorMsg)
        if (event.error === 'network' || event.error === 'no-speech') {
          setTimeout(() => {
            if (isListening.value && recognition) {
              try { recognition.start() } catch {}
            }
          }, 1000)
        }
      }

      rec.onend = () => {
        if (isListening.value && recognition) {
          try { recognition.start() } catch {}
        }
      }

      rec.start()
      isListening.value = true
      error.value = null
      return true
    } catch (e: any) {
      const errMsg = typeof e.message === 'string' ? e.message : '语音识别启动失败'
      error.value = errMsg
      options.onError?.(errMsg)
      return false
    }
  }

  function stopListening() {
    if (volcanoASR) {
      volcanoASR.stopListening()
      volcanoASR = null
    }
    if (recognition) {
      recognition.stop()
      recognition = null
    }
    isListening.value = false
    currentText.value = ''
    useVolcano = false
  }

  function resetText() {
    finalText.value = ''
    currentText.value = ''
  }

  onUnmounted(() => {
    stopListening()
  })

  return {
    isListening,
    currentText,
    finalText,
    error,
    isSupported,
    startListening,
    stopListening,
    resetText,
  }
}
