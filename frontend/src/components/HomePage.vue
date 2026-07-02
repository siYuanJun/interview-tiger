<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import ConfigModal from './ConfigModal.vue'

const router = useRouter()
const showConfig = ref(false)
const checking = ref(true)
const browserSupported = ref(true)

// 浏览器兼容性检测
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
  <div class="flex flex-col items-center justify-center min-h-screen p-6">
    <!-- 设置按钮 -->
    <div class="absolute top-4 right-4">
      <button
        @click="showConfig = true"
        class="p-3 rounded-full hover:bg-gray-200 transition-colors"
        aria-label="设置"
      >
        <svg
          class="w-6 h-6 text-gray-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
          />
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
      </button>
    </div>

    <!-- 主内容 -->
    <div class="text-center max-w-md">
      <!-- Logo图标 -->
      <div class="mb-8">
        <div
          class="w-24 h-24 bg-primary-600 rounded-2xl flex items-center justify-center mx-auto shadow-lg shadow-primary-200"
        >
          <span class="text-5xl">🐯</span>
        </div>
      </div>

      <!-- 标题 -->
      <h1 class="text-4xl font-bold text-gray-900 mb-3">面试虎</h1>
      <p class="text-gray-500 text-lg mb-2">AI 智能面试助手</p>
      <p class="text-gray-400 text-sm mb-8">
        实时语音识别 · 知识库增强 · 个性化回答建议
      </p>

      <!-- 兼容性检测 -->
      <div v-if="checking" class="mb-8">
        <div class="flex items-center justify-center gap-2 text-gray-500">
          <div
            class="w-2 h-2 bg-primary-500 rounded-full animate-pulse"
          ></div>
          <span class="text-sm">检测浏览器兼容性...</span>
        </div>
      </div>

      <div
        v-else-if="!browserSupported"
        class="mb-8 p-4 bg-yellow-50 border border-yellow-200 rounded-xl text-left"
      >
        <p class="text-yellow-800 font-medium text-sm mb-1">
          ⚠️ 浏览器兼容性提示
        </p>
        <p class="text-yellow-700 text-xs">
          当前浏览器可能不完全支持语音功能。建议使用
          <strong>Chrome 80+</strong> 或 <strong>Edge 80+</strong> 浏览器。
        </p>
      </div>

      <!-- 开始面试按钮 -->
      <button
        @click="startInterview"
        class="btn-primary text-lg px-10 py-4 rounded-xl shadow-lg shadow-primary-200 hover:shadow-xl hover:shadow-primary-300 transform hover:-translate-y-0.5 transition-all"
      >
        开始面试
      </button>
    </div>

    <!-- 配置弹窗 -->
    <ConfigModal v-if="showConfig" @close="showConfig = false" />
  </div>
</template>
