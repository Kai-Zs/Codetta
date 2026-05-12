<template>
  <div class="flex flex-col flex-1 relative">
    <!-- 顶栏 -->
    <header class="flex justify-between items-center px-3 py-2">
      <button @click="$router.back()" class="text-gray-400 dark:text-gray-500 p-1">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <div class="flex items-center gap-2 text-xs text-gray-400 dark:text-gray-500">
        <span>{{ question?.q_number }}</span>
        <span v-if="!isFromWrong">已做 {{ progress.done }}/{{ progress.total }}</span>
        <span v-if="!isFromWrong && store.mode !== 'filter'">正确率 {{ progress.accuracy }}%</span>
      </div>
      <button @click="showSheet = true" class="text-sm text-purple font-medium">答题卡</button>
    </header>

    <!-- 进度条 -->
    <div class="h-1 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden flex-shrink-0"><div class="h-full bg-purple dark:bg-purple/80 transition-all duration-300 rounded-full" :style="{ width: progressPercent + '%' }" /></div>

    <!-- 翻页 -->
    <div class="flex justify-between px-4 py-1.5">
      <button @click="prevQuestion" :disabled="!hasPrev"
        class="text-xs text-gray-400 dark:text-gray-500 disabled:opacity-30">← 上一题</button>
      <button @click="nextQuestion" :disabled="!hasNext"
        class="text-xs text-gray-400 disabled:opacity-30">下一题 →</button>
    </div>

    <!-- 手机壳内容 -->
    <div class="flex-1 px-4 pb-4 overflow-y-auto">
      <LoadingSpinner v-if="loading" />
      <template v-else-if="question">
        <span class="inline-block bg-purple/5 text-purple text-xs px-2 py-0.5 rounded mb-3">{{ question.type }}</span>
        <h2 class="text-base font-semibold text-gray-800 dark:text-gray-200 mb-2 leading-relaxed">{{ question.title }}</h2>
        <div class="text-sm text-gray-600 dark:text-gray-400 mb-4 leading-relaxed whitespace-pre-wrap" v-html="renderedContent"></div>
        <component
          ref="answerRef"
          :is="typeComp"
          :key="question.id"
          :question="question"
          :options="parsedOptions"
          :blanks="parsedBlanks"
          :correct-answer="question.answer"
          :submitted="submitted"
          :previous-answer="previousAnswer"
          @answer="onAnswer"
        />
      </template>
    </div>

    <div class="px-4 pb-3">
      <button v-if="!isReadonly && !submitted" @click="doSubmit"
        class="w-full py-3 bg-purple text-white rounded-xl font-medium">提交</button>
      <div v-if="submitted && !isFromWrong" class="flex gap-3">
        <button v-if="isPrevWrong" @click="markCorrect"
          class="flex-1 py-2.5 bg-green text-white rounded-lg text-sm font-medium">标为正确</button>
        <button @click="prevQuestion" :disabled="!hasPrev"
          class="flex-1 py-2.5 border border-gray-200 dark:border-gray-700 rounded-lg text-sm disabled:opacity-30 text-gray-500 dark:text-gray-400">上一题</button>
        <button @click="nextQuestion" :disabled="!hasNext"
          class="flex-1 py-2.5 bg-purple text-white rounded-lg text-sm disabled:opacity-30">下一题</button>
      </div>
      <button v-if="submitted && !hasNext && isFromWrong && !isReadonly" @click="backToWrong"
        class="w-full py-2.5 bg-purple text-white rounded-lg text-sm font-medium">返回错题本</button>
    </div>

    <div class="flex items-center justify-between px-4 pb-2">
      <BottomDisclaimer />
      <div class="flex items-center gap-3 ml-4 flex-shrink-0">
        <button @click="theme.toggle()" class="w-4 h-4 text-gray-400 dark:text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition">
          <svg v-if="theme.isDark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
        </button>
        <button @click="showSettings = true" class="w-4 h-4 text-gray-400 dark:text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 15a3 3 0 100-6 3 3 0 000 6z"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
        </button>
      </div>
    </div>

    <!-- 答题卡 -->
    <AnswerSheet :open="showSheet" :items="sheetItems" :currentId="question?.id"
      @close="showSheet = false" @jump="jumpTo" />

    <!-- 编程模式首次弹窗 -->
    <ProgModeModal :open="showProgModeModal" @close="onProgModeClose" />

    <!-- 设置 -->
    <SettingsPanel :open="showSettings" @close="showSettings = false" />

    <!-- 编辑器浮层 -->
    <CodeEditorPanel :visible="showEditor" :question="question" :previous-answer="previousAnswer" @submit="onEditorSubmit" />

    <!-- Toast -->
    <Toast :visible="toastVisible" :msg="toastMsg" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'
