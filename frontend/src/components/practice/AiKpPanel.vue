<template>
  <div class="kp-panel">
    <!-- 顶栏 -->
    <div class="kp-topbar">
      <h3 class="kp-title">知识点解析</h3>
      <div class="kp-topbar-actions">
        <button v-if="content" @click="$emit('reanalyze')" class="kp-btn-sm">重新解析</button>
        <button @click="$emit('close')" class="kp-btn-close">&#10005;</button>
      </div>
    </div>

    <!-- 对话流（可滚动） -->
    <div class="kp-conversation" ref="convRef">
      <!-- 加载态 -->
      <div v-if="loading" class="kp-state">
        <div class="kp-skeleton">
          <div class="kp-skel-line w-3/4"></div>
          <div class="kp-skel-line w-1/2"></div>
          <div class="kp-skel-line w-full"></div>
          <div class="kp-skel-line w-2/3"></div>
        </div>
        <p class="kp-loading-text">AI 正在分析知识点…</p>
      </div>

      <!-- 错误态 -->
      <div v-else-if="error" class="kp-state">
        <p class="kp-error-text">{{ error }}</p>
        <button @click="$emit('reanalyze')" class="kp-btn-retry">重试</button>
      </div>

      <!-- 空态 -->
      <div v-else-if="!content" class="kp-state">
        <p class="kp-empty-text">点击「AI 知识点解析」按钮获取分析</p>
      </div>

      <!-- 对话消息列表 -->
      <template v-else>
        <!-- 首条 AI 解析 -->
        <div class="kp-msg assistant">
          <div class="kp-msg-body" v-html="renderedContent"></div>
        </div>

        <!-- 追问历史 -->
        <div v-for="(m, i) in chatMessages" :key="i" class="kp-msg" :class="m.role">
          <template v-if="m.role === 'user'">
            <div class="kp-msg-bubble">{{ m.content }}</div>
          </template>
          <template v-else>
            <div class="kp-msg-body" v-html="renderMd(m.content)"></div>
          </template>
        </div>

        <!-- 追问加载中 -->
        <div v-if="chatLoading" class="kp-msg assistant">
          <div class="kp-msg-body"><span class="kp-typing">…</span></div>
        </div>
      </template>
    </div>

    <!-- 底部输入区（有内容时始终显示） -->
    <div v-if="content" class="kp-input-row">
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

