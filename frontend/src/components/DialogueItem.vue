<script setup lang="ts">
// 对话展示组件 - TASK-015
import type { DialogueItem } from '@/stores/interview'

const props = defineProps<{
  item: DialogueItem
}>()
</script>

<template>
  <div class="flex gap-4 mb-6">
    <!-- 左侧：面试官问题 -->
    <div class="flex-1 min-w-0">
      <div class="card border-l-4 border-l-primary-500">
        <div class="flex items-center gap-2 mb-2">
          <span class="text-xs font-medium text-primary-600 bg-primary-50 px-2 py-0.5 rounded-full">
            🎤 面试官
          </span>
          <span class="text-xs text-gray-400">
            {{ new Date(item.timestamp).toLocaleTimeString('zh-CN') }}
          </span>
        </div>
        <p class="text-gray-800 text-sm leading-relaxed">
          {{ item.question }}
        </p>
      </div>
    </div>

    <!-- 右侧：AI回答 -->
    <div class="flex-1 min-w-0">
      <div
        class="card border-l-4 border-l-green-500"
        :class="{ 'animate-pulse': item.status === 'generating' }"
      >
        <div class="flex items-center gap-2 mb-2">
          <span
            class="text-xs font-medium px-2 py-0.5 rounded-full"
            :class="item.status === 'generating'
              ? 'text-yellow-600 bg-yellow-50'
              : 'text-green-600 bg-green-50'"
          >
            {{ item.status === 'generating' ? '🤖 生成中...' : '✅ AI建议' }}
          </span>
          <span
            v-if="item.knowledgeUsed && item.status === 'done'"
            class="text-xs text-blue-500 bg-blue-50 px-2 py-0.5 rounded-full"
          >
            📚 知识库增强
          </span>
        </div>

        <!-- 回答内容 / 打字机效果 -->
        <div v-if="item.answer" class="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap">
          {{ item.answer }}
          <span
            v-if="item.status === 'generating'"
            class="inline-block w-1.5 h-4 bg-primary-500 ml-0.5 animate-pulse align-middle"
          ></span>
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
