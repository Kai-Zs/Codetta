<template>
  <div class="kp-panel">
    <div class="kp-topbar">
      <h3 class="kp-title">知识点解析</h3>
      <div class="kp-topbar-actions">
        <button v-if="content" @click="$emit('reanalyze')" class="kp-btn-sm">重新解析</button>
        <button @click="$emit('close')" class="kp-btn-close">&#10005;</button>
      </div>
    </div>

    <div class="kp-body" ref="bodyRef">
      <div v-if="loading" class="kp-state">
        <div class="kp-skeleton">
          <div class="kp-skel-line w-3/4"></div>
          <div class="kp-skel-line w-1/2"></div>
          <div class="kp-skel-line w-full"></div>
          <div class="kp-skel-line w-2/3"></div>
        </div>
        <p class="kp-loading-text">AI 正在分析知识点…</p>
      </div>

      <div v-else-if="error" class="kp-state">
        <p class="kp-error-text">{{ error }}</p>
        <button @click="$emit('reanalyze')" class="kp-btn-retry">重试</button>
      </div>

      <div v-else-if="!content" class="kp-state">
        <p class="kp-empty-text">点击「AI 知识点解析」按钮获取分析</p>
      </div>

      <div v-else class="kp-markdown" v-html="renderedHtml"></div>
    </div>

    <div v-if="content" class="kp-chat">
      <div class="kp-chat-messages" ref="chatRef">
        <div v-for="(m, i) in chatMessages" :key="i" class="kp-chat-msg" :class="m.role">
          <div class="kp-chat-bubble" v-html="m.role === 'assistant' ? renderMd(m.content) : escapeHtml(m.content)"></div>
        </div>
        <div v-if="chatLoading" class="kp-chat-msg assistant">
          <div class="kp-chat-bubble"><span class="kp-typing">…</span></div>
        </div>
      </div>
      <div class="kp-chat-input-row">
        <textarea
          v-model="chatInput"
          @keydown.enter.exact.prevent="send"
          @keydown.shift.enter="chatInput += '\n'"
          placeholder="追问 AI…"
          :disabled="chatLoading"
          rows="1"
          ref="inputRef"
          class="kp-chat-input"
        ></textarea>
        <button @click="send" :disabled="chatLoading || !chatInput.trim()" class="kp-chat-send">发送</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js/lib/common'
import 'highlight.js/styles/github-dark.css'
import katex from 'katex'
import 'katex/dist/katex.min.css'
import DOMPurify from 'dompurify'

marked.setOptions({ breaks: true, gfm: true })

function renderMd(text) {
  let html = text.replace(/\$\$([\s\S]*?)\$\$/g, (_, formula) => {
    try { return katex.renderToString(formula.trim(), { displayMode: true, throwOnError: false }) }
    catch { return `<pre>${formula}</pre>` }
  })
  html = html.replace(/\$([^$]+?)\$/g, (_, formula) => {
    try { return katex.renderToString(formula.trim(), { displayMode: false, throwOnError: false }) }
    catch { return formula }
  })
  const mdHtml = marked.parse(html)
  return DOMPurify.sanitize(mdHtml, { ADD_ATTR: ['target'] })
}

