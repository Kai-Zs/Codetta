<template>
  <div class="min-h-screen bg-bg flex flex-col">
    <header class="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-white">
      <button @click="$router.back()" class="text-gray-500">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <div class="flex items-center gap-3 text-xs text-gray-400">
        <span>{{ question?.q_number }}</span>
        <button v-if="!isFromWrong" @click="toggleMode" class="text-purple text-xs">{{ store.mode === 'random' ? '切顺序' : '切随机' }}</button>
        <span v-if="!isFromWrong">已做 {{ progress.done }}/{{ progress.total }}</span>
        <span v-if="!isFromWrong">正确率 {{ progress.accuracy }}%</span>
      </div>
      <button @click="showSheet=true" class="text-sm text-purple">答题卡</button>
    </header>
    <div class="h-1 bg-gray-100"><div class="h-full bg-purple transition-all duration-300" :style="{width: progressPercent+'%'}"/></div>
    <div class="px-4 py-3">
      <span class="text-xs text-purple font-medium">{{ question?.type }}</span>
      <h2 class="text-base font-medium text-gray-800 mt-1">{{ question?.title }}</h2>
    </div>
    <div class="flex-1 px-4 pb-24">
      <LoadingSpinner v-if="loading" :show="true" />
      <component v-else-if="question" :is="typeComp" :question="question" ref="answerRef" @submit="onSubmit" />
    </div>
    <footer class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 px-4 py-3 flex gap-3">
      <button v-if="!isReadonly" @click="prevQuestion" :disabled="!hasPrev" class="px-3 py-2 border border-gray-200 rounded-lg text-sm disabled:opacity-30">上一题</button>
      <button v-if="!isReadonly" @click="handleSubmit" :disabled="submitted" class="flex-1 py-2 bg-purple text-white rounded-lg text-sm font-medium disabled:opacity-40">提交</button>
      <button v-if="!isReadonly" @click="nextQuestion" :disabled="!hasNext" class="px-3 py-2 border border-gray-200 rounded-lg text-sm disabled:opacity-30">下一题</button>
      <button v-if="!hasNext && isFromWrong && !isReadonly" @click="backToWrong" class="flex-1 py-2 bg-purple text-white rounded-lg text-sm font-medium">返回错题本</button>
    </footer>
    <div class="flex items-center justify-between px-4 pb-20">
      <BottomDisclaimer />
      <button @click="showSettings=true" class="text-gray-400 hover:text-gray-600 ml-4 flex-shrink-0">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
      </button>
    </div>
    <AnswerSheet :open="showSheet" :items="sheetItems" :currentId="question?.id" @close="showSheet=false" @jump="jumpTo" />
    <ProgModeModal :open="showProgModeModal" @close="onProgModeClose" />
    <SettingsPanel :open="showSettings" @close="showSettings=false" />
    <Teleport to="body">
      <Transition enter-active-class="transition-opacity duration-200" leave-active-class="transition-opacity duration-200" enter-from-class="opacity-0" leave-to-class="opacity-0">
        <div v-if="toastVisible" class="fixed bottom-20 left-1/2 -translate-x-1/2 px-4 py-2 rounded-lg text-white text-sm z-50 bg-purple">{{ toastMsg }}</div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'
import { usePracticeStore } from '../stores/practice'
import { useSettingsStore } from '../stores/settings'
import { useAuthStore } from '../stores/auth'
import BottomDisclaimer from '../components/layout/BottomDisclaimer.vue'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'
import AnswerSheet from '../components/common/AnswerSheet.vue'
import SingleChoice from '../components/practice/SingleChoice.vue'
import TrueFalse from '../components/practice/TrueFalse.vue'
import FillBlank from '../components/practice/FillBlank.vue'
import CodeWrite from '../components/practice/CodeWrite.vue'
import CodeReview from '../components/practice/CodeReview.vue'
import ProgModeModal from '../components/common/ProgModeModal.vue'
import SettingsPanel from '../components/common/SettingsPanel.vue'

