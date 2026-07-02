// 火山引擎流式语音识别 Composable
// 豆包输入法同款引擎 — PCM → WebSocket → 后端 → 火山引擎 ASR
import { ref, onUnmounted } from 'vue'

export interface ASRResult {
  text: string
  isFinal: boolean
}

export function useVolcanoASR() {
  const isListening = ref(false)
  const currentText = ref('')
  const finalText = ref('')
  const error = ref<string | null>(null)

  let audioContext: AudioContext | null = null
  let processorNode: ScriptProcessorNode | null = null
  let mediaStream: MediaStream | null = null
  let ws: WebSocket | null = null
  let wsReady = false
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null

  /** 启动录音 + WebSocket 连接 */
  async function startListening(options: {
    onResult?: (result: ASRResult) => void
    onError?: (error: string) => void
    wsUrl?: string
  } = {}): Promise<boolean> {
    try {
      error.value = null
      finalText.value = ''
      currentText.value = ''

      // 1) 获取麦克风 PCM 流
      mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000,
          channelCount: 1,
        }
      })

      audioContext = new AudioContext({ sampleRate: 16000 })
      const source = audioContext.createMediaStreamSource(mediaStream)

      // ScriptProcessorNode 用于抽取 PCM 原始数据
      // bufferSize=4096 → 约 256ms/帧 @ 16kHz
      processorNode = audioContext.createScriptProcessor(4096, 1, 1)
      source.connect(processorNode)
      processorNode.connect(audioContext.destination)

      // 2) 连接后端 WebSocket（通过 Vite proxy 转发）
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = options.wsUrl || `${protocol}//${window.location.host}/api/asr/stream`
      ws = new WebSocket(wsUrl)
      ws.binaryType = 'arraybuffer'

      ws.onopen = () => {
        wsReady = true
        isListening.value = true
      }

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          if (msg.type === 'result') {
            if (msg.is_final) {
              finalText.value += msg.text
              currentText.value = ''
              options.onResult?.({ text: msg.text, isFinal: true })
            } else {
              currentText.value = msg.text
              options.onResult?.({ text: msg.text, isFinal: false })
            }
          } else if (msg.type === 'error') {
            error.value = msg.message
            options.onError?.(msg.message)
          }
        } catch (e) {
          // 忽略非 JSON 消息
        }
      }

      ws.onerror = () => {
        const errMsg = '语音识别 WebSocket 连接失败'
        error.value = errMsg
        options.onError?.(errMsg)
        // 回退：这里不自动重连，由调用方决定是否 fallback
      }

      ws.onclose = () => {
        wsReady = false
        isListening.value = false
      }

      // 3) 处理音频帧
      processorNode.onaudioprocess = (e) => {
        if (!wsReady || !ws) return
        const inputData = e.inputBuffer.getChannelData(0)
        // Float32 → Int16 PCM
        const pcmBuffer = new Int16Array(inputData.length)
        for (let i = 0; i < inputData.length; i++) {
          const s = Math.max(-1, Math.min(1, inputData[i]))
          pcmBuffer[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
        }
        // Int16Array → Uint8Array → base64
        const uint8 = new Uint8Array(pcmBuffer.buffer)
        const base64 = btoa(String.fromCharCode(...uint8))
        ws.send(JSON.stringify({ type: 'audio', data: base64 }))
      }

      error.value = null
      return true

    } catch (e: any) {
      const errMsg = e.name === 'NotAllowedError'
        ? '麦克风权限被拒绝，请在浏览器设置中允许使用麦克风'
        : e.message || '录音启动失败'
      error.value = errMsg
      options.onError?.(errMsg)
      return false
    }
  }

  /** 停止录音并关闭连接 */
  function stopListening() {
    // 断开 WebSocket
    if (ws) {
      if (wsReady) {
        try { ws.send(JSON.stringify({ type: 'finish' })) } catch {}
      }
      ws.close()
      ws = null
      wsReady = false
    }

    // 断开音频处理
    if (processorNode) {
      processorNode.disconnect()
      processorNode = null
    }
    if (audioContext) {
      audioContext.close()
      audioContext = null
    }
    if (mediaStream) {
      mediaStream.getTracks().forEach(t => t.stop())
      mediaStream = null
    }
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }

    isListening.value = false
    currentText.value = ''
  }

  // 浏览器兼容性检测（Chrome/Edge 支持 AudioContext + ScriptProcessor）
  function isSupported(): boolean {
    return !!(window.AudioContext || (window as any).webkitAudioContext)
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
  }
}
