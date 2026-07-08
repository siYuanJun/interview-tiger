<script setup lang="ts">
import { ref } from 'vue'
import { 
  Mic, 
  Bot, 
  ChevronDown,
  ChevronUp,
  MessageSquare 
} from 'lucide-vue-next'
import MarkdownRenderer from './MarkdownRenderer.vue'

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

const isExpanded = ref(false)
const showExpandButton = ref(false)
const contentRef = ref<HTMLElement | null>(null)

function formatTime(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ''
  }
}

function toggleExpand() {
  isExpanded.value = !isExpanded.value
}

function checkContentHeight() {
  if (contentRef.value) {
    showExpandButton.value = contentRef.value.scrollHeight > 150
  }
}

import { onMounted, nextTick } from 'vue'
onMounted(() => {
  nextTick(checkContentHeight)
})
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
          <span class="text-xs text-white/50">
            {{ formatTime(item.created_at) }}
          </span>
        </div>

        <div v-if="item.answer" class="space-y-3">
          <div class="dialogue-question-title">
            <span class="text-xs font-semibold text-primary/70 uppercase tracking-wider">问题</span>
            <p class="text-foreground/90 font-medium mt-1">{{ item.question }}</p>
          </div>
          
          <div class="dialogue-answer-content" :class="{ expanded: isExpanded }" ref="contentRef">
            <span class="text-xs font-semibold text-accent/70 uppercase tracking-wider">回答</span>
            <MarkdownRenderer :content="item.answer" />
          </div>

          <button 
            v-if="showExpandButton"
            @click="toggleExpand"
            class="w-full flex items-center justify-center gap-2 py-2 text-xs text-primary/60 hover:text-primary transition-colors"
          >
            <ChevronUp v-if="isExpanded" class="w-4 h-4" />
            <ChevronDown v-else class="w-4 h-4" />
            <span>{{ isExpanded ? '收起' : '展开全部' }}</span>
          </button>
        </div>

        <div v-else class="flex items-center justify-center py-8">
          <div class="flex items-center gap-3">
            <div class="flex gap-2">
              <span class="w-3 h-3 bg-primary rounded-full animate-pulse" style="animation-delay: 0ms"></span>
              <span class="w-3 h-3 bg-secondary rounded-full animate-pulse" style="animation-delay: 150ms"></span>
              <span class="w-3 h-3 bg-accent rounded-full animate-pulse" style="animation-delay: 300ms"></span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
