<script setup lang="ts">
import { 
  Mic, 
  Bot, 
  MessageSquare 
} from 'lucide-vue-next'

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
      <div class="dialogue-bubble-user relative">
        <div class="flex items-center gap-2 mb-3">
          <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
            <Mic class="w-4 h-4" />
          </div>
          <span class="text-xs font-medium bg-white/10 px-3 py-1 rounded-full">
            面试官
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
      <div class="dialogue-bubble-ai relative">
        <div class="flex items-center gap-2 mb-3">
          <div class="w-8 h-8 bg-primary/20 rounded-lg flex items-center justify-center">
            <Bot class="w-4 h-4 text-primary" />
          </div>
          <span class="text-xs font-medium text-primary bg-primary/10 px-3 py-1 rounded-full">
            AI建议
          </span>
        </div>

        <div v-if="item.answer" class="text-foreground text-sm leading-relaxed whitespace-pre-wrap">
          {{ item.answer }}
        </div>
        <div v-else class="flex items-center gap-2 text-foreground/50 text-sm">
          <div class="flex gap-1.5">
            <span class="w-2 h-2 bg-primary rounded-full animate-pulse" style="animation-delay: 0ms"></span>
            <span class="w-2 h-2 bg-secondary rounded-full animate-pulse" style="animation-delay: 150ms"></span>
            <span class="w-2 h-2 bg-accent rounded-full animate-pulse" style="animation-delay: 300ms"></span>
          </div>
          <span>正在生成回答...</span>
        </div>
      </div>
    </div>
  </div>
</template>