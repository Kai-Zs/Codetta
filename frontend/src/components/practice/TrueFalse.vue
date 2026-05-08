<template>
  <div class="flex gap-3">
    <button @click="select(true)"
      :class="[
        'flex-1 py-4 rounded-xl text-base font-medium border-2 transition',
        submitted
          ? answer === true
            ? answer === correctAnswer ? 'border-green bg-green/5 text-green' : 'border-red-400 bg-red-50 dark:bg-red-50/10 text-red-400'
            : correctAnswer === true ? 'border-green bg-green/5 text-green' : 'border-gray-100 dark:border-gray-700 text-gray-300 dark:text-gray-600'
          : answer === true ? 'border-purple bg-purple/5 dark:bg-purple/10 text-purple' : 'border-gray-100 dark:border-gray-700 text-gray-600 dark:text-gray-300'
      ]">正确</button>
    <button @click="select(false)"
      :class="[
        'flex-1 py-4 rounded-xl text-base font-medium border-2 transition',
        submitted
          ? answer === false
            ? answer === correctAnswer ? 'border-green bg-green/5 text-green' : 'border-red-400 bg-red-50 dark:bg-red-50/10 text-red-400'
            : correctAnswer === false ? 'border-green bg-green/5 text-green' : 'border-gray-100 dark:border-gray-700 text-gray-300 dark:text-gray-600'
          : answer === false ? 'border-purple bg-purple/5 dark:bg-purple/10 text-purple' : 'border-gray-100 dark:border-gray-700 text-gray-600 dark:text-gray-300'
      ]">错误</button>
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

function select(v) { if (props.submitted) return; answer.value = v; emit('answer', v ? '正确' : '错误') }
function getAnswer() { return answer.value === true ? '正确' : answer.value === false ? '错误' : '' }
function reset() { answer.value = null }

defineExpose({ getAnswer, reset })
</script>
