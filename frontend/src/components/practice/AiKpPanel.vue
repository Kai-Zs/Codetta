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
    <div class="kp-conversation kp-scroll" ref="convRef">
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
            <div class="kp-msg-body" v-html="renderChatMd(i, m.content)"></div>
          </template>
        </div>

        <!-- 追问加载中 -->
        <div v-if="chatLoading" class="kp-msg assistant">
          <div class="kp-msg-body"><span class="kp-typing">…</span></div>
        </div>
      </template>
    </div>

    <!-- AI 准确性提示 -->
    <div v-if="content" class="kp-disclaimer">AI 生成内容仅供参考，请以教材和教师讲解为准</div>

    <!-- 底部输入区（有内容时始终显示） -->
    <div v-if="content" class="kp-input-row">
      <textarea
        v-model="chatInput"
        @keydown="onInputKeydown" @input="autoResize" placeholder="追问 AI…"
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
import { ref, computed, watch, nextTick, onBeforeUnmount } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js/lib/common'
import 'highlight.js/styles/github-dark.css'
import katex from 'katex'
import 'katex/dist/katex.min.css'
import DOMPurify from 'dompurify'

marked.setOptions({ breaks: true, gfm: true })

function decodeEntities(text) {
  const txt = document.createElement('textarea')
  txt.innerHTML = text
  return txt.value
}

function renderMd(text) {
  try {
    text = decodeEntities(text)
    let html = text.replace(/\$\$([\s\S]*?)\$\$/g, (_, f) => {
      try { return katex.renderToString(f.trim(), { displayMode: true, throwOnError: false }) }
      catch { return `<pre>${f}</pre>` }
    })
    html = html.replace(/\$([^$]+?)\$/g, (_, f) => {
      try { return katex.renderToString(f.trim(), { displayMode: false, throwOnError: false }) }
      catch { return f }
    })
    let mdHtml = marked.parse(html)
    mdHtml = mdHtml.replace(/<pre><code class="language-(\w+)">([\s\S]*?)<\/code><\/pre>/g, (_, lang, code) => {
      const unescaped = decodeEntities(code)
      const valid = hljs.getLanguage(lang)
      const highlighted = valid ? hljs.highlight(unescaped, { language: lang }).value : hljs.highlightAuto(unescaped).value
      return `<pre><span class="kp-code-lang">${lang}</span><code class="hljs">${highlighted}</code></pre>`
    })
    mdHtml = mdHtml.replace(/<a /g, '<a target="_blank" rel="noopener noreferrer" ')
    mdHtml = mdHtml.replace(/(<table>[\s\S]*?<\/table>)/g, '<div class="kp-table-wrap">$1</div>')
    return DOMPurify.sanitize(mdHtml, { ADD_ATTR: ['target'] })
  } catch {
    return text.replace(/</g, '&lt;').replace(/>/g, '&gt;')
  }
}

// 打字机效果：逐字显示文本，每隔 throttleMs 渲染一次 markdown
function useTypewriter(source, throttleMs = 60) {
  const displayed = ref('')
  let timer = null
  let pos = 0
  let stopped = false

  function start(text) {
    stop()
    if (!text) { displayed.value = ''; return }
    stopped = false
    pos = 0
    displayed.value = ''
    const chars = [...text]  // 正确处理 Unicode/emoji
    const step = Math.max(1, Math.floor(chars.length / 80)) || 1  // 约 80 帧完成
    const interval = Math.max(16, Math.min(throttleMs, (chars.length / 80) * throttleMs / step))

    timer = setInterval(() => {
      if (stopped) return
      pos = Math.min(pos + step, chars.length)
      displayed.value = chars.slice(0, pos).join('')
      if (pos >= chars.length) stop()
    }, interval)
  }

  function stop() {
    stopped = true
    if (timer) { clearInterval(timer); timer = null }
  }

  function finish() {
    stop()
    if (source.value) displayed.value = source.value
  }

  return { displayed, start, stop, finish }
}

