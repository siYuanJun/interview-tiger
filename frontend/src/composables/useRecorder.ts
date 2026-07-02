// 录音 Composable - TASK-004
import { ref, onUnmounted } from 'vue'

export function useRecorder() {
  const isRecording = ref(false)
  const mediaRecorder = ref<MediaRecorder | null>(null)
  const audioStream = ref<MediaStream | null>(null)
  const error = ref<string | null>(null)

  async function startRecording(): Promise<boolean> {
    try {
      error.value = null
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000
        }
      })
      audioStream.value = stream
      mediaRecorder.value = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
          ? 'audio/webm;codecs=opus'
          : 'audio/webm'
      })
      isRecording.value = true
      return true
    } catch (e: any) {
      error.value = e.message || '麦克风权限获取失败'
      console.error('录音启动失败:', e)
      return false
    }
  }

  function stopRecording() {
    if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
      mediaRecorder.value.stop()
    }
    if (audioStream.value) {
      audioStream.value.getTracks().forEach(track => track.stop())
      audioStream.value = null
    }
    mediaRecorder.value = null
    isRecording.value = false
  }

  onUnmounted(() => {
    stopRecording()
  })

  return {
    isRecording,
    mediaRecorder,
    audioStream,
    error,
    startRecording,
    stopRecording
  }
}
