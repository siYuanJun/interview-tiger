<script setup lang="ts">
import { computed, onMounted, onUpdated, ref, watch } from 'vue'
import { marked } from 'marked'
import { Check, Copy } from 'lucide-vue-next'

const props = defineProps<{
  content: string
}>()

const containerRef = ref<HTMLElement | null>(null)

function renderMarkdown(text: string): string {
  if (!text) return ''
  return marked.parse(text, { async: false }) as string
}

const renderedHtml = computed(() => renderMarkdown(props.content))

function attachCopyButtons() {
  if (!containerRef.value) return
  const blocks = containerRef.value.querySelectorAll('pre')
  blocks.forEach((block) => {
    if (block.querySelector('.md-copy-btn')) return
    const wrapper = document.createElement('div')
    wrapper.className = 'md-code-wrapper'
    block.parentNode?.insertBefore(wrapper, block)
    wrapper.appendChild(block)

    const btn = document.createElement('button')
    btn.className = 'md-copy-btn'
    btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>'
    btn.title = '复制代码'
    btn.addEventListener('click', () => {
      const code = block.querySelector('code')?.textContent || block.textContent || ''
      navigator.clipboard.writeText(code).then(() => {
        btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>'
        btn.classList.add('copied')
        setTimeout(() => {
          btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>'
          btn.classList.remove('copied')
        }, 2000)
      })
    })
    wrapper.appendChild(btn)
  })
}

onMounted(() => attachCopyButtons())
onUpdated(() => attachCopyButtons())
watch(() => props.content, () => {
  setTimeout(attachCopyButtons, 0)
})
</script>

<template>
  <div ref="containerRef" class="md-content text-foreground text-sm leading-relaxed mt-1" v-html="renderedHtml"></div>
</template>

<style scoped>
.md-content :deep(p) {
  margin-bottom: 0.75rem;
}
.md-content :deep(p:last-child) {
  margin-bottom: 0;
}
.md-content :deep(h1),
.md-content :deep(h2),
.md-content :deep(h3),
.md-content :deep(h4) {
  color: #E2E8F0;
  font-weight: 600;
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}
.md-content :deep(h1) { font-size: 1.25rem; }
.md-content :deep(h2) { font-size: 1.1rem; }
.md-content :deep(h3) { font-size: 1rem; }
.md-content :deep(strong) {
  color: #fbbf24;
  font-weight: 600;
}
.md-content :deep(ul),
.md-content :deep(ol) {
  padding-left: 1.5rem;
  margin-bottom: 0.75rem;
}
.md-content :deep(li) {
  margin-bottom: 0.25rem;
}
.md-content :deep(li::marker) {
  color: #A78BFA;
}
.md-content :deep(blockquote) {
  border-left: 3px solid #7C3AED;
  padding: 0.5rem 1rem;
  margin: 0.75rem 0;
  background: rgba(124, 58, 237, 0.08);
  border-radius: 0 0.5rem 0.5rem 0;
  color: #C4B5FD;
}

.md-code-wrapper {
  position: relative;
  margin: 0.75rem 0;
  border-radius: 0.75rem;
  overflow: hidden;
}
.md-content :deep(pre) {
  background: rgba(15, 15, 35, 0.8);
  border: 1px solid rgba(124, 58, 237, 0.3);
  border-radius: 0.75rem;
  padding: 1rem;
  overflow-x: auto;
  font-size: 0.8rem;
  line-height: 1.6;
  margin: 0;
}
.md-content :deep(code) {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
}
.md-content :deep(pre code) {
  background: none;
  padding: 0;
}
.md-content :deep(:not(pre) > code) {
  background: rgba(124, 58, 237, 0.15);
  padding: 0.15rem 0.4rem;
  border-radius: 0.3rem;
  color: #C4B5FD;
  font-size: 0.8rem;
}

.md-copy-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: rgba(30, 27, 75, 0.8);
  border: 1px solid rgba(124, 58, 237, 0.3);
  border-radius: 0.4rem;
  color: #A78BFA;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s ease;
}
.md-code-wrapper:hover .md-copy-btn {
  opacity: 1;
}
.md-copy-btn:hover {
  background: rgba(124, 58, 237, 0.3);
  color: #E2E8F0;
}
.md-copy-btn.copied {
  color: #34D399;
  border-color: rgba(52, 211, 153, 0.4);
}
</style>
