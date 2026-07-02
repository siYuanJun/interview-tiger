<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useInterviewStore } from '@/stores/interview'
import { DEFAULT_MODEL_ID } from '@/constants'
import { 
  X, 
  Brain, 
  BookOpen, 
  Key, 
  Bot,
  CheckCircle
} from 'lucide-vue-next'

const emit = defineEmits<{
  close: []
}>()

const store = useInterviewStore()

const apiKey = ref('')
const kbId = ref('')
const kbApiKey = ref('')
const modelId = ref(DEFAULT_MODEL_ID)
const saved = ref(false)

onMounted(() => {
  apiKey.value = store.apiKey
  kbId.value = store.kbId
  kbApiKey.value = store.kbApiKey
  modelId.value = store.modelId
})

function saveConfig() {
  store.saveConfig({
    apiKey: apiKey.value,
    kbId: kbId.value,
    kbApiKey: kbApiKey.value,
    modelId: modelId.value
  })
  saved.value = true
  setTimeout(() => {
    saved.value = false
  }, 2000)
}
</script>

<template>
  <div
    class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
    @click.self="emit('close')"
  >
    <div class="tech-card w-full max-w-md p-6 animate-slide-up">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 bg-primary/20 rounded-lg flex items-center justify-center">
            <Key class="w-4 h-4 text-primary" />
          </div>
          <h2 class="text-lg font-semibold text-foreground font-heading">设置</h2>
        </div>
        <button
          @click="emit('close')"
          class="p-2 rounded-lg hover:bg-muted/50 transition-colors"
        >
          <X class="w-5 h-5 text-foreground/50" />
        </button>
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-foreground/80 mb-1.5 flex items-center gap-2">
            <Brain class="w-4 h-4 text-primary" />
            大模型 API Key
          </label>
          <input
            v-model="apiKey"
            type="password"
            placeholder="输入 ARK_API_KEY"
            class="input-tech"
          />
          <p class="text-xs text-foreground/40 mt-1">火山引擎方舟平台 Bearer Token</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-foreground/80 mb-1.5 flex items-center gap-2">
            <BookOpen class="w-4 h-4 text-accent" />
            知识库 ID
          </label>
          <input
            v-model="kbId"
            type="text"
            placeholder="输入知识库ID（如 siyuan_jianli）"
            class="input-tech"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-foreground/80 mb-1.5 flex items-center gap-2">
            <Key class="w-4 h-4 text-secondary" />
            知识库 API Key（AK:SK）
          </label>
          <input
            v-model="kbApiKey"
            type="password"
            placeholder="AK:SK 格式的知识库密钥"
            class="input-tech"
          />
          <p class="text-xs text-foreground/40 mt-1">
            格式：AccessKey:SecretKey（冒号分隔）
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-foreground/80 mb-1.5 flex items-center gap-2">
            <Bot class="w-4 h-4 text-primary" />
            模型 ID
          </label>
          <input
            v-model="modelId"
            type="text"
            placeholder="deepseek-v4-flash-260425"
            class="input-tech"
          />
          <p class="text-xs text-foreground/40 mt-1">
            推荐 deepseek-v4-flash-260425（高性价比）或 deepseek-v4-pro
          </p>
        </div>
      </div>

      <div class="mt-6 flex gap-3">
        <button @click="emit('close')" class="flex-1 btn-tech-secondary">
          取消
        </button>
        <button @click="saveConfig" class="flex-1 btn-tech-primary flex items-center justify-center gap-2">
          <CheckCircle v-if="saved" class="w-4 h-4" />
          <span>{{ saved ? '已保存' : '保存配置' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>