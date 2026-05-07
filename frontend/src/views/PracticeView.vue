<template>
  <div class="min-h-screen bg-bg flex flex-col">
    <header class="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-white">
      <button @click="$router.back()" class="text-gray-500">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <span class="text-sm font-medium text-gray-600">{{ question?.q_number }}</span>
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
    <BottomDisclaimer />
    <AnswerSheet :open="showSheet" :items="sheetItems" :currentId="question?.id" @close="showSheet=false" @jump="jumpTo" />
    <ProgModeModal :open="showProgModeModal" @close="showProgModeModal=false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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

const store = usePracticeStore()
const settings = useSettingsStore()
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const question = ref(null), loading = ref(false), submitted = ref(false)
const showProgModeModal = ref(false)
const answerRef = ref(null), showSheet = ref(false)
const questions = ref([]), questionIndex = ref(0)

const typeComp = computed(() => {
  if (!question.value) return null
  const map = { '单选题': SingleChoice, '判断题': TrueFalse, '填空题': FillBlank }
  if (question.value.type === '编程题') return settings.progMode === 'review' ? CodeReview : CodeWrite
  return map[question.value.type]
})

const progressPercent = computed(() => questions.value.length ? (questionIndex.value / questions.value.length) * 100 : 0)
const hasPrev = computed(() => questionIndex.value > 0)
const hasNext = computed(() => questionIndex.value < questions.value.length - 1)
const sheetItems = computed(() => questions.value.map((q, i) => ({ id: q.id, label: i + 1, status: null })))
const isReadonly = computed(() => route.meta.readonly === true)
const isFromWrong = computed(() => route.path.includes('/wrong'))

function backToWrong() { router.push('/wrong') }

onMounted(async () => {
  try {
    loading.value = true
    await auth.fetchMe()
    settings.init()

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
    await store.submitAnswer({
      question_id: question.value.id,
      answer_status: result.isCorrect ? 'correct' : (result.partial ? 'partial' : 'incorrect'),
      user_answer: JSON.stringify(result),
      mode: store.mode,
      ai_feedback: result.aiFeedback ? JSON.stringify(result.aiFeedback) : null,
    })
  } catch (e) {
    console.error('提交失败', e)
  }
}
</script>
