<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import ConfigModal from './ConfigModal.vue'
import TigerLogo from './TigerLogo.vue'
import { DEFAULT_KB_PROVIDER } from '@/constants'
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
const checkingLocalKb = ref(false)
const localKbEmpty = ref(false)

function checkBrowserSupport() {
  const hasMediaDevices = !!(navigator.mediaDevices?.getUserMedia)
  const hasSpeech = !!(
    window.SpeechRecognition || window.webkitSpeechRecognition
  )
  browserSupported.value = hasMediaDevices && hasSpeech
  checking.value = false
}

checkBrowserSupport()

async function startInterview() {
  const kbProvider = localStorage.getItem('kb_provider') || DEFAULT_KB_PROVIDER
  
  if (kbProvider === 'local') {
    checkingLocalKb.value = true
    try {
      const response = await fetch('/api/local_kb/stats')
      const data = await response.json()
      if (data.code === 0 && data.data && data.data.total_chunks > 0) {
        router.push('/interview')
      } else {
        localKbEmpty.value = true
        showConfig.value = true
      }
    } catch {
      localKbEmpty.value = true
      showConfig.value = true
    } finally {
      checkingLocalKb.value = false
    }
  } else {
    router.push('/interview')
  }
}

function onConfigClose() {
  showConfig.value = false
  localKbEmpty.value = false
}

function onDocsUploaded() {
  showConfig.value = false
  localKbEmpty.value = false
  router.push('/interview')
}
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-screen p-6 relative overflow-hidden">
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-primary/5 via-transparent to-accent/5"></div>
      <div class="absolute top-1/3 left-1/4 w-[600px] h-[600px] bg-primary/15 rounded-full blur-[180px]"></div>
      <div class="absolute bottom-1/3 right-1/4 w-[600px] h-[600px] bg-accent/15 rounded-full blur-[180px]"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-secondary/10 rounded-full blur-[200px]"></div>
    </div>

    <div class="absolute top-6 right-6 z-10 flex items-center gap-3">
      <a
        href="https://github.com/siYuanJun/interview-tiger"
        target="_blank"
        rel="noopener noreferrer"
        class="p-3 rounded-xl bg-[rgba(30,27,75,0.6)] backdrop-blur-xl border border-[rgba(123,58,237,0.3)] hover:border-[rgba(192,132,252,0.5)] hover:bg-[rgba(30,27,75,0.8)] transition-all duration-300 group"
        aria-label="GitHub"
        title="在 GitHub 上查看源码"
      >
        <svg class="w-5 h-5 text-foreground/70 group-hover:text-foreground transition-colors" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
        </svg>
      </a>
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
        <div class="absolute -bottom-5 left-1/2 -translate-x-1/2 px-5 py-1.5 bg-[rgba(30,27,75,0.8)] backdrop-blur-md rounded-full border border-[rgba(251,191,36,0.3)] whitespace-nowrap">
          <span class="text-[#fbbf24] text-base font-semibold flex items-center gap-1.5">
            <Sparkles class="w-3.5 h-3.5" />
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
        :disabled="checkingLocalKb"
        class="btn-primary-gradient text-lg px-12 py-5 flex items-center justify-center gap-3 mx-auto group disabled:opacity-60 disabled:cursor-not-allowed"
      >
        <span v-if="checkingLocalKb" class="flex items-center gap-2">
          <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
          检查本地知识库...
        </span>
        <template v-else>
          <span>开始面试</span>
          <ArrowRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </template>
      </button>

      <p class="mt-6 text-xs text-foreground/30">
        API Key 仅存储在浏览器本地，数据安全有保障
      </p>
    </div>

    <ConfigModal
      v-if="showConfig"
      :initial-provider="localKbEmpty ? 'local' : undefined"
      @close="onConfigClose"
      @uploaded="onDocsUploaded"
    />
  </div>
</template>
