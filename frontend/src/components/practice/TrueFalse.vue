<template>
  <div class="flex gap-3">
    <button @click="select(true)"
      :class="btnClass(true, '正确')">正确</button>
    <button @click="select(false)"
      :class="btnClass(false, '错误')">错误</button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({ correctAnswer: String, submitted: Boolean, previousAnswer: Object })
const emit = defineEmits(['answer'])
const answer = ref(null)

watch(() => props.previousAnswer, (prev) => {
  if (prev && prev.answer && props.submitted) {
    answer.value = prev.answer === '正确'
  }
}, { immediate: true })

function isCorrect(label) {
  return props.correctAnswer === label
}

function btnClass(myVal, label) {
  const selected = answer.value === myVal
  const correct = isCorrect(label)
  if (!props.submitted) {
    return selected
      ? 'flex-1 py-4 rounded-xl text-base font-medium border-2 transition border-purple bg-purple/5 dark:bg-purple/10 text-purple'
      : 'flex-1 py-4 rounded-xl text-base font-medium border-2 transition border-gray-100 dark:border-gray-700 text-gray-600 dark:text-gray-300'
  }
  if (selected) {
    return correct
      ? 'flex-1 py-4 rounded-xl text-base font-medium border-2 transition border-green bg-green/5 text-green'
      : 'flex-1 py-4 rounded-xl text-base font-medium border-2 transition border-red-400 bg-red-50 dark:bg-red-50/10 text-red-400'
  }
  return correct
    ? 'flex-1 py-4 rounded-xl text-base font-medium border-2 transition border-green bg-green/5 text-green'
    : 'flex-1 py-4 rounded-xl text-base font-medium border-2 transition border-gray-100 dark:border-gray-700 text-gray-300 dark:text-gray-600'
}

function select(v) { if (props.submitted) return; answer.value = v; emit('answer', v ? '正确' : '错误') }
function getAnswer() { return answer.value === true ? '正确' : answer.value === false ? '错误' : '' }
function reset() { answer.value = null }

defineExpose({ getAnswer, reset })
</script>
