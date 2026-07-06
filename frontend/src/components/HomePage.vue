<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import ConfigModal from './ConfigModal.vue'
import { 
  Cat, 
  Settings, 
  Mic, 
  Database, 
  Zap,
  ArrowRight
} from 'lucide-vue-next'

const router = useRouter()
const showConfig = ref(false)
const checking = ref(true)
const browserSupported = ref(true)

function checkBrowserSupport() {
  const hasMediaDevices = !!(navigator.mediaDevices?.getUserMedia)
  const hasSpeech = !!(
    window.SpeechRecognition || window.webkitSpeechRecognition
  )
  browserSupported.value = hasMediaDevices && hasSpeech
  checking.value = false
}

checkBrowserSupport()

function startInterview() {
  router.push('/interview')
}
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-screen p-6 bg-background relative overflow-hidden">
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-primary/5 via-transparent to-accent/5"></div>
      <div class="absolute top-1/3 left-1/4 w-[500px] h-[500px] bg-primary/10 rounded-full blur-[150px] animate-pulse-neon"></div>
      <div class="absolute bottom-1/3 right-1/4 w-[500px] h-[500px] bg-accent/10 rounded-full blur-[150px] animate-pulse-neon" style="animation-delay: 1.5s"></div>
    </div>

    <div class="absolute top-4 right-4 z-10">
      <button
        @click="showConfig = true"
        class="p-3 rounded-xl bg-muted/50 backdrop-blur-sm border border-border/30 hover:border-primary/50 hover:bg-muted/70 transition-all"
        aria-label="设置"
      >
        <Settings class="w-5 h-5 text-foreground/70" />
      </button>
    </div>

    <div class="text-center max-w-lg z-10">
      <div class="mb-8 relative">
        <div class="w-28 h-28 bg-gradient-to-br from-primary to-secondary rounded-3xl flex items-center justify-center mx-auto shadow-xl shadow-primary/30 animate-float">
          <Cat class="w-16 h-16 text-white" />
        </div>
        <div class="absolute inset-0 bg-gradient-to-br from-primary/40 to-accent/40 rounded-3xl blur-2xl"></div>
      </div>

      <h1 class="text-5xl font-bold text-gradient-tech font-heading mb-4">面试虎</h1>
      <p class="text-lg text-foreground/70 mb-2">AI 智能面试助手</p>
      <p class="text-sm text-foreground/50 mb-10">实时语音识别 · 知识库增强 · 个性化回答建议</p>

      <div class="grid grid-cols-3 gap-4 mb-10">
        <div class="tech-card-hover p-4 text-center">
          <div class="w-10 h-10 bg-primary/20 rounded-xl flex items-center justify-center mx-auto mb-3">
            <Mic class="w-5 h-5 text-primary" />
          </div>
          <p class="text-xs text-foreground/60">实时语音</p>
        </div>
        <div class="tech-card-hover p-4 text-center">
          <div class="w-10 h-10 bg-accent/20 rounded-xl flex items-center justify-center mx-auto mb-3">
            <Database class="w-5 h-5 text-accent" />
          </div>
          <p class="text-xs text-foreground/60">知识库</p>
        </div>
        <div class="tech-card-hover p-4 text-center">
          <div class="w-10 h-10 bg-secondary/20 rounded-xl flex items-center justify-center mx-auto mb-3">
            <Zap class="w-5 h-5 text-secondary" />
          </div>
          <p class="text-xs text-foreground/60">智能分析</p>
        </div>
      </div>

      <div v-if="checking" class="mb-8">
        <div class="flex items-center justify-center gap-2 text-foreground/50">
          <div
            class="w-2 h-2 bg-primary rounded-full animate-pulse"
          ></div>
          <span class="text-sm">检测浏览器兼容性...</span>
        </div>
      </div>

      <div
        v-else-if="!browserSupported"
        class="mb-8 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-xl text-left"
      >
        <p class="text-yellow-400 font-medium text-sm mb-1">
          浏览器兼容性提示
        </p>
        <p class="text-yellow-400/70 text-xs">
          当前浏览器可能不完全支持语音功能。建议使用
          <strong>Chrome 80+</strong> 或 <strong>Edge 80+</strong> 浏览器。
        </p>
      </div>

      <button
        @click="startInterview"
        class="btn-tech-primary text-lg px-10 py-4 flex items-center justify-center gap-3 animate-glow"
      >
        <span>开始面试</span>
        <ArrowRight class="w-5 h-5" />
      </button>
    </div>

    <ConfigModal v-if="showConfig" @close="showConfig = false" />
  </div>
</template>