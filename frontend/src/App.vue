<template>
  <div class="min-h-screen flex items-center justify-center overflow-hidden">
    <BackgroundLayer />
    <!-- 管理后台独立布局，不走手机壳 -->
    <router-view v-if="isAdmin" />
    <template v-else>
      <!-- 手机壳 + AI 面板 整体居中 -->
      <div class="kp-app-row" :class="{ 'kp-app-row--open': kpStore.aiOpen }">
        <div :class="['phone-wrapper', { 'phone-wrapper--editor': hasEditor }]">
          <PhoneShell>
            <router-view />
          </PhoneShell>
        </div>
        <!-- AI 触发按钮（手机壳外右侧） -->
        <button
          v-if="kpStore.kpEnabled && !kpStore.aiOpen && isPractice"
          class="kp-app-trigger"
          @click="kpStore.open(currentQuestionId, null)"
        >
          <span class="kp-app-trigger-text">知识点解析</span>
        </button>
        <!-- AI 面板（手机壳外右侧） -->
        <AiKpPanel
          v-if="kpStore.aiOpen"
          :content="kpStore.aiContent"
          :loading="kpStore.aiLoading"
          :error="kpStore.aiError"
          @close="kpStore.close()"
          @reanalyze="onReanalyze"
          @chat="onChat"
        />
      </div>
    </template>
    <!-- 备案信息 -->
    <div class="fixed bottom-0 left-0 right-0 z-0 pb-1.5 text-center pointer-events-none">
      <p class="text-[11px] text-gray-400 dark:text-gray-500 leading-relaxed">
        <a href="https://beian.miit.gov.cn/" target="_blank" class="pointer-events-auto hover:text-gray-500 dark:hover:text-gray-400 transition">晋ICP备2026004314号-1</a>
        &nbsp;
        <img :src="beianIcon" width="14" height="14" class="inline align-text-bottom opacity-60" />
        <a href="https://beian.mps.gov.cn/#/query/webSearch?code=14108102001175" rel="noreferrer" target="_blank" class="pointer-events-auto hover:text-gray-500 dark:hover:text-gray-400 transition">晋公网安备14108102001175号</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import beianIcon from './assets/beian.png'
import BackgroundLayer from './components/layout/BackgroundLayer.vue'
import PhoneShell from './components/layout/PhoneShell.vue'
import AiKpPanel from './components/practice/AiKpPanel.vue'
import { useThemeStore } from './stores/theme'
import { usePracticeStore } from './stores/practice'
import { useKpStore } from './stores/knowledge_point'

const route = useRoute()
const theme = useThemeStore()
const practice = usePracticeStore()
const kpStore = useKpStore()
const hasEditor = computed(() => practice.editorVisible)
const isAdmin = computed(() => route.path.startsWith('/admin'))
const isPractice = computed(() => route.path.startsWith('/practice'))

const currentQuestionId = ref(null)

// Allow PracticeView to set question context via global event
window.__kpSetQuestion = (qid) => { currentQuestionId.value = qid }

function onReanalyze() {
  if (!confirm('将重新调用 AI 分析当前题目的知识点，是否继续？')) return
  kpStore.reanalyze()
}

async function onChat(messages, resolve, reject) {
  try {
    const reply = await kpStore.chat(messages)
    resolve(reply)
  } catch (e) { reject(e) }
}

onMounted(() => {
  theme.init()
  kpStore.check()
})
</script>

<style scoped>
.kp-app-row {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  gap: 8px;
}
.kp-app-trigger {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  padding: 12px 6px;
  border-radius: 8px;
  border: 1px solid #c4b5fd;
  background: #ede9fe;
  color: #7c3aed;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
  flex-shrink: 0;
  min-height: 140px;
  align-self: stretch;
}
.kp-app-trigger:hover { background: #ddd6fe; }
.kp-app-trigger-text { display: inline-block; letter-spacing: 2px; }
</style>

<style>
.dark .kp-app-trigger {
  background: #1e1b4b;
  border-color: #6d28d9;
  color: #a78bfa;
}
.dark .kp-app-trigger:hover { background: #312e81; }
@media (min-height: 700px) { .kp-app-trigger { min-height: 200px; } }
@media (min-height: 900px) { .kp-app-trigger { min-height: 280px; } }
</style>