function escapeHtml(text) {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

const props = defineProps({
  content: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const emit = defineEmits(['close', 'reanalyze', 'chat'])

const chatMessages = ref([])
const chatInput = ref('')
const chatLoading = ref(false)
const bodyRef = ref(null)
const chatRef = ref(null)
const inputRef = ref(null)

const renderedHtml = computed(() => props.content ? renderMd(props.content) : '')

async function send() {
  const text = chatInput.value.trim()
  if (!text || chatLoading.value) return
  chatMessages.value.push({ role: 'user', content: text })
  chatInput.value = ''
  chatLoading.value = true
  await nextTick()
  chatRef.value?.scrollTo({ top: chatRef.value.scrollHeight, behavior: 'smooth' })

  try {
    const reply = await new Promise((resolve, reject) => {
      emit('chat', chatMessages.value, resolve, reject)
    })
    chatMessages.value.push({ role: 'assistant', content: reply })
  } catch {
    chatMessages.value.push({ role: 'assistant', content: '追问失败，请重试。' })
  } finally {
    chatLoading.value = false
    await nextTick()
    chatRef.value?.scrollTo({ top: chatRef.value.scrollHeight, behavior: 'smooth' })
  }
}

watch(() => props.content, () => {
  chatMessages.value = []
})
</script>

<style scoped>
.kp-panel {
  position: relative;
  z-index: 20;
  flex: 1;
  min-width: 340px;
  max-width: 880px;
  min-height: 500px;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  transition: background 0.3s ease, border-color 0.3s ease;
}
.dark .kp-panel { background: #1a1a2e; border-color: #2d2d4a; }

.kp-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
  transition: border-color 0.3s ease;
}
.dark .kp-topbar { border-color: #2d2d4a; }

.kp-title {
  font-size: 14px; font-weight: 600; margin: 0;
  color: #1a1a2e;
  transition: color 0.3s ease;
}
.dark .kp-title { color: #e2e8f0; }

.kp-topbar-actions { display: flex; gap: 8px; align-items: center; }

.kp-btn-sm {
  font-size: 12px; padding: 4px 10px; border-radius: 6px;
  border: 1px solid #d1d5db;
  background: #f9fafb; cursor: pointer;
  color: #374151;
  transition: background 0.3s ease, border-color 0.3s ease, color 0.3s ease;
}
.dark .kp-btn-sm { background: #374151; border-color: #4b5563; color: #e5e7eb; }

.kp-btn-close {
  font-size: 16px; border: none; background: none; cursor: pointer;
  line-height: 1; padding: 2px; color: #9ca3af;
  transition: color 0.3s ease;
}
.kp-btn-close:hover { color: #374151; }
.dark .kp-btn-close:hover { color: #e5e7eb; }

.kp-body {
  flex: 1; overflow-y: auto; padding: 14px;
  background: #fff;
  transition: background 0.3s ease;
}
.dark .kp-body { background: #1a1a2e; }

.kp-markdown {
  font-size: 13px; line-height: 1.7; color: #374151;
  transition: color 0.3s ease;
}
.dark .kp-markdown { color: #cbd5e1; }

.kp-state {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 40px 20px; text-align: center;
}

.kp-loading-text {
  font-size: 13px; color: #9ca3af; margin-top: 12px;
  transition: color 0.3s ease;
}
.dark .kp-loading-text { color: #6b7280; }

.kp-empty-text {
  font-size: 13px; color: #9ca3af;
  transition: color 0.3s ease;
}
.dark .kp-empty-text { color: #6b7280; }

.kp-error-text { font-size: 13px; color: #ef4444; margin-bottom: 12px; }

.kp-btn-retry {
  padding: 6px 16px; border-radius: 6px; font-size: 13px;
  background: #8b5cf6; color: #fff; border: none; cursor: pointer;
  transition: background 0.3s ease;
}
.kp-btn-retry:hover { background: #7c3aed; }

.kp-skeleton { width: 100%; }

.kp-skel-line {
  height: 14px; background: #e5e7eb; border-radius: 4px; margin-bottom: 10px;
  transition: background 0.3s ease;
}
.dark .kp-skel-line { background: #374151; }

.w-3\/4 { width: 75%; } .w-1\/2 { width: 50%; } .w-full { width: 100%; } .w-2\/3 { width: 66.6%; }

.kp-chat {
  border-top: 1px solid #e5e7eb;
  display: flex; flex-direction: column; flex-shrink: 0;
  transition: border-color 0.3s ease;
}
.dark .kp-chat { border-color: #2d2d4a; }

.kp-chat-messages { flex: 1; max-height: 200px; overflow-y: auto; padding: 8px 14px; }
.kp-chat-msg { margin-bottom: 8px; }
.kp-chat-msg.user { text-align: right; }
.kp-chat-msg.assistant { text-align: left; }

.kp-chat-bubble {
  display: inline-block; max-width: 85%; padding: 6px 10px; border-radius: 10px;
  font-size: 12px; line-height: 1.5; word-break: break-word;
}

.kp-chat-msg.user .kp-chat-bubble { background: #8b5cf6; color: #fff; }

.kp-chat-msg.assistant .kp-chat-bubble {
  background: #f3f4f6; color: #374151;
  transition: background 0.3s ease, color 0.3s ease;
}
.dark .kp-chat-msg.assistant .kp-chat-bubble { background: #1f2937; color: #e5e7eb; }

.kp-typing { animation: kp-blink 1s infinite; }
@keyframes kp-blink { 50% { opacity: 0; } }

.kp-chat-input-row {
  display: flex; gap: 8px; padding: 8px 14px;
  border-top: 1px solid #e5e7eb;
  position: sticky; bottom: 0; background: #fff;
  transition: background 0.3s ease, border-color 0.3s ease;
}
.dark .kp-chat-input-row { background: #1a1a2e; border-color: #2d2d4a; }

.kp-chat-input {
  flex: 1; resize: none; padding: 6px 10px; border-radius: 8px;
  border: 1px solid #d1d5db;
  font-size: 12px; line-height: 1.5;
  background: #f9fafb; color: #374151;
  transition: background 0.3s ease, border-color 0.3s ease, color 0.3s ease;
}
.dark .kp-chat-input { background: #111827; border-color: #374151; color: #e5e7eb; }
.kp-chat-input:focus { outline: none; border-color: #8b5cf6; }

.kp-chat-send {
  padding: 6px 14px; border-radius: 8px; font-size: 12px;
  background: #8b5cf6; color: #fff; border: none; cursor: pointer; flex-shrink: 0;
  transition: background 0.3s ease;
}
.kp-chat-send:hover { background: #7c3aed; }
.kp-chat-send:disabled { opacity: 0.5; cursor: not-allowed; }
</style>

<style>
.kp-markdown pre {
  background: #1f2937; color: #e5e7eb; padding: 12px; border-radius: 8px;
  overflow-x: auto; font-size: 12px; margin: 8px 0;
  transition: background 0.3s ease;
}
.dark .kp-markdown pre { background: #0d1117; }
.kp-markdown code { font-size: 12px; }
.kp-markdown p code {
  background: #f3f4f6; color: #374151; padding: 2px 5px; border-radius: 4px;
  transition: background 0.3s ease, color 0.3s ease;
}
.dark .kp-markdown p code { background: #374151; color: #e5e7eb; }
.kp-markdown table { width: 100%; border-collapse: collapse; }
.kp-markdown th, .kp-markdown td {
  border: 1px solid #e5e7eb; padding: 6px 8px; font-size: 12px;
  transition: border-color 0.3s ease;
}
.dark .kp-markdown th, .dark .kp-markdown td { border-color: #2d2d4a; }
.kp-markdown th { background: #f9fafb; transition: background 0.3s ease; }
.dark .kp-markdown th { background: #1f2937; }
.kp-markdown h2, .kp-markdown h3 { color: #1a1a2e; transition: color 0.3s ease; }
.dark .kp-markdown h2, .dark .kp-markdown h3 { color: #e2e8f0; }
.kp-markdown h2 { font-size: 15px; margin: 14px 0 6px; }
.kp-markdown h3 { font-size: 14px; margin: 12px 0 4px; }
.kp-markdown ul, .kp-markdown ol { padding-left: 18px; }
.kp-markdown li { margin-bottom: 4px; }
.kp-markdown p { margin-bottom: 8px; }
.kp-chat-bubble pre {
  background: rgba(0,0,0,0.06); padding: 6px; border-radius: 6px;
  overflow-x: auto; font-size: 11px; margin: 4px 0;
  transition: background 0.3s ease;
}
.dark .kp-chat-bubble pre { background: rgba(0,0,0,0.3); }
</style>
