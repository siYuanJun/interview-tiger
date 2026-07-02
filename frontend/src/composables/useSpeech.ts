// 语音识别 Composable - TASK-005
import { ref, onUnmounted } from 'vue'

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

  function isSupported(): boolean {
    return !!(window.SpeechRecognition || window.webkitSpeechRecognition)
  }

  function startListening(options: {
    onResult?: (result: SpeechResult) => void
    onError?: (error: string) => void
  } = {}): boolean {
    if (!isSupported()) {
      error.value = '当前浏览器不支持语音识别，请使用 Chrome 或 Edge 浏览器'
      options.onError?.(error.value)
      return false
    }

    try {
      const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition
      recognition = new SpeechRecognitionAPI()

      // 持续识别模式
      recognition.continuous = true
      // 返回临时结果
      recognition.interimResults = true
      // 中文识别
      recognition.lang = 'zh-CN'
      // 最大替代结果数
      recognition.maxAlternatives = 1

      recognition.onresult = (event: SpeechRecognitionEvent) => {
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

        // 累积最终结果
        if (finalChunk) {
          finalText.value += finalChunk + ' '
        }

        currentText.value = interimText

        const speechResult: SpeechResult = {
          text: finalChunk || interimText,
          isFinal: !!finalChunk,
          confidence: event.results[event.results.length - 1]?.[0]?.confidence || 0
        }

        options.onResult?.(speechResult)
      }

      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        const errorMsg = `语音识别错误: ${event.error}`
        error.value = errorMsg
        console.error(errorMsg, event)
        options.onError?.(errorMsg)

        // 网络错误或无法识别时尝试自动重启
        if (event.error === 'network' || event.error === 'no-speech') {
          setTimeout(() => {
            if (isListening.value && recognition) {
              try {
                recognition.start()
              } catch (e) {
                // 忽略重复启动错误
              }
            }
          }, 1000)
        }
      }

      recognition.onend = () => {
        // 如果仍在监听状态，自动重启
        if (isListening.value && recognition) {
          try {
            recognition.start()
          } catch (e) {
            // 忽略重复启动错误
          }
        }
      }

      recognition.start()
      isListening.value = true
      error.value = null
      return true
    } catch (e: any) {
      error.value = e.message || '语音识别启动失败'
      console.error('语音识别启动失败:', e)
      options.onError?.(error.value)
      return false
    }
  }

  function stopListening() {
    if (recognition) {
      recognition.stop()
      recognition = null
    }
    isListening.value = false
    currentText.value = ''
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
    resetText
  }
}
