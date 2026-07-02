<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useInterviewStore } from '@/stores/interview'

const emit = defineEmits<{
  close: []
}>()

const store = useInterviewStore()

const apiKey = ref('')
const kbId = ref('')
const kbApiKey = ref('')
const modelId = ref('doubao-seed-2-1-pro-260628')
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
    class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4"
    @click.self="emit('close')"
  >
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-lg font-semibold text-gray-900">⚙️ 设置</h2>
        <button
          @click="emit('close')"
          class="p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="space-y-4">
        <!-- 大模型API Key -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">
            🧠 大模型 API Key
          </label>
          <input
            v-model="apiKey"
            type="password"
            placeholder="输入 ARK_API_KEY"
            class="input-field"
          />
          <p class="text-xs text-gray-400 mt-1">火山引擎方舟平台 Bearer Token</p>
        </div>

        <!-- 知识库ID -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">
            📚 知识库 ID
          </label>
          <input
            v-model="kbId"
            type="text"
            placeholder="输入知识库ID（如 kb-xxx）"
            class="input-field"
          />
        </div>

        <!-- 知识库API Key (AK:SK) -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">
            🔑 知识库 API Key（AK:SK）
          </label>
          <input
            v-model="kbApiKey"
            type="password"
            placeholder="AK:SK 格式的知识库密钥"
            class="input-field"
          />
          <p class="text-xs text-gray-400 mt-1">
            格式：AccessKey:SecretKey（冒号分隔）
          </p>
        </div>

        <!-- 模型ID -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">
            🤖 模型 ID
          </label>
          <input
            v-model="modelId"
            type="text"
            placeholder="doubao-seed-2-1-pro-260628"
            class="input-field"
          />
          <p class="text-xs text-gray-400 mt-1">
            推荐 doubao-seed-2-1-pro-260628 或 doubao-seed-2-0-mini-260215
          </p>
        </div>
      </div>

      <div class="mt-6 flex gap-3">
        <button @click="emit('close')" class="flex-1 px-4 py-3 rounded-lg border border-gray-300 text-gray-700 font-medium hover:bg-gray-50 transition-colors">
          取消
        </button>
        <button @click="saveConfig" class="flex-1 btn-primary">
          <span v-if="!saved">保存配置</span>
          <span v-else>✅ 已保存</span>
        </button>
      </div>
    </div>
  </div>
</template>
