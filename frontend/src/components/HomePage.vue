<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import ConfigModal from './ConfigModal.vue'
import TigerLogo from './TigerLogo.vue'
import { 
  Settings, 
  Mic, 
  Database, 
  Zap,
  ArrowRight,
  Sparkles
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
  <div class="flex flex-col items-center justify-center min-h-screen p-6 relative overflow-hidden">
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-primary/5 via-transparent to-accent/5"></div>
      <div class="absolute top-1/3 left-1/4 w-[600px] h-[600px] bg-primary/10 rounded-full blur-[180px] animate-pulse-neon"></div>
      <div class="absolute bottom-1/3 right-1/4 w-[600px] h-[600px] bg-accent/10 rounded-full blur-[180px] animate-pulse-neon" style="animation-delay: 1.5s"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-secondary/5 rounded-full blur-[200px]"></div>
    </div>

    <div class="absolute top-6 right-6 z-10">
      <button
        @click="showConfig = true"
        class="p-3 rounded-xl bg-[rgba(30,27,75,0.6)] backdrop-blur-xl border border-[rgba(123,58,237,0.3)] hover:border-[rgba(192,132,252,0.5)] hover:bg-[rgba(30,27,75,0.8)] transition-all duration-300 group"
        aria-label="设置"
      >
        <Settings class="w-5 h-5 text-foreground/70 group-hover:text-foreground transition-colors" />
      </button>
    </div>

    <div class="text-center max-w-4xl z-10 animate-fade-in-up">
      <div class="mb-10 relative inline-block">
        <TigerLogo :size="180" :radius="85" />
        <div class="absolute -bottom-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-[rgba(30,27,75,0.8)] backdrop-blur-md rounded-full border border-[rgba(251,191,36,0.3)]">
          <span class="text-[#fbbf24] text-sm font-medium flex items-center gap-1">
            <Sparkles class="w-3 h-3" />
            AI 智能助手
          </span>
        </div>
      </div>

      <h1 class="text-6xl font-bold font-heading mb-4 tracking-tight">
        <span class="text-white glow-text-primary">面试虎</span>
        <span class="gradient-text-main"> Interview Tiger</span>
      </h1>
      
      <p class="text-xl text-foreground/70 mb-3 font-medium">
        AI 智能面试助手
      </p>
      
      <p class="text-sm text-foreground/50 mb-12 max-w-xl mx-auto leading-relaxed">
        实时语音识别 · 双知识库支持 · RAG 检索增强 · 个性化面试建议
      </p>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 max-w-3xl mx-auto">
        <div class="glass-card p-6 text-center group">
          <div class="card-icon-wrapper mb-4 group-hover:scale-110 transition-transform duration-300">
            <Mic class="w-7 h-7 text-[#60a5fa]" />
          </div>
          <h3 class="text-lg font-semibold text-white mb-2">实时语音识别</h3>
          <p class="text-sm text-foreground/50">浏览器原生能力，即时转文字</p>
        </div>
        
        <div class="glass-card p-6 text-center group">
          <div class="card-icon-wrapper mb-4 group-hover:scale-110 transition-transform duration-300">
            <Database class="w-7 h-7 text-[#c084fc]" />
          </div>
          <h3 class="text-lg font-semibold text-white mb-2">双知识库支持</h3>
          <p class="text-sm text-foreground/50">火山引擎 / 本地 ChromaDB 自由切换</p>
        </div>
        
        <div class="glass-card p-6 text-center group">
          <div class="card-icon-wrapper mb-4 group-hover:scale-110 transition-transform duration-300">
            <Zap class="w-7 h-7 text-[#f472b6]" />
          </div>
          <h3 class="text-lg font-semibold text-white mb-2">智能分析</h3>
          <p class="text-sm text-foreground/50">基于 STAR 法则生成个性化回答</p>
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
        class="mb-8 p-5 bg-yellow-500/10 border border-yellow-500/30 rounded-2xl text-left max-w-md mx-auto backdrop-blur-sm"
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
        class="btn-primary-gradient text-lg px-12 py-5 flex items-center justify-center gap-3 mx-auto group"
      >
        <span>开始面试</span>
        <ArrowRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
      </button>

      <p class="mt-6 text-xs text-foreground/30">
        API Key 仅存储在浏览器本地，数据安全有保障
      </p>
    </div>

    <ConfigModal v-if="showConfig" @close="showConfig = false" />
  </div>
</template>