import { useAuthStore } from '../stores/auth'
import { usePracticeStore } from '../stores/practice'
import { useSettingsStore } from '../stores/settings'
import { useThemeStore } from '../stores/theme'
import BottomDisclaimer from '../components/layout/BottomDisclaimer.vue'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'
import AnswerSheet from '../components/common/AnswerSheet.vue'
import SettingsPanel from '../components/common/SettingsPanel.vue'
import ProgModeModal from '../components/common/ProgModeModal.vue'
import Toast from '../components/common/Toast.vue'
import SingleChoice from '../components/practice/SingleChoice.vue'
import TrueFalse from '../components/practice/TrueFalse.vue'
import FillBlank from '../components/practice/FillBlank.vue'
import CodeWrite from '../components/practice/CodeWrite.vue'
import CodeReview from '../components/practice/CodeReview.vue'
import CodeEditorPanel from '../components/practice/CodeEditorPanel.vue'
import { useKpStore } from '../stores/knowledge_point'

const route = useRoute()
const router = useRouter()
const store = usePracticeStore()
const settings = useSettingsStore()
const auth = useAuthStore()
const theme = useThemeStore()

const question = ref(null)
const questions = ref([])
const questionIndex = ref(0)
const loading = ref(false)
const submitted = ref(false)
const showSheet = ref(false)
const showSettings = ref(false)
const showProgModeModal = ref(false)
const toastVisible = ref(false)
const toastMsg = ref('')
const answerStatuses = ref({})
const doneInfo = ref({})
const previousAnswer = ref(null)
const progress = reactive({ done: 0, total: 618, accuracy: 0 })
const editorCode = ref('')
const answerRef = ref(null)

const kpStore = useKpStore()

// 解析
const parsedOptions = computed(() => {
  if (!question.value?.options) return []
  try { return JSON.parse(question.value.options) } catch { return [] }
})
const parsedBlanks = computed(() => {
  if (!question.value?.answer_parts) return []
  try { return JSON.parse(question.value.answer_parts) } catch { return [] }
})

const isReadonly = computed(() => route.meta.readonly === true)
const isFromWrong = computed(() => route.path.includes('/wrong'))
const isPrevWrong = computed(() => {
  if (!question.value) return false
  const info = doneInfo.value[question.value.id]
  return info && (info.status === 'incorrect' || info.status === 'partial')
})

const typeComp = computed(() => {
  if (!question.value) return null
  const t = question.value.type
  if (t === '单选题') return SingleChoice
  if (t === '判断题') return TrueFalse
  if (t === '填空题') return FillBlank
  if (t === '编程题') return settings.progMode === 'review' ? CodeReview : CodeWrite
  return null
})

const showEditor = computed(() => {
  return question.value?.type === '编程题' && settings.progMode === 'write' && !isReadonly.value
})
watch(showEditor, (v) => { store.editorVisible = v }, { immediate: true })
onBeforeUnmount(() => { store.editorVisible = false })

const progressPercent = computed(() =>
  questions.value.length ? (questionIndex.value / questions.value.length) * 100 : 0)
const hasPrev = computed(() => questionIndex.value > 0)
const hasNext = computed(() => questionIndex.value < questions.value.length - 1)

const sheetItems = computed(() =>
  questions.value.map((q) => ({ id: q.id, label: q.q_number, chapter: q.chapter, status: answerStatuses.value[q.id] || null })))

const renderedContent = computed(() => {
  if (!question.value?.content) return ''
  return question.value.content.replace(/\n/g, '<br>')
})

function showToast(msg) { toastMsg.value = msg; toastVisible.value = true; setTimeout(() => toastVisible.value = false, 2500) }

function onProgModeClose(mode) {
  showProgModeModal.value = false
  if (mode) {
    settings.progMode = mode
    settings.update()
    if (auth.user?.prog_mode === null) showToast('可在设置中修改编程题模式')
  } else if (auth.user?.prog_mode === null) {
    settings.progMode = 'write'
    settings.update()
    showToast('可在设置中修改编程题模式')
  }
}

function onEditorSubmit(code) {
  editorCode.value = code
  doSubmit()
}

async function doSubmit() {
  if (!answerRef.value) return
  let result
  if (question.value.type === '编程题') {
    if (settings.progMode === 'write') {
      result = await answerRef.value.doSubmit(editorCode.value || answerRef.value?.getCode?.())
    } else {
      result = answerRef.value.doSubmit()
    }
  } else {
    const ans = answerRef.value.getAnswer()
    // 未作答不允许提交
    if (question.value.type === '单选题' || question.value.type === '判断题') {
      if (!ans) { showToast('未作答，不能提交'); return }
    } else if (question.value.type === '填空题') {
      if (!Array.isArray(ans) || ans.every(a => !a.input.trim())) { showToast('未作答，不能提交'); return }
    }
    const correct = question.value.answer || ''
    let isCorrect, partial, answer
    if (question.value.type === '单选题') {
      answer = ans
      isCorrect = ans === correct
    } else if (question.value.type === '判断题') {
      answer = ans
      isCorrect = ans === correct
    } else if (question.value.type === '填空题') {
      const parts = ans // getAnswer returns [{ input, is_correct }]
      answer = parts
      if (answerRef.value && answerRef.value.checkResults) answerRef.value.checkResults()
      partial = parts.some(p => p.is_correct) && !parts.every(p => p.is_correct)
      isCorrect = parts.every(p => p.is_correct)
    }
    result = { isCorrect, partial, answer }
  }
  if (!result) return

  submitted.value = true
  const status = result.isCorrect ? 'correct' : (result.partial ? 'partial' : 'incorrect')
  answerStatuses.value[question.value.id] = status
  doneInfo.value[question.value.id] = { status, user_answer: JSON.stringify(result) }
  // 实时刷新进度
  const statuses = Object.values(answerStatuses.value)
  progress.done = statuses.length
  progress.accuracy = progress.done ? Math.round(statuses.filter(s => s === 'correct').length / progress.done * 100 * 10) / 10 : 0

  try {
    await store.submitAnswer({
      question_id: question.value.id,
      answer_status: status,
      user_answer: JSON.stringify(result),
      mode: store.mode,
      ai_feedback: result.aiFeedback ? JSON.stringify(result.aiFeedback) : null,
      prog_submit_type: settings.progMode === 'review' ? 'review' : 'write',
    })
  } catch { /* error handled silently */ }
}

