<template>
  <div class="flex flex-col min-h-full relative">
    <!-- 顶栏 -->
    <header class="flex justify-between items-center px-3 py-2">
      <button @click="$router.back()" class="text-gray-400 p-1">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <div class="flex items-center gap-2 text-xs text-gray-400">
        <span>{{ question?.q_number }}</span>
        <button v-if="!isFromWrong" @click="toggleMode"
          class="text-purple text-xs">{{ store.mode === 'random' ? '切顺序' : '切随机' }}</button>
        <span v-if="!isFromWrong">已做 {{ progress.done }}/{{ progress.total }}</span>
        <span v-if="!isFromWrong">正确率 {{ progress.accuracy }}%</span>
      </div>
      <button @click="showSheet = true" class="text-sm text-purple font-medium">答题卡</button>
    </header>

    <!-- 进度条 -->
    <div class="h-1 bg-gray-100"><div class="h-full bg-purple transition-all duration-300" :style="{ width: progressPercent + '%' }" /></div>

    <!-- 翻页 -->
    <div class="flex justify-between px-4 py-1.5">
      <button @click="prevQuestion" :disabled="!hasPrev"
        class="text-xs text-gray-400 disabled:opacity-30">← 上一题</button>
      <button @click="nextQuestion" :disabled="!hasNext"
        class="text-xs text-gray-400 disabled:opacity-30">下一题 →</button>
    </div>

    <!-- 题目区域 -->
    <div class="flex-1 px-4 pb-4 overflow-y-auto">
      <LoadingSpinner v-if="loading" />
      <template v-else-if="question">
        <!-- 题型标签 -->
        <span class="inline-block bg-purple/5 text-purple text-xs px-2 py-0.5 rounded mb-3">{{ question.type }}</span>
        <!-- 标题 + 内容 -->
        <h2 class="text-base font-semibold text-gray-800 mb-2 leading-relaxed">{{ question.title }}</h2>
        <div class="text-sm text-gray-600 mb-4 leading-relaxed whitespace-pre-wrap" v-html="renderedContent"></div>
        <!-- 题型组件 -->
        <component
          ref="answerRef"
          :is="typeComp"
          :key="question.id"
          :question="question"
          :options="parsedOptions"
          :blanks="parsedBlanks"
          :correct-answer="question.answer"
          :submitted="submitted"
          @answer="onAnswer"
        />
      </template>
    </div>

    <!-- 底部操作 -->
    <div class="px-4 pb-3">
      <button v-if="!isReadonly && !submitted" @click="doSubmit"
        class="w-full py-3 bg-purple text-white rounded-xl font-medium">提交</button>
      <div v-if="submitted && !isFromWrong" class="flex gap-3">
        <button @click="prevQuestion" :disabled="!hasPrev"
          class="flex-1 py-2.5 border border-gray-200 rounded-lg text-sm disabled:opacity-30">上一题</button>
        <button @click="nextQuestion" :disabled="!hasNext"
          class="flex-1 py-2.5 bg-purple text-white rounded-lg text-sm disabled:opacity-30">下一题</button>
      </div>
      <button v-if="submitted && !hasNext && isFromWrong && !isReadonly" @click="backToWrong"
        class="w-full py-2.5 bg-purple text-white rounded-lg text-sm font-medium">返回错题本</button>
    </div>

    <!-- 底部 -->
    <div class="flex items-center justify-between px-4 pb-2">
      <BottomDisclaimer />
      <button @click="showSettings = true" class="text-gray-300 hover:text-gray-400 w-4 h-4 ml-4 flex-shrink-0">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
      </button>
    </div>

    <!-- 答题卡 -->
    <AnswerSheet :open="showSheet" :items="sheetItems" :currentId="question?.id"
      @close="showSheet = false" @jump="jumpTo" />

    <!-- 编程模式首次弹窗 -->
    <ProgModeModal :open="showProgModeModal" @close="onProgModeClose" />

    <!-- 设置 -->
    <SettingsPanel :open="showSettings" @close="showSettings = false" />

    <!-- 编辑器浮层 -->
    <CodeEditorPanel :visible="showEditor" :question="question" @submit="onEditorSubmit" />

    <!-- Toast -->
    <Toast :visible="toastVisible" :msg="toastMsg" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'
