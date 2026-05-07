<template>
  <div>
    <p class="text-gray-700 mb-6 whitespace-pre-wrap">{{ question.content }}</p>
    <div class="space-y-3">
      <div v-for="(part, i) in parts" :key="i" class="flex items-center gap-2">
        <span class="text-sm text-gray-400">空{{ i+1 }}</span>
        <input v-model="answers[i]" :disabled="submitted" :class="['flex-1 px-3 py-2 border rounded-lg focus:outline-none',
          submitted ? (answers[i]?.trim()===part ? 'border-green bg-green/10' : 'border-red-500 bg-red-50') : 'border-gray-200 focus:border-purple']" />
        <span v-if="submitted" :class="answers[i]?.trim()===part ? 'text-green' : 'text-red-500'">{{ answers[i]?.trim()===part ? '✓' : '✗' }}</span>
      </div>
    </div>
    <div v-if="submitted" class="mt-4 p-3 bg-gray-50 rounded-lg">
      <p class="text-sm text-gray-500">正确答案：<span class="text-purple font-medium">{{ parts.join('  |  ') }}</span></p>
    </div>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
const props = defineProps({ question: Object })
const emit = defineEmits(['submit'])
const parts = computed(() => JSON.parse(props.question.answer_parts || '[]'))
const answers = ref(parts.value.map(() => ''))
const submitted = ref(false)
function doSubmit() {
  submitted.value = true
  const correctCount = parts.value.filter((p, i) => answers.value[i]?.trim() === p).length
  emit('submit', { answers: answers.value, isCorrect: correctCount === parts.value.length, partial: correctCount > 0 && correctCount < parts.value.length })
}
defineExpose({ doSubmit })
</script>
