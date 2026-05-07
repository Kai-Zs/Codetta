<template>
  <div class="flex gap-3">
    <button
      @click="select(true)"
      :class="[
        'flex-1 py-4 rounded-xl text-base font-medium border-2 transition',
        submitted
          ? answer === true
            ? answer === correctAnswer ? 'border-green bg-green/5 text-green' : 'border-red-400 bg-red-50 text-red-400'
            : correctAnswer === true ? 'border-green bg-green/5 text-green' : 'border-gray-100 text-gray-300'
          : answer === true ? 'border-purple bg-purple/5 text-purple' : 'border-gray-100 text-gray-600'
      ]">
      正确
    </button>
    <button
      @click="select(false)"
      :class="[
        'flex-1 py-4 rounded-xl text-base font-medium border-2 transition',
        submitted
          ? answer === false
            ? answer === correctAnswer ? 'border-green bg-green/5 text-green' : 'border-red-400 bg-red-50 text-red-400'
            : correctAnswer === false ? 'border-green bg-green/5 text-green' : 'border-gray-100 text-gray-300'
          : answer === false ? 'border-purple bg-purple/5 text-purple' : 'border-gray-100 text-gray-600'
      ]">
      错误
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({ correctAnswer: String, submitted: Boolean })
const emit = defineEmits(['answer'])

const answer = ref(null)

function select(v) {
  if (props.submitted) return
  answer.value = v
  emit('answer', v ? '正确' : '错误')
}

function getAnswer() { return answer.value === true ? '正确' : answer.value === false ? '错误' : '' }
function reset() { answer.value = null }

defineExpose({ getAnswer, reset })
</script>