const props = defineProps({
  content: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const emit = defineEmits(['close', 'reanalyze', 'chat'])

const chatMessages = ref([])
const chatMsgTyping = ref(new Map())  // index → displayed raw text
const chatInput = ref('')
const chatLoading = ref(false)
const convRef = ref(null)
const inputRef = ref(null)

// 初始解析的打字机
const { displayed: typewriterText, start: twStart, stop: twStop, finish: twFinish } = useTypewriter(() => props.content)
const renderedContent = computed(() => typewriterText.value ? renderMd(typewriterText.value) : '')

// content 变化时启动打字机
watch(() => props.content, (val) => {
  if (val) twStart(val)
  else typewriterText.value = ''
})

// 异步打字机辅助
function typeOutMessage(index, text) {
  const chars = [...text]
  let pos = 0
  const step = Math.max(1, Math.floor(chars.length / 60)) || 1
  const map = new Map(chatMsgTyping.value)
  map.set(index, '')
  chatMsgTyping.value = map

  return new Promise(resolve => {
    const timer = setInterval(() => {
      pos = Math.min(pos + step, chars.length)
      const m = new Map(chatMsgTyping.value)
      m.set(index, chars.slice(0, pos).join(''))
      chatMsgTyping.value = m
      if (pos >= chars.length) { clearInterval(timer); resolve() }
    }, 40)
  })
}

function getTypedMsg(index, raw) {
  const typing = chatMsgTyping.value.get(index)
  return typing !== undefined ? typing : raw
}

// 渲染追问 AI 回复
function renderChatMd(index, raw) {
  const text = getTypedMsg(index, raw)
  if (text === raw) return renderMd(raw)  // 已完成
  return renderMd(text)  // 打字中
}

function autoResize() {
  const el = inputRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}

function onInputKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

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
  nextTick(() => autoResize())
  chatLoading.value = true
  scrollBottom()

  try {
    const reply = await new Promise((resolve, reject) => {
      emit('chat', chatMessages.value, resolve, reject)
    })
    const idx = chatMessages.value.length
    chatMessages.value.push({ role: 'assistant', content: reply })
    // 启动打字机动画
    await typeOutMessage(idx, reply)
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
  chatMsgTyping.value = new Map()
  scrollBottom()
})

onBeforeUnmount(() => { twStop() })
</script>

<style scoped>
.kp-panel {
  position: relative;
  z-index: 20;
  flex: 1;
  min-width: 340px;
  max-width: 880px;
  height: calc(100vh - 7rem);
  max-height: calc(100vh - 7rem);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  transition: background 0.3s ease, border-color 0.3s ease;
}
@media (max-width: 768px) {
  .kp-panel {
    width: 100%;
    min-width: 0;
    max-width: none;
    height: 60vh;
    max-height: 60vh;
  }
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

/* AI 准确性提示 */
.kp-disclaimer {
  text-align: center; font-size: 11px; color: #9ca3af;
  padding: 6px 14px 0; flex-shrink: 0; user-select: none;
  transition: color 0.3s ease;
}
.dark .kp-disclaimer { color: #6b7280; }

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
.kp-chat-input::-webkit-scrollbar { width: 4px; }
.kp-chat-input::-webkit-scrollbar-track { background: transparent; }
.kp-chat-input::-webkit-scrollbar-thumb { background: #d4c0f0; border-radius: 2px; }
.dark .kp-chat-input::-webkit-scrollbar-thumb { background: #3a3050; }

.kp-chat-send {
  padding: 8px 16px; border-radius: 8px; font-size: 13px;
  background: #8b5cf6; color: #fff; border: none; cursor: pointer; flex-shrink: 0;
  transition: background 0.3s ease;
}
.kp-chat-send:hover { background: #7c3aed; }
.kp-chat-send:disabled { opacity: 0.5; cursor: not-allowed; }
</style>

<style>
/* 滚动条 — 与手机壳同款 */
.kp-scroll::-webkit-scrollbar { width: 4px; }
.kp-scroll::-webkit-scrollbar-track { background: transparent; }
.kp-scroll::-webkit-scrollbar-thumb { background: #d4c0f0; border-radius: 2px; }
.dark .kp-scroll::-webkit-scrollbar-thumb { background: #3a3050; }

/* ===== markdown 渲染全局样式 ===== */

/* 代码块 */
.kp-msg-body pre {
  background: #1f2937; color: #e5e7eb; padding: 14px 16px; border-radius: 8px;
  overflow-x: auto; font-size: 12px; line-height: 1.6; margin: 10px 0;
  position: relative;
  transition: background 0.3s ease;
}
.dark .kp-msg-body pre { background: #0d1117; }

/* 代码语言标签 */
.kp-code-lang {
  position: absolute; top: 0; right: 0; padding: 2px 8px;
  font-size: 10px; color: #9ca3af; background: rgba(255,255,255,0.08);
  border-radius: 0 8px 0 6px;
  text-transform: uppercase; letter-spacing: 0.5px;
}

/* 表格容器（溢出滚动） */
.kp-table-wrap { overflow-x: auto; margin: 10px 0; }

.kp-msg-body code { font-size: 12px; font-family: 'Fira Code', 'Cascadia Code', 'Consolas', monospace; }

/* 行内代码 */
.kp-msg-body :not(pre) > code {
  background: #f3f4f6; color: #7c3aed; padding: 2px 6px; border-radius: 4px;
  font-size: 12px; white-space: nowrap;
  transition: background 0.3s ease, color 0.3s ease;
}
.dark .kp-msg-body :not(pre) > code { background: #374151; color: #c4b5fd; }

/* 标题 */
.kp-msg-body h1 { font-size: 18px; font-weight: 700; margin: 20px 0 10px; color: #1a1a2e; transition: color 0.3s ease; }
.kp-msg-body h2 { font-size: 16px; font-weight: 600; margin: 16px 0 8px; color: #1a1a2e; transition: color 0.3s ease; }
.kp-msg-body h3 { font-size: 14px; font-weight: 600; margin: 14px 0 6px; color: #1a1a2e; transition: color 0.3s ease; }
.kp-msg-body h4 { font-size: 13px; font-weight: 600; margin: 12px 0 4px; color: #374151; transition: color 0.3s ease; }
.dark .kp-msg-body h1, .dark .kp-msg-body h2, .dark .kp-msg-body h3 { color: #e2e8f0; }
.dark .kp-msg-body h4 { color: #cbd5e1; }

/* 段落 */
.kp-msg-body p { margin-bottom: 8px; }

/* 链接 */
.kp-msg-body a {
  color: #7c3aed; text-decoration: underline; text-underline-offset: 2px;
  transition: color 0.3s ease;
}
.kp-msg-body a:hover { color: #6d28d9; }
.dark .kp-msg-body a { color: #a78bfa; }
.dark .kp-msg-body a:hover { color: #c4b5fd; }

/* 列表 */
.kp-msg-body ul, .kp-msg-body ol { padding-left: 22px; margin: 6px 0 10px; }
.kp-msg-body li { margin-bottom: 4px; }
.kp-msg-body li > ul, .kp-msg-body li > ol { margin-top: 4px; margin-bottom: 0; }

/* 任务列表 */
.kp-msg-body input[type="checkbox"] {
  margin-right: 6px; accent-color: #8b5cf6; vertical-align: middle;
}

/* 引用块 */
.kp-msg-body blockquote {
  border-left: 3px solid #8b5cf6; padding: 6px 12px; margin: 10px 0;
  background: #f9fafb; color: #6b7280; border-radius: 0 6px 6px 0;
  transition: background 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}
.dark .kp-msg-body blockquote { background: #1f2937; color: #9ca3af; border-color: #6d28d9; }
.kp-msg-body blockquote p { margin-bottom: 4px; }

/* 表格 */
.kp-msg-body table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 12px; }
.kp-msg-body th, .kp-msg-body td {
  border: 1px solid #e5e7eb; padding: 8px 10px; text-align: left;
  transition: border-color 0.3s ease;
}
.dark .kp-msg-body th, .dark .kp-msg-body td { border-color: #2d2d4a; }
.kp-msg-body th { background: #f9fafb; font-weight: 600; color: #374151; transition: background 0.3s ease, color 0.3s ease; }
.dark .kp-msg-body th { background: #1f2937; color: #e5e7eb; }
.kp-msg-body tr:nth-child(even) td { background: #f9fafb; transition: background 0.3s ease; }
.dark .kp-msg-body tr:nth-child(even) td { background: #0f172a; }
.kp-msg-body tr:hover td { background: #f3f4f6; transition: background 0.15s ease; }
.dark .kp-msg-body tr:hover td { background: #1e293b; }

/* 分割线 */
.kp-msg-body hr {
  border: none; border-top: 1px solid #e5e7eb; margin: 16px 0;
  transition: border-color 0.3s ease;
}
.dark .kp-msg-body hr { border-color: #2d2d4a; }

/* 图片 */
.kp-msg-body img {
  max-width: 100%; border-radius: 8px; margin: 8px 0;
}

/* 强调 */
.kp-msg-body strong { font-weight: 600; color: #1a1a2e; transition: color 0.3s ease; }
.dark .kp-msg-body strong { color: #f1f5f9; }

/* 键盘标签 */
.kp-msg-body kbd {
  background: #f3f4f6; border: 1px solid #d1d5db; border-bottom-width: 2px;
  border-radius: 4px; padding: 1px 5px; font-size: 11px; font-family: monospace;
  transition: background 0.3s ease, border-color 0.3s ease;
}
.dark .kp-msg-body kbd { background: #1f2937; border-color: #4b5563; color: #e5e7eb; }
</style>