const store = usePracticeStore()
const settings = useSettingsStore()
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const question = ref(null), loading = ref(false), submitted = ref(false)
const showProgModeModal = ref(false)
const toastVisible = ref(false), toastMsg = ref('')

function showToast(msg) { toastMsg.value = msg; toastVisible.value = true; setTimeout(() => toastVisible.value = false, 2500) }
function onProgModeClose() {
  showProgModeModal.value = false
  if (auth.user?.prog_mode === null) {
    settings.progMode = 'write'
    settings.update()
    showToast('可在设置中修改编程题模式')
  }
}
const answerRef = ref(null), showSheet = ref(false), showSettings = ref(false)
const questions = ref([]), questionIndex = ref(0)
const answerStatuses = ref({})
const progress = reactive({ done: 0, total: 618, accuracy: 0 })

const typeComp = computed(() => {
  if (!question.value) return null
  const map = { '单选题': SingleChoice, '判断题': TrueFalse, '填空题': FillBlank }
  if (question.value.type === '编程题') return settings.progMode === 'review' ? CodeReview : CodeWrite
  return map[question.value.type]
})

const progressPercent = computed(() => questions.value.length ? (questionIndex.value / questions.value.length) * 100 : 0)
const hasPrev = computed(() => questionIndex.value > 0)
const hasNext = computed(() => questionIndex.value < questions.value.length - 1)
const sheetItems = computed(() => questions.value.map((q, i) => ({ id: q.id, label: i + 1, status: answerStatuses.value[q.id] || null })))
const isReadonly = computed(() => route.meta.readonly === true)
const isFromWrong = computed(() => route.path.includes('/wrong'))

function backToWrong() { router.push('/wrong') }
function toggleMode() {
  store.setMode(store.mode === 'random' ? 'sequential' : 'random')
  if (store.mode === 'random') {
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

  // 根据路由设置模式
  if (route.path.includes('/random')) {
    store.setMode('random')
  } else if (route.path.includes('/wrong')) {
    store.setMode('wrong')
  } else {
    store.setMode('sequential')
  }

  // 错题重做：根据 ids 参数加载特定题目
  if (route.query.ids) {
    const ids = route.query.ids.split(',').map(Number)
    questions.value = await Promise.all(ids.map(async (id, i) => {
      const { data } = await api.get(`/questions/${id}`)
      return { id, q_number: data.q_number, type: data.type, title: data.title }
    }))
    if (questions.value.length) question.value = await store.fetchQuestion(questions.value[0].id)
    loading.value = false
    return
  }

  // 构造 API 请求参数
  const params = { per: 1000 }
  if (route.query.type) {
    params.type = Array.isArray(route.query.type) ? route.query.type.join(',') : route.query.type
  }
  if (route.query.chapter) params.chapter = route.query.chapter

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

function handleSubmit() { answerRef.value?.doSubmit?.(); submitted.value = true }
function nextQuestion() { if (hasNext.value) { questionIndex.value++; loadCurrent(); submitted.value = false } }
function prevQuestion() { if (hasPrev.value) { questionIndex.value--; loadCurrent(); submitted.value = false } }
async function loadCurrent() {
  loading.value = true; question.value = await store.fetchQuestion(questions.value[questionIndex.value].id); loading.value = false
  if (isReadonly.value) submitted.value = true
  if (question.value?.type === '编程题' && auth.needsSetup) showProgModeModal.value = true
}
async function jumpTo(id) { questionIndex.value = questions.value.findIndex(q => q.id === id); loadCurrent(); showSheet.value = false; submitted.value = false }
async function onSubmit(result) {
  try {
    const status = result.isCorrect ? 'correct' : (result.partial ? 'partial' : 'incorrect')
    answerStatuses.value[question.value.id] = status
    await store.submitAnswer({
      question_id: question.value.id,
      answer_status: status,
      user_answer: JSON.stringify(result),
      mode: store.mode,
      ai_feedback: result.aiFeedback ? JSON.stringify(result.aiFeedback) : null,
    })
  } catch (e) {
    console.error('提交失败', e)
  }
}
</script>
