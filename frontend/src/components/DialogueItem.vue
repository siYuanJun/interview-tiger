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
  <div class="flex gap-4 mb-6 animate-slide-up">
    <div class="flex-1 min-w-0">
      <div class="glass-card p-4 border-l-4 border-l-accent">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium text-accent bg-accent/20 px-3 py-1 rounded-full">
            🎤 面试官
          </span>
          <span class="text-xs text-white/50">
            {{ formatTime(item.created_at) }}
          </span>
          <span
            v-if="item.rule"
            class="text-xs text-white/60 bg-white/10 px-3 py-1 rounded-full"
          >
            {{ item.rule }}
          </span>
        </div>
        <p class="text-white text-sm leading-relaxed">
          {{ item.question }}
        </p>
      </div>
    </div>

    <div class="flex-1 min-w-0">
      <div class="glass-card p-4 border-l-4 border-l-secondary">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium text-secondary bg-secondary/20 px-3 py-1 rounded-full">
            🤖 AI建议
          </span>
        </div>

        <div v-if="item.answer" class="text-white text-sm leading-relaxed whitespace-pre-wrap">
          {{ item.answer }}
        </div>
        <div v-else class="flex items-center gap-2 text-white/50 text-sm">
          <div class="flex gap-1.5">
            <span class="w-2 h-2 bg-secondary rounded-full animate-pulse" style="animation-delay: 0ms"></span>
            <span class="w-2 h-2 bg-secondary rounded-full animate-pulse" style="animation-delay: 150ms"></span>
            <span class="w-2 h-2 bg-secondary rounded-full animate-pulse" style="animation-delay: 300ms"></span>
          </div>
          <span>正在生成回答...</span>
        </div>
      </div>
    </div>
  </div>
</template>