import { useAuthStore } from '../stores/auth'
import { usePracticeStore } from '../stores/practice'
import { useSettingsStore } from '../stores/settings'
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

const route = useRoute()
const router = useRouter()
const store = usePracticeStore()
const settings = useSettingsStore()
const auth = useAuthStore()

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
const progress = reactive({ done: 0, total: 618, accuracy: 0 })
const editorCode = ref('')
const answerRef = ref(null)

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

const progressPercent = computed(() =>
  questions.value.length ? (questionIndex.value / questions.value.length) * 100 : 0)
const hasPrev = computed(() => questionIndex.value > 0)
const hasNext = computed(() => questionIndex.value < questions.value.length - 1)

const sheetItems = computed(() =>
  questions.value.map((q, i) => ({ id: q.id, label: i + 1, status: answerStatuses.value[q.id] || null })))

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
    if (!ans && ans !== '') return
    const correct = question.value.answer || ''
    let isCorrect, partial
    if (question.value.type === '单选题') {
      isCorrect = ans === correct
    } else if (question.value.type === '判断题') {
      isCorrect = ans === correct
    } else if (question.value.type === '填空题') {
      const parts = ans // getAnswer returns [{ input, is_correct }]
      if (answerRef.value && answerRef.value.checkResults) answerRef.value.checkResults()
      partial = parts.some(p => p.is_correct) && !parts.every(p => p.is_correct)
      isCorrect = parts.every(p => p.is_correct)
    }
    result = { isCorrect, partial }
  }
  if (!result) return

  submitted.value = true
  const status = result.isCorrect ? 'correct' : (result.partial ? 'partial' : 'incorrect')
  answerStatuses.value[question.value.id] = status

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

function onAnswer() { /* track user answer selection */ }

async function loadCurrent() {
  if (!questions.value[questionIndex.value]) return
  loading.value = true
  submitted.value = false
  question.value = await store.fetchQuestion(questions.value[questionIndex.value].id)
  loading.value = false

  if (question.value.type === '编程题' && auth.user?.prog_mode === null) {
    showProgModeModal.value = true
  }
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

function toggleMode() {
  const newMode = store.mode === 'random' ? 'sequential' : 'random'
  store.setMode(newMode)
  if (newMode === 'random') {
    for (let i = questions.value.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [questions.value[i], questions.value[j]] = [questions.value[j], questions.value[i]]
    }
  }
  questionIndex.value = 0
  loadCurrent()
}

onMounted(async () => {
  try {
    loading.value = true
    await auth.fetchMe()
    settings.init()
    try { const { data } = await api.get('/progress'); Object.assign(progress, data) } catch {}

    if (route.path.includes('/random')) store.setMode('random')
    else if (route.path.includes('/wrong')) store.setMode('wrong')
    else store.setMode('sequential')

    let params = {}
    if (isFromWrong.value) {
      const ids = route.query.ids
      if (ids) params = { ids }
      else params = { type: '', chapter: '' }
    }
    if (store.mode === 'random') {
      params.type = store.filters.type.join(',')
      params.chapter = store.filters.chapter
    }

    const { data } = await api.get('/questions', { params })
    questions.value = data.items
    if (store.mode === 'random') {
      for (let i = questions.value.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [questions.value[i], questions.value[j]] = [questions.value[j], questions.value[i]]
      }
    }
    if (questions.value.length) question.value = await store.fetchQuestion(questions.value[0].id)
  } catch (e) {
    console.error('PracticeView mount error:', e)
  } finally {
    loading.value = false
  }
})
</script>
