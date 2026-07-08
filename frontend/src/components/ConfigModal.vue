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
  RefreshCw
} from 'lucide-vue-next'

const emit = defineEmits<{
  close: []
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
    question: '知识库 API Key（AK:SK）是什么？',
    description: '火山引擎访问密钥，在密钥管理页面创建',
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
  kbProvider.value = (store.kbProvider as 'volcengine' | 'local') || 'volcengine'
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
    class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
    @click.self="emit('close')"
  >
    <div class="tech-card w-full max-w-lg p-6 animate-slide-up max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 bg-primary/20 rounded-lg flex items-center justify-center">
            <Key class="w-4 h-4 text-primary" />
          </div>
          <h2 class="text-lg font-semibold text-foreground font-heading">设置</h2>
        </div>
        <div class="flex items-center gap-2">
          <button
            @click.stop="showHelp = true"
            class="p-2 rounded-lg hover:bg-muted/50 transition-colors cursor-pointer z-10"
            title="帮助"
          >
            <HelpCircle class="w-5 h-5 text-foreground/50" />
          </button>
          <button
            @click="emit('close')"
            class="p-2 rounded-lg hover:bg-muted/50 transition-colors"
          >
            <X class="w-5 h-5 text-foreground/50" />
          </button>
        </div>
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
            <Database class="w-4 h-4 text-accent" />
            知识库类型
          </label>
          <div class="flex gap-2">
            <button
              @click="kbProvider = 'volcengine'"
              :class="[
                'flex-1 py-2.5 px-4 rounded-xl border-2 transition-all flex items-center justify-center gap-2',
                kbProvider === 'volcengine'
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-border/50 bg-muted/20 text-foreground/60 hover:border-border'
              ]"
            >
              <Cloud class="w-4 h-4" />
              <span>火山引擎</span>
            </button>
            <button
              @click="kbProvider = 'local'"
              :class="[
                'flex-1 py-2.5 px-4 rounded-xl border-2 transition-all flex items-center justify-center gap-2',
                kbProvider === 'local'
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-border/50 bg-muted/20 text-foreground/60 hover:border-border'
              ]"
            >
              <FolderOpen class="w-4 h-4" />
              <span>本地知识库</span>
            </button>
          </div>
        </div>

        <div v-if="kbProvider === 'volcengine'">
          <label class="block text-sm font-medium text-foreground/80 mb-1.5 flex items-center gap-2">
            <BookOpen class="w-4 h-4 text-accent" />
            知识库 ID
          </label>
          <input
            v-model="kbId"
            type="text"
            placeholder="输入知识库ID"
            class="input-tech"
          />
        </div>

        <div v-if="kbProvider === 'volcengine'">
          <label class="block text-sm font-medium text-foreground/80 mb-1.5 flex items-center gap-2">
            <Key class="w-4 h-4 text-secondary" />
            知识库 API Key
          </label>
          <input
            v-model="kbApiKey"
            type="password"
            placeholder="输入 VIKING_API_KEY"
            class="input-tech"
          />
          <p class="text-xs text-foreground/40 mt-1">
            VikingDB 知识库服务的 API Key（纯字母数字格式）
          </p>
        </div>

        <div v-if="kbProvider === 'local'" class="bg-muted/30 rounded-xl p-4">
          <div class="flex items-center gap-2 mb-4">
            <Upload class="w-4 h-4 text-primary" />
            <span class="text-sm font-medium text-foreground">上传文档</span>
          </div>
          
          <div class="border-2 border-dashed border-border/50 rounded-xl p-4 text-center hover:border-primary/50 transition-colors cursor-pointer"
               @click="$refs.fileInput?.click()">
            <FileText class="w-8 h-8 text-foreground/30 mx-auto mb-2" />
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
            class="w-full mt-3 py-2.5 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <RefreshCw v-if="uploadLoading" class="w-4 h-4 animate-spin" />
            <span>{{ uploadLoading ? '上传中...' : '上传到本地知识库' }}</span>
          </button>

          <div class="mt-4 pt-4 border-t border-border/30">
            <div class="flex items-center gap-2 mb-3">
              <Settings class="w-4 h-4 text-accent" />
              <span class="text-sm font-medium text-foreground">切片参数</span>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs text-foreground/60 mb-1">切片大小</label>
                <input
                  v-model.number="chunkSize"
                  type="number"
                  min="200"
                  max="2000"
                  class="input-tech"
                  placeholder="500"
                />
                <p class="text-xs text-foreground/40 mt-0.5">字符数</p>
              </div>
              <div>
                <label class="block text-xs text-foreground/60 mb-1">重叠大小</label>
                <input
                  v-model.number="chunkOverlap"
                  type="number"
                  min="0"
                  max="200"
                  class="input-tech"
                  placeholder="50"
                />
                <p class="text-xs text-foreground/40 mt-0.5">字符数</p>
              </div>
            </div>
          </div>

          <div class="mt-4 pt-4 border-t border-border/30">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-2">
                <FolderOpen class="w-4 h-4 text-accent" />
                <span class="text-sm font-medium text-foreground">已上传文档</span>
              </div>
              <button
                v-if="uploadedDocs.length > 0"
                @click="clearDocs"
                class="text-xs text-red-500 hover:text-red-600 transition-colors flex items-center gap-1"
              >
                <Trash2 class="w-3 h-3" />
                清空
              </button>
            </div>
            
            <div v-if="isLoadingDocs" class="text-center py-4">
              <RefreshCw class="w-5 h-5 text-foreground/30 mx-auto animate-spin" />
            </div>
            
            <div v-else-if="uploadedDocs.length === 0" class="text-center py-4">
              <FileText class="w-8 h-8 text-foreground/30 mx-auto mb-2" />
              <p class="text-sm text-foreground/40">暂无上传的文档</p>
            </div>
            
            <div v-else class="space-y-2 max-h-40 overflow-y-auto">
              <div
                v-for="doc in uploadedDocs"
                :key="doc.doc_id"
                class="flex items-center justify-between p-3 bg-muted/20 rounded-lg"
              >
                <div>
                  <p class="text-sm text-foreground">{{ doc.doc_name }}</p>
                  <p class="text-xs text-foreground/40">{{ doc.chunks }} 个切片</p>
                </div>
                <button
                  @click="deleteDoc(doc.doc_id)"
                  class="p-1.5 rounded-lg hover:bg-red-500/10 text-foreground/40 hover:text-red-500 transition-colors"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
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

  <div
    v-if="showHelp"
    class="fixed inset-0 bg-black/80 backdrop-blur-sm z-[60] flex items-center justify-center p-4"
    @click.self="showHelp = false"
  >
    <div class="tech-card w-full max-w-md p-6 animate-slide-up">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 bg-primary/20 rounded-lg flex items-center justify-center">
            <HelpCircle class="w-4 h-4 text-primary" />
          </div>
          <h2 class="text-lg font-semibold text-foreground font-heading">配置帮助</h2>
        </div>
        <button
          @click="showHelp = false"
          class="p-2 rounded-lg hover:bg-muted/50 transition-colors"
        >
          <X class="w-5 h-5 text-foreground/50" />
        </button>
      </div>

      <div class="space-y-2">
        <div
          v-for="(doc, index) in helpDocs"
          :key="index"
          class="group p-4 bg-muted/20 rounded-xl hover:bg-muted/40 transition-colors cursor-pointer"
          @click="openLink(doc.link)"
        >
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-foreground/90">{{ doc.question }}</span>
            <ChevronRight class="w-4 h-4 text-foreground/30 group-hover:text-primary transition-colors" />
          </div>
          <p class="text-xs text-foreground/50 mt-1.5">{{ doc.description }}</p>
        </div>
      </div>

      <div class="mt-4 pt-4 border-t border-border/30">
        <button
          @click="openLink('https://my.feishu.cn/docx/AzijduiLDoSnsgxsaQsc7O3pnIb?from=from_copylink')"
          class="w-full flex items-center justify-center gap-2 text-sm text-primary/80 hover:text-primary transition-colors"
        >
          <ExternalLink class="w-4 h-4" />
          <span>查看完整配置文档</span>
        </button>
      </div>
    </div>
  </div>
</template>
