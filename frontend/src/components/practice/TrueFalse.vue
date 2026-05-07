<template>
  <div>
    <p class="text-gray-700 mb-6 whitespace-pre-wrap">{{ question.content }}</p>
    <div class="flex gap-4">
      <button @click="choose('正确')" :class="['flex-1 py-4 rounded-xl border-2 text-lg font-medium transition',
        submitted ? (question.answer==='正确' ? 'border-green bg-green/10 text-green' : answer==='正确' ? 'border-red-500 bg-red-50 text-red-500' : 'border-gray-100')
        : answer==='正确' ? 'border-purple bg-purple/5' : 'border-gray-100']">正确</button>
      <button @click="choose('错误')" :class="['flex-1 py-4 rounded-xl border-2 text-lg font-medium transition',
        submitted ? (question.answer==='错误' ? 'border-green bg-green/10 text-green' : answer==='错误' ? 'border-red-500 bg-red-50 text-red-500' : 'border-gray-100')
        : answer==='错误' ? 'border-purple bg-purple/5' : 'border-gray-100']">错误</button>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'
const props = defineProps({ question: Object })
const emit = defineEmits(['submit'])
const answer = ref(null), submitted = ref(false)
function choose(v) { if (!submitted.value) answer.value = v }
function doSubmit() {
  submitted.value = true
  emit('submit', { answer: answer.value, isCorrect: answer.value === props.question.answer })
}
defineExpose({ doSubmit })
</script>
