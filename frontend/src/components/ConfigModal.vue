<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useInterviewStore } from '@/stores/interview'
import { DEFAULT_MODEL_ID, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP } from '@/constants'
import { 
  X, 
  Brain, 
  BookOpen, 
  Key, 
  CheckCircle,
  HelpCircle,
  ExternalLink,
  ChevronRight,
  Upload,
  FileText,
  Settings,
  Database,
  Cloud,
  Trash2,
  FolderOpen,
  RefreshCw,
  Download
} from 'lucide-vue-next'

const props = defineProps<{
  initialProvider?: 'volcengine' | 'local'
}>()

const emit = defineEmits<{
  close: []
  uploaded: []
}>()

const store = useInterviewStore()

const apiKey = ref('')
const kbId = ref('')
const kbApiKey = ref('')
const kbProvider = ref<'volcengine' | 'local'>('volcengine')
const saved = ref(false)
const showHelp = ref(false)

const chunkSize = ref(DEFAULT_CHUNK_SIZE)
const chunkOverlap = ref(DEFAULT_CHUNK_OVERLAP)
const files = ref<File[]>([])
const uploadedDocs = ref<any[]>([])
const uploadLoading = ref(false)
const isLoadingDocs = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const isLocalMode = computed(() => kbProvider.value === 'local')

const helpDocs = [
  {
    question: '大模型 API Key 如何获取？',
    description: '在火山引擎方舟平台创建应用，获取 Bearer Token',
    link: 'https://my.feishu.cn/docx/AzijduiLDoSnsgxsaQsc7O3pnIb?from=from_copylink'
  },
  {
    question: '模型 ID 在哪里查看？',
    description: '方舟控制台模型市场，选择模型后查看模型标识符',
    link: 'https://my.feishu.cn/docx/AzijduiLDoSnsgxsaQsc7O3pnIb?from=from_copylink'
  },
  {
    question: '知识库 ID 如何获取？',
    description: '知识库管理页面，查看知识库基本信息',
    link: 'https://my.feishu.cn/docx/AzijduiLDoSnsgxsaQsc7O3pnIb?from=from_copylink'
  },
  {
    question: '知识库 API Key 如何获取？',
    description: '在火山引擎方舟控制台左侧菜单「知识库」开通服务后，会生成一个纯字母数字格式的 Bearer Token，形如 X7PQPKCV...',
    link: 'https://my.feishu.cn/docx/AzijduiLDoSnsgxsaQsc7O3pnIb?from=from_copylink'
  },
  {
    question: '推荐使用哪些模型？',
    description: 'deepseek-v4-flash（性价比）或 deepseek-v4-pro（高性能）',
    link: 'https://my.feishu.cn/docx/AzijduiLDoSnsgxsaQsc7O3pnIb?from=from_copylink'
  }
]

onMounted(() => {
  apiKey.value = store.apiKey
  kbId.value = store.kbId
  kbApiKey.value = store.kbApiKey
  kbProvider.value = props.initialProvider || (store.kbProvider as 'volcengine' | 'local') || 'volcengine'
  if (isLocalMode.value) {
    loadDocs()
  }
})

async function loadDocs() {
  isLoadingDocs.value = true
  try {
    const response = await fetch('/api/local_kb/list')
    const data = await response.json()
    if (data.code === 0) {
      uploadedDocs.value = data.data
    }
  } catch (error) {
    console.error('加载文档列表失败:', error)
  }
  isLoadingDocs.value = false
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files) {
    files.value = Array.from(target.files)
  }
}

async function uploadFiles() {
  if (files.value.length === 0) return
  
  uploadLoading.value = true
  try {
    const formData = new FormData()
    files.value.forEach(file => {
      formData.append('files', file)
    })
    formData.append('chunk_size', chunkSize.value.toString())
    formData.append('chunk_overlap', chunkOverlap.value.toString())
    
    const response = await fetch('/api/local_kb/upload', {
      method: 'POST',
      body: formData
    })
    
    const data = await response.json()
    if (data.code === 0) {
      saved.value = true
      setTimeout(() => { saved.value = false }, 2000)
      files.value = []
      await loadDocs()
      emit('uploaded')
    } else {
      alert(data.message || '上传失败')
    }
  } catch (error) {
    console.error('上传失败:', error)
    alert('上传失败，请检查后端服务')
  }
  uploadLoading.value = false
}

async function deleteDoc(docId: string) {
  if (!confirm('确定要删除这个文档吗？')) return
  
  try {
    const response = await fetch(`/api/local_kb/delete/${docId}`, {
      method: 'DELETE'
    })
    
    const data = await response.json()
    if (data.code === 0) {
      await loadDocs()
    } else {
      alert(data.message || '删除失败')
    }
  } catch (error) {
    console.error('删除失败:', error)
  }
}

async function clearDocs() {
  if (!confirm('确定要清空所有文档吗？此操作不可恢复！')) return
  
  try {
    const response = await fetch('/api/local_kb/clear', {
      method: 'DELETE'
    })
    
    const data = await response.json()
    if (data.code === 0) {
      uploadedDocs.value = []
    } else {
      alert(data.message || '清空失败')
    }
  } catch (error) {
    console.error('清空失败:', error)
  }
}

function downloadDoc(docId: string) {
  window.open(`/api/local_kb/download/${docId}`, '_blank')
}

function handleUploadClick() {
  fileInput.value?.click()
}

function saveConfig() {
  store.saveConfig({
    apiKey: apiKey.value,
    kbId: kbId.value,
    kbApiKey: kbApiKey.value,
    modelId: DEFAULT_MODEL_ID,
    kbProvider: kbProvider.value
  })
  saved.value = true
  setTimeout(() => {
    saved.value = false
  }, 2000)
  if (isLocalMode.value) {
    loadDocs()
  }
}

function openLink(url: string) {
  window.open(url, '_blank')
}
</script>

<template>
  <div
    class="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4"
    @click.self="emit('close')"
  >
    <div class="glass-card-strong w-full max-w-lg p-7 animate-slide-in-right max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-gradient-to-br from-primary/20 to-secondary/20 rounded-xl flex items-center justify-center border border-primary/30">
            <Key class="w-5 h-5 text-primary" />
          </div>
          <div>
            <h2 class="text-lg font-semibold text-white font-heading">
              {{ props.initialProvider === 'local' ? '上传知识库文档' : '设置' }}
            </h2>
            <p class="text-xs text-foreground/50">
              {{ props.initialProvider === 'local' ? '请先上传文档到本地知识库' : '配置 AI 面试助手' }}
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button
            @click.stop="showHelp = true"
            class="p-2 rounded-lg hover:bg-[rgba(123,58,237,0.1)] transition-colors cursor-pointer z-10"
            title="帮助"
          >
            <HelpCircle class="w-5 h-5 text-foreground/50 hover:text-foreground/70" />
          </button>
          <button
            @click="emit('close')"
            class="p-2 rounded-lg hover:bg-[rgba(123,58,237,0.1)] transition-colors"
          >
            <X class="w-5 h-5 text-foreground/50 hover:text-foreground/70" />
          </button>
        </div>
      </div>

      <div class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-foreground/80 mb-2 flex items-center gap-2">
            <Brain class="w-4 h-4 text-[#60a5fa]" />
            大模型 API Key
          </label>
          <input
            v-model="apiKey"
            type="password"
            placeholder="输入 ARK_API_KEY"
            class="input-glass"
          />
          <p class="text-xs text-foreground/40 mt-1.5">火山引擎方舟平台 Bearer Token</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-foreground/80 mb-2 flex items-center gap-2">
            <Database class="w-4 h-4 text-[#c084fc]" />
            知识库类型
          </label>
          <div class="flex gap-3">
            <button
              @click="kbProvider = 'volcengine'"
              :class="[
                'flex-1 py-3 px-4 rounded-xl border-2 transition-all duration-300 flex items-center justify-center gap-2',
                kbProvider === 'volcengine'
                  ? 'border-[#60a5fa] bg-[rgba(96,165,250,0.15)] text-[#60a5fa] shadow-lg shadow-[rgba(96,165,250,0.2)]'
                  : 'border-[rgba(123,58,237,0.3)] bg-[rgba(30,27,75,0.5)] text-foreground/60 hover:border-[rgba(192,132,252,0.5)]'
              ]"
            >
              <Cloud class="w-4 h-4" />
              <span class="font-medium">火山引擎</span>
            </button>
            <button
              @click="kbProvider = 'local'"
              :class="[
                'flex-1 py-3 px-4 rounded-xl border-2 transition-all duration-300 flex items-center justify-center gap-2',
                kbProvider === 'local'
                  ? 'border-[#c084fc] bg-[rgba(192,132,252,0.15)] text-[#c084fc] shadow-lg shadow-[rgba(192,132,252,0.2)]'
                  : 'border-[rgba(123,58,237,0.3)] bg-[rgba(30,27,75,0.5)] text-foreground/60 hover:border-[rgba(192,132,252,0.5)]'
              ]"
            >
              <FolderOpen class="w-4 h-4" />
              <span class="font-medium">本地知识库</span>
            </button>
          </div>
        </div>

        <div v-if="kbProvider === 'volcengine'" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-foreground/80 mb-2 flex items-center gap-2">
              <BookOpen class="w-4 h-4 text-[#c084fc]" />
              知识库 ID
            </label>
            <input
              v-model="kbId"
              type="text"
              placeholder="输入知识库ID"
              class="input-glass"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-foreground/80 mb-2 flex items-center gap-2">
              <Key class="w-4 h-4 text-[#f472b6]" />
              知识库 API Key
            </label>
            <input
              v-model="kbApiKey"
              type="password"
              placeholder="输入 VIKING_API_KEY"
              class="input-glass"
            />
            <p class="text-xs text-foreground/40 mt-1.5">
              VikingDB 知识库服务的 API Key（纯字母数字格式）
            </p>
          </div>
        </div>

        <div v-if="kbProvider === 'local'" class="bg-[rgba(30,27,75,0.5)] rounded-2xl p-5 border border-[rgba(123,58,237,0.2)]">
          <div class="flex items-center gap-2 mb-4">
            <Upload class="w-4 h-4 text-[#60a5fa]" />
            <span class="text-sm font-medium text-white">上传文档</span>
          </div>
          
          <div 
            class="border-2 border-dashed border-[rgba(123,58,237,0.3)] rounded-xl p-5 text-center hover:border-[rgba(192,132,252,0.5)] transition-all duration-300 cursor-pointer bg-[rgba(123,58,237,0.05)]"
            @click="handleUploadClick"
          >
            <FileText class="w-10 h-10 text-foreground/30 mx-auto mb-3" />
            <p class="text-sm text-foreground/60">
              {{ files.length > 0 ? `已选择 ${files.length} 个文件` : '点击或拖拽上传文档' }}
            </p>
            <p class="text-xs text-foreground/40 mt-1">支持 PDF、TXT、MD、DOCX、JSON</p>
            <input 
              ref="fileInput" 
              type="file" 
              multiple 
              class="hidden"
              @change="handleFileSelect"
            />
          </div>

          <button
            v-if="files.length > 0"
            @click="uploadFiles"
            :disabled="uploadLoading"
            class="w-full mt-4 py-3 bg-gradient-to-r from-[#60a5fa] to-[#c084fc] text-white rounded-xl font-semibold hover:shadow-lg hover:shadow-[rgba(123,58,237,0.3)] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <RefreshCw v-if="uploadLoading" class="w-4 h-4 animate-spin" />
            <span>{{ uploadLoading ? '上传中...' : '上传到本地知识库' }}</span>
          </button>

          <div class="mt-5 pt-5 border-t border-[rgba(123,58,237,0.2)]">
            <div class="flex items-center gap-2 mb-4">
              <Settings class="w-4 h-4 text-[#f472b6]" />
              <span class="text-sm font-medium text-white">切片参数</span>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs text-foreground/60 mb-1.5">切片大小</label>
                <input
                  v-model.number="chunkSize"
                  type="number"
                  min="200"
                  max="2000"
                  class="input-glass"
                  placeholder="500"
                />
                <p class="text-xs text-foreground/40 mt-1">字符数</p>
              </div>
              <div>
                <label class="block text-xs text-foreground/60 mb-1.5">重叠大小</label>
                <input
                  v-model.number="chunkOverlap"
                  type="number"
                  min="0"
                  max="200"
                  class="input-glass"
                  placeholder="50"
                />
                <p class="text-xs text-foreground/40 mt-1">字符数</p>
              </div>
            </div>
          </div>

          <div class="mt-5 pt-5 border-t border-[rgba(123,58,237,0.2)]">
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-2">
                <FolderOpen class="w-4 h-4 text-[#c084fc]" />
                <span class="text-sm font-medium text-white">已上传文档</span>
              </div>
              <button
                v-if="uploadedDocs.length > 0"
                @click="clearDocs"
                class="text-xs text-red-400 hover:text-red-300 transition-colors flex items-center gap-1"
              >
                <Trash2 class="w-3 h-3" />
                清空
              </button>
            </div>
            
            <div v-if="isLoadingDocs" class="text-center py-6">
              <RefreshCw class="w-5 h-5 text-foreground/30 mx-auto animate-spin" />
            </div>
            
            <div v-else-if="uploadedDocs.length === 0" class="text-center py-6">
              <FileText class="w-10 h-10 text-foreground/20 mx-auto mb-3" />
              <p class="text-sm text-foreground/40">暂无上传的文档</p>
            </div>
            
            <div v-else class="space-y-3 max-h-48 overflow-y-auto">
              <div
                v-for="doc in uploadedDocs"
                :key="doc.doc_id"
                class="flex items-center justify-between p-3 bg-[rgba(123,58,237,0.1)] rounded-xl border border-[rgba(123,58,237,0.1)] hover:border-[rgba(192,132,252,0.3)] transition-colors"
              >
                <div>
                  <p class="text-sm text-white">{{ doc.doc_name }}</p>
                  <p class="text-xs text-foreground/40">
                    {{ doc.chunks }} 个切片
                    <span v-if="doc.file_size_bytes"> · {{ (doc.file_size_bytes / 1024).toFixed(1) }} KB</span>
                  </p>
                </div>
                <div class="flex items-center gap-1">
                  <button
                    @click="downloadDoc(doc.doc_id)"
                    class="p-2 rounded-lg hover:bg-blue-500/10 text-foreground/40 hover:text-blue-400 transition-all"
                    title="下载原始文件"
                  >
                    <Download class="w-4 h-4" />
                  </button>
                  <button
                    @click="deleteDoc(doc.doc_id)"
                    class="p-2 rounded-lg hover:bg-red-500/10 text-foreground/40 hover:text-red-400 transition-all"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

      <div class="mt-7 flex gap-4">
        <button @click="emit('close')" class="flex-1 btn-secondary-glass">
          取消
        </button>
        <button @click="saveConfig" class="flex-1 btn-primary-gradient flex items-center justify-center gap-2">
          <CheckCircle v-if="saved" class="w-4 h-4" />
          <span>{{ saved ? '已保存' : '保存配置' }}</span>
        </button>
      </div>
    </div>
  </div>

  <div
    v-if="showHelp"
    class="fixed inset-0 bg-black/70 backdrop-blur-md z-[60] flex items-center justify-center p-4"
    @click.self="showHelp = false"
  >
    <div class="glass-card-strong w-full max-w-md p-7 animate-slide-in-right">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-gradient-to-br from-primary/20 to-secondary/20 rounded-xl flex items-center justify-center border border-primary/30">
            <HelpCircle class="w-5 h-5 text-primary" />
          </div>
          <div>
            <h2 class="text-lg font-semibold text-white font-heading">配置帮助</h2>
            <p class="text-xs text-foreground/50">获取配置相关信息</p>
          </div>
        </div>
        <button
          @click="showHelp = false"
          class="p-2 rounded-lg hover:bg-[rgba(123,58,237,0.1)] transition-colors"
        >
          <X class="w-5 h-5 text-foreground/50 hover:text-foreground/70" />
        </button>
      </div>

      <div class="space-y-3">
        <div
          v-for="(doc, index) in helpDocs"
          :key="index"
          class="group p-4 bg-[rgba(123,58,237,0.05)] rounded-xl border border-[rgba(123,58,237,0.1)] hover:border-[rgba(192,132,252,0.3)] hover:bg-[rgba(123,58,237,0.1)] transition-all duration-300 cursor-pointer"
          @click="openLink(doc.link)"
        >
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-white">{{ doc.question }}</span>
            <ChevronRight class="w-4 h-4 text-foreground/30 group-hover:text-[#c084fc] transition-colors" />
          </div>
          <p class="text-xs text-foreground/50 mt-2">{{ doc.description }}</p>
        </div>
      </div>

      <div class="mt-5 pt-5 border-t border-[rgba(123,58,237,0.2)]">
        <button
          @click="openLink('https://my.feishu.cn/docx/AzijduiLDoSnsgxsaQsc7O3pnIb?from=from_copylink')"
          class="w-full flex items-center justify-center gap-2 py-3 text-sm text-[#c084fc] hover:text-[#818cf8] transition-colors border border-[rgba(192,132,252,0.3)] rounded-xl hover:bg-[rgba(192,132,252,0.1)]"
        >
          <ExternalLink class="w-4 h-4" />
          <span>查看完整配置文档</span>
        </button>
      </div>
    </div>
  </div>
</template>
