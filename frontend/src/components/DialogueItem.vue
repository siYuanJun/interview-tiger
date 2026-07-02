<script setup lang="ts">
interface Dialogue {
  id: string
  question: string
  answer: string
  is_valid: boolean
  rule: string
  created_at: string
}

const props = defineProps<{
  item: Dialogue
}>()

function formatTime(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ''
  }
}
</script>

<template>
  <div class="flex gap-4 mb-6">
    <div class="flex-1 min-w-0">
      <div class="card border-l-4 border-l-primary-500">
        <div class="flex items-center gap-2 mb-2">
          <span class="text-xs font-medium text-primary-600 bg-primary-50 px-2 py-0.5 rounded-full">
            🎤 面试官
          </span>
          <span class="text-xs text-gray-400">
            {{ formatTime(item.created_at) }}
          </span>
          <span
            v-if="item.rule"
            class="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full"
          >
            {{ item.rule }}
          </span>
        </div>
        <p class="text-gray-800 text-sm leading-relaxed">
          {{ item.question }}
        </p>
      </div>
    </div>

    <div class="flex-1 min-w-0">
      <div class="card border-l-4 border-l-green-500">
        <div class="flex items-center gap-2 mb-2">
          <span class="text-xs font-medium text-green-600 bg-green-50 px-2 py-0.5 rounded-full">
            🤖 AI建议
          </span>
        </div>

        <div v-if="item.answer" class="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap">
          {{ item.answer }}
        </div>
        <div v-else class="flex items-center gap-2 text-gray-400 text-sm">
          <div class="flex gap-1">
            <span class="w-2 h-2 bg-gray-300 rounded-full animate-typing" style="animation-delay: 0ms"></span>
            <span class="w-2 h-2 bg-gray-300 rounded-full animate-typing" style="animation-delay: 150ms"></span>
            <span class="w-2 h-2 bg-gray-300 rounded-full animate-typing" style="animation-delay: 300ms"></span>
          </div>
          <span>正在生成回答...</span>
        </div>
      </div>
    </div>
  </div>
</template>