async function markCorrect() {
  const qid = question.value.id
  try {
    await api.post('/progress/mark-correct', null, { params: { question_id: qid } })
    answerStatuses.value[qid] = 'correct'
    // 同步更新 user_answer 中的 isCorrect，让组件不再高亮错误选项
    const prevData = { ...doneInfo.value[qid] }
    try {
      const parsed = JSON.parse(prevData.user_answer || '{}')
      parsed.isCorrect = true
      prevData.user_answer = JSON.stringify(parsed)
    } catch {}
    prevData.status = 'correct'
    doneInfo.value[qid] = prevData
    previousAnswer.value = { ...previousAnswer.value, isCorrect: true, markedCorrect: true }
    if (question.value.type !== '编程题') answerRef.value?.reset?.()
    const statuses = Object.values(answerStatuses.value)
    progress.accuracy = progress.done ? Math.round(statuses.filter(s => s === 'correct').length / progress.done * 100 * 10) / 10 : 0
    showToast('已标记为正确')
  } catch { showToast('操作失败') }
}

function onAnswer() { /* track user answer selection */ }

async function loadCurrent() {
  if (!questions.value[questionIndex.value]) return
  loading.value = true
  submitted.value = false
  previousAnswer.value = null
  question.value = await store.fetchQuestion(questions.value[questionIndex.value].id)
  loading.value = false

  // 已做题回看（顺序模式只读，筛选模式可重做）
  const prev = doneInfo.value[question.value.id]
  if (prev && !isFromWrong.value && store.mode !== 'filter') {
    submitted.value = true
    try { previousAnswer.value = JSON.parse(prev.user_answer) } catch { previousAnswer.value = prev.user_answer }
  }

  if (question.value.type === '编程题' && auth.user?.prog_mode === null) {
    showProgModeModal.value = true
  }

  // Sync current question ID to App.vue for KP trigger
  window.__kpSetQuestion?.(question.value.id)
}

async function nextQuestion() {
  if (!hasNext.value) return
  questionIndex.value++
  await loadCurrent()
}

async function prevQuestion() {
  if (!hasPrev.value) return
  questionIndex.value--
  await loadCurrent()
}

async function jumpTo(id) {
  const idx = questions.value.findIndex(q => q.id === id)
  if (idx >= 0) { questionIndex.value = idx; await loadCurrent(); showSheet.value = false }
}

function backToWrong() { router.push('/wrong') }

onMounted(async () => {
  try {
    loading.value = true
    await auth.fetchMe()
    settings.init()
    let nextId = null
    try {
      const { data } = await api.get('/progress')
      Object.assign(progress, data)
      nextId = data.next_question_id
      const statusMap = {}
      const infoMap = {}
      for (const [qid, info] of Object.entries(data.done_map || {})) {
        const nid = parseInt(qid)
        statusMap[nid] = info.status
        infoMap[nid] = info
      }
      answerStatuses.value = statusMap
      doneInfo.value = infoMap
    } catch {}

    if (route.path.includes('/filter')) store.setMode('filter')
    else if (route.path.includes('/wrong')) store.setMode('wrong')
    else store.setMode('sequential')

    let params = { per: 1000 }
    if (isFromWrong.value) {
      const ids = route.query.ids
      if (ids) params = { ids }
      else params = { type: '', chapter: '' }
    }
    if (store.mode === 'filter') {
      if (store.filters.type.length) params.type = store.filters.type.join(',')
      if (store.filters.chapter) params.chapter = store.filters.chapter
    }

    const { data } = await api.get('/questions', { params })
    questions.value = data.items
    // sequential 模式：从第一个未做题开始；filter 模式从第一题开始
    if (store.mode === 'sequential' && nextId) {
      const idx = questions.value.findIndex(q => q.id === nextId)
      if (idx >= 0) questionIndex.value = idx
    }
    if (questions.value.length) question.value = await store.fetchQuestion(questions.value[questionIndex.value].id)
  } catch (e) {
    console.error('PracticeView mount error:', e)
  } finally {
    loading.value = false
  }
})
</script>

