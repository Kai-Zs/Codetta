<template>
  <div class="flex flex-col gap-3">
    <div v-for="(part, i) in blanks" :key="i" class="flex flex-col gap-1">
      <div class="flex items-center gap-2">
        <span class="text-sm text-gray-400 w-5">{{ i + 1 }}.</span>
        <input
          v-model="answers[i]"
          :disabled="submitted"
          :class="[
            'flex-1 px-3 py-2.5 border rounded-lg text-sm focus:outline-none',
            submitted
              ? results[i] ? 'border-green bg-green/5 text-green' : 'border-red-400 bg-red-50 text-red-400'
              : 'border-gray-200 focus:border-purple'
          ]"
          placeholder="输入答案" />
        <span v-if="submitted" class="text-sm w-5">{{ results[i] ? '✓' : '✗' }}</span>
      </div>
      <p v-if="submitted && !results[i]" class="text-xs text-green pl-7">正确答案：{{ part }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const props = defineProps({ blanks: Array, submitted: Boolean })

const answers = ref(props.blanks?.map(() => '') || [])
const results = reactive([])

function getAnswer() {
  const correct = props.blanks || []
  const result = answers.value.map((a, i) => ({
    input: a.trim(),
    is_correct: a.trim().toLowerCase() === (correct[i] || '').toLowerCase()
  }))
  return result
}

function reset() {
  answers.value = props.blanks?.map(() => '') || []
  results.length = 0
}

function checkResults() {
  const correct = props.blanks || []
  results.length = 0
  answers.value.forEach((a, i) => {
    results.push(a.trim().toLowerCase() === (correct[i] || '').toLowerCase())
  })
}

defineExpose({ getAnswer, reset, checkResults })
</script>