const props = defineProps({
  content: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const emit = defineEmits(['close', 'reanalyze', 'chat'])

const chatMessages = ref([])
const chatInput = ref('')
const chatLoading = ref(false)
const convRef = ref(null)
const inputRef = ref(null)

const renderedContent = computed(() => props.content ? renderMd(props.content) : '')

function scrollBottom() {
  nextTick(() => {
    convRef.value?.scrollTo({ top: convRef.value.scrollHeight, behavior: 'smooth' })
  })
}

async function send() {
  const text = chatInput.value.trim()
  if (!text || chatLoading.value) return
  chatMessages.value.push({ role: 'user', content: text })
  chatInput.value = ''
  chatLoading.value = true
  scrollBottom()

  try {
    const reply = await new Promise((resolve, reject) => {
      emit('chat', chatMessages.value, resolve, reject)
    })
    chatMessages.value.push({ role: 'assistant', content: reply })
  } catch {
    chatMessages.value.push({ role: 'assistant', content: '追问失败，请重试。' })
  } finally {
    chatLoading.value = false
    scrollBottom()
  }
}

// 内容变化时清空追问历史
watch(() => props.content, () => {
  chatMessages.value = []
  scrollBottom()
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

/* 对话区 */
.kp-conversation {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #fff;
  transition: background 0.3s ease;
}
.dark .kp-conversation { background: #1a1a2e; }

/* 加载/错误/空态 */
.kp-state {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 40px 20px; text-align: center;
  height: 100%;
}
.kp-loading-text { font-size: 13px; color: #9ca3af; margin-top: 12px; transition: color 0.3s ease; }
.dark .kp-loading-text { color: #6b7280; }
.kp-empty-text { font-size: 13px; color: #9ca3af; transition: color 0.3s ease; }
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

/* 对话消息 - AI */
.kp-msg { margin-bottom: 16px; }
.kp-msg-body {
  font-size: 13px; line-height: 1.7; color: #374151;
  transition: color 0.3s ease;
}
.dark .kp-msg-body { color: #cbd5e1; }

/* 对话消息 - 用户气泡 */
.kp-msg.user { text-align: right; }
.kp-msg-bubble {
  display: inline-block; max-width: 75%; padding: 8px 14px; border-radius: 12px 12px 0 12px;
  font-size: 13px; line-height: 1.6; word-break: break-word;
  background: #8b5cf6; color: #fff;
  text-align: left;
}

/* 加载动画 */
.kp-typing { animation: kp-blink 1s infinite; font-size: 18px; color: #9ca3af; }
@keyframes kp-blink { 50% { opacity: 0; } }

/* 底部输入 */
.kp-input-row {
  display: flex; gap: 8px; padding: 10px 14px;
  border-top: 1px solid #e5e7eb;
  background: #fff; flex-shrink: 0;
  transition: background 0.3s ease, border-color 0.3s ease;
}
.dark .kp-input-row { background: #1a1a2e; border-color: #2d2d4a; }

.kp-chat-input {
  flex: 1; resize: none; padding: 8px 12px; border-radius: 8px;
  border: 1px solid #d1d5db;
  font-size: 13px; line-height: 1.5;
  background: #f9fafb; color: #374151;
  transition: background 0.3s ease, border-color 0.3s ease, color 0.3s ease;
}
.dark .kp-chat-input { background: #111827; border-color: #374151; color: #e5e7eb; }
.kp-chat-input:focus { outline: none; border-color: #8b5cf6; }

.kp-chat-send {
  padding: 8px 16px; border-radius: 8px; font-size: 13px;
  background: #8b5cf6; color: #fff; border: none; cursor: pointer; flex-shrink: 0;
  transition: background 0.3s ease;
}
.kp-chat-send:hover { background: #7c3aed; }
.kp-chat-send:disabled { opacity: 0.5; cursor: not-allowed; }
</style>

<style>
/* markdown 渲染（非 scoped，作用于 v-html 内容） */
.kp-msg-body pre, .kp-markdown pre {
  background: #1f2937; color: #e5e7eb; padding: 12px; border-radius: 8px;
  overflow-x: auto; font-size: 12px; margin: 8px 0;
  transition: background 0.3s ease;
}
.dark .kp-msg-body pre, .dark .kp-markdown pre { background: #0d1117; }
.kp-msg-body code, .kp-markdown code { font-size: 12px; }
.kp-msg-body p code, .kp-markdown p code {
  background: #f3f4f6; color: #374151; padding: 2px 5px; border-radius: 4px;
  transition: background 0.3s ease, color 0.3s ease;
}
.dark .kp-msg-body p code, .dark .kp-markdown p code { background: #374151; color: #e5e7eb; }
.kp-msg-body table, .kp-markdown table { width: 100%; border-collapse: collapse; }
.kp-msg-body th, .kp-msg-body td, .kp-markdown th, .kp-markdown td {
  border: 1px solid #e5e7eb; padding: 6px 8px; font-size: 12px;
  transition: border-color 0.3s ease;
}
.dark .kp-msg-body th, .dark .kp-msg-body td,
.dark .kp-markdown th, .dark .kp-markdown td { border-color: #2d2d4a; }
.kp-msg-body th, .kp-markdown th { background: #f9fafb; transition: background 0.3s ease; }
.dark .kp-msg-body th, .dark .kp-markdown th { background: #1f2937; }
.kp-msg-body h2, .kp-msg-body h3, .kp-markdown h2, .kp-markdown h3 {
  color: #1a1a2e; transition: color 0.3s ease;
}
.dark .kp-msg-body h2, .dark .kp-msg-body h3,
.dark .kp-markdown h2, .dark .kp-markdown h3 { color: #e2e8f0; }
.kp-msg-body h2, .kp-markdown h2 { font-size: 15px; margin: 14px 0 6px; }
.kp-msg-body h3, .kp-markdown h3 { font-size: 14px; margin: 12px 0 4px; }
.kp-msg-body ul, .kp-msg-body ol, .kp-markdown ul, .kp-markdown ol { padding-left: 18px; }
.kp-msg-body li, .kp-markdown li { margin-bottom: 4px; }
.kp-msg-body p, .kp-markdown p { margin-bottom: 8px; }
</style>
