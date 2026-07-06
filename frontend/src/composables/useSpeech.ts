// 语音识别 Composable - 使用浏览器 Web Speech API
import { ref, onUnmounted } from 'vue'

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
  const state = ref<'idle' | 'starting' | 'listening' | 'recognizing' | 'error'>('idle')

  let recognition: SpeechRecognition | null = null
  let restartTimer: ReturnType<typeof setTimeout> | null = null
  let pauseTimer: ReturnType<typeof setTimeout> | null = null
  let stream: MediaStream | null = null
  let currentOptions: {
    onResult?: (result: SpeechResult) => void
    onError?: (error: string) => void
  } = {}
  let isStopping = false
  let isStarting = false
  let generation = 0

  function isSupported(): boolean {
    return !!(window.SpeechRecognition || window.webkitSpeechRecognition)
  }

  async function startListening(options: {
    onResult?: (result: SpeechResult) => void
    onError?: (error: string) => void
  } = {}): Promise<boolean> {
    if (isStarting) {
      return false
    }
    
    error.value = null
    state.value = 'starting'
    isStarting = true
    currentOptions = options

    if (!isSupported()) {
      error.value = '当前浏览器不支持语音识别，请使用 Chrome 或 Edge 浏览器'
      state.value = 'error'
      options.onError?.(error.value)
      isStarting = false
      return false
    }

    try {
      if (!stream) {
        stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
          }
        })
      }

      const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition
      const rec = new SpeechRecognitionAPI()
      generation++
      const currentGeneration = generation
      recognition = rec

      rec.continuous = true
      rec.interimResults = true
      rec.lang = 'zh-CN'
      rec.maxAlternatives = 1

      rec.onresult = (event: SpeechRecognitionEvent) => {
        if (generation !== currentGeneration) return

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
          state.value = 'listening'
        }

        if (interimText) {
          currentText.value = interimText
          state.value = 'recognizing'
          
          if (pauseTimer) clearTimeout(pauseTimer)
          pauseTimer = setTimeout(() => {
            if (generation !== currentGeneration) return
            if (isListening.value && currentText.value.trim()) {
              const pausedResult = pauseRecognition()
              if (pausedResult) {
                options.onResult?.(pausedResult)
              }
            }
          }, 1500)
        } else if (!finalChunk) {
          currentText.value = ''
        }

        const isFinal = !!finalChunk
        options.onResult?.({
          text: finalChunk || interimText,
          isFinal,
          confidence: event.results[event.results.length - 1]?.[0]?.confidence || 0
        })
      }

      rec.onerror = (event: SpeechRecognitionErrorEvent) => {
        if (generation !== currentGeneration) return

        const errorMsg = getErrorMessage(event.error)
        error.value = errorMsg
        state.value = 'error'
        options.onError?.(errorMsg)

        if (event.error === 'network' || event.error === 'no-speech') {
          scheduleRestart(options, currentGeneration)
        }
      }

      rec.onend = () => {
        if (generation !== currentGeneration) return

        if (isStopping) {
          isStopping = false
          state.value = 'idle'
          return
        }

        if (isListening.value && recognition) {
          scheduleRestart(options, currentGeneration)
        }
      }

      try {
        rec.start()
      } catch (startErr: any) {
        if (startErr.name === 'InvalidStateError' || startErr.message?.includes('already started')) {
          try {
            rec.stop()
          } catch {
            // ignore
          }
          await new Promise(resolve => setTimeout(resolve, 100))
          rec.start()
        } else {
          throw startErr
        }
      }

      isListening.value = true
      state.value = 'listening'
      isStarting = false
      return true
    } catch (e: any) {
      const errMsg = typeof e.message === 'string' ? e.message : '语音识别启动失败'
      error.value = errMsg
      state.value = 'error'
      options.onError?.(errMsg)
      isStarting = false
      return false
    }
  }

  function scheduleRestart(options: {
    onResult?: (result: SpeechResult) => void
    onError?: (error: string) => void
  }, expectedGeneration: number) {
    if (!isListening.value) return
    if (restartTimer) clearTimeout(restartTimer)
    restartTimer = setTimeout(() => {
      if (generation !== expectedGeneration) return
      if (!isListening.value || !recognition) return

      try {
        recognition.start()
        state.value = 'listening'
        error.value = null
      } catch (e: any) {
        options.onError?.(e.message || '重启识别失败')
      }
    }, 1000)
  }

  function getErrorMessage(errorCode: string): string {
    const errors: Record<string, string> = {
      'not-allowed': '麦克风权限被拒绝，请在浏览器设置中允许访问麦克风',
      'no-speech': '未检测到语音输入',
      'network': '网络连接异常，正在重试',
      'not-available': '语音识别服务不可用',
      'service-not-allowed': '语音识别服务被禁止',
      'bad-grammar': '语音识别语法错误',
      'language-not-supported': '不支持当前语言',
    }
    return errors[errorCode] || `语音识别错误: ${errorCode}`
  }

  function stopListening() {
    isListening.value = false
    isStopping = true
    if (restartTimer) {
      clearTimeout(restartTimer)
      restartTimer = null
    }
    if (pauseTimer) {
      clearTimeout(pauseTimer)
      pauseTimer = null
    }
    if (recognition) {
      try {
        recognition.stop()
      } catch {
        // ignore
      }
      recognition = null
    }
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      stream = null
    }
    state.value = 'idle'
    currentText.value = ''
    isStopping = false
  }

  function resetText() {
    finalText.value = ''
    currentText.value = ''
  }

  function forceStop() {
    if (!recognition || !isListening.value) return

    const allText = (finalText.value + ' ' + currentText.value).trim()
    
    isListening.value = false
    isStopping = true
    if (restartTimer) {
      clearTimeout(restartTimer)
      restartTimer = null
    }
    
    try {
      recognition.stop()
    } catch {
      // ignore
    }
    recognition = null
    state.value = 'idle'
    isStopping = false

    if (allText) {
      return {
        text: allText,
        isFinal: true,
        confidence: 1.0
      }
    }
    return null
  }

  function pauseRecognition() {
    if (!recognition || !isListening.value) return

    const allText = (finalText.value + ' ' + currentText.value).trim()
    
    isListening.value = false
    isStopping = true
    if (restartTimer) {
      clearTimeout(restartTimer)
      restartTimer = null
    }
    
    try {
      recognition.stop()
    } catch {
      // ignore
    }
    recognition = null
    state.value = 'idle'
    isStopping = false

    if (allText) {
      return {
        text: allText,
        isFinal: true,
        confidence: 1.0
      }
    }
    return null
  }

  async function resumeListening(): Promise<boolean> {
    return startListening(currentOptions)
  }

  onUnmounted(() => {
    stopListening()
  })

  return {
    isListening,
    currentText,
    finalText,
    error,
    state,
    isSupported,
    startListening,
    stopListening,
    resetText,
    forceStop,
    pauseRecognition,
    resumeListening,
  }
}
