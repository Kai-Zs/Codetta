<template>
  <div :class="['flex gap-4', isMobile ? 'flex-col' : 'flex-row']">
    <div :class="['overflow-y-auto', isMobile ? 'h-40' : 'flex-1']">
      <p class="text-gray-700 whitespace-pre-wrap text-sm">{{ question.content }}</p>
    </div>
    <div :class="['flex flex-col', isMobile ? '' : 'flex-1']">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs text-gray-400">代码编辑器</span>
        <button @click="code=question.template||''" class="text-xs text-purple">重置</button>
      </div>
      <textarea v-model="code" :disabled="submitted" :class="['w-full font-mono text-sm p-3 border rounded-lg resize-none focus:outline-none',
        isMobile ? 'h-48' : 'h-80', submitted ? 'bg-gray-50' : 'border-gray-200 focus:border-purple']" />
      <div v-if="judging" class="mt-3 text-center text-sm text-gray-400">判题中...</div>
      <div v-if="timeout" class="mt-3 p-3 bg-yellow-50 rounded-lg text-sm text-center">
        <p class="text-gray-600 mb-2">判题超时，请手动判断</p>
        <div class="flex gap-3 justify-center">
          <button @click="manualJudge(true)" class="px-4 py-1 bg-green text-white rounded-lg text-sm">做对了</button>
          <button @click="manualJudge(false)" class="px-4 py-1 bg-red-500 text-white rounded-lg text-sm">做错了</button>
        </div>
      </div>
      <div v-if="judgeResult" class="mt-3 p-3 bg-yellow-50 rounded-lg text-sm">
        <p><span class="font-medium">评分：{{ judgeResult.score }}/10</span> <span :class="judgeResult.is_correct ? 'text-green' : 'text-red-500'">{{ judgeResult.is_correct ? '✓' : '✗' }}</span></p>
        <p class="text-gray-600 mt-1">{{ judgeResult.comment }}</p>
        <p class="text-xs text-gray-400 mt-2">人工智能生成，仅供参考</p>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import api from '../../api'
const props = defineProps({ question: Object })
const emit = defineEmits(['submit'])
const code = ref(props.question.template || '')
const submitted = ref(false), judging = ref(false), timeout = ref(false), judgeResult = ref(null)
const isMobile = computed(() => window.innerWidth < 768)
function manualJudge(correct) {
  timeout.value = false
  emit('submit', { code: code.value, isCorrect: correct, manual: true })
}
async function doSubmit() {
  submitted.value = true; judging.value = true
  try {
    const { data } = await api.post('/judge/code', { question_id: props.question.id, user_code: code.value })
    judgeResult.value = data
    emit('submit', { code: code.value, isCorrect: data.is_correct, aiFeedback: data })
  } catch {
    timeout.value = true
  }
  judging.value = false
}
defineExpose({ doSubmit })
</script>
