<template>
  <div class="flex flex-col gap-2">
    <button
      v-for="(opt, i) in options"
      :key="i"
      @click="select(i)"
      :class="[
        'w-full px-4 py-3.5 rounded-xl text-sm text-left border-2 transition',
        submitted
          ? answer === i
            ? answer === correctIdx ? 'border-green bg-green/5 text-green' : 'border-red-400 bg-red-50 dark:bg-red-50/10 text-red-400'
            : i === correctIdx ? 'border-green bg-green/5 text-green' : 'border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-400 dark:text-gray-600'
          : answer === i ? 'border-purple bg-purple/5 dark:bg-purple/10 text-purple' : 'border-gray-100 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:border-gray-200 dark:hover:border-gray-600'
      ]">
      <span v-html="renderOpt(opt)"></span>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({ options: Array, submitted: Boolean, correctAnswer: String, previousAnswer: Object })
const emit = defineEmits(['answer'])

const letters = 'ABCDEFGHIJ'.split('')
const answer = ref(-1)
const correctIdx = computed(() => {
  if (!props.correctAnswer) return -1
  return props.options.findIndex(opt => {
    const prefix = opt.trim().slice(0, 1).toUpperCase()
    return prefix === props.correctAnswer.toUpperCase()
  })
})

// 回看时恢复上次选择的索引
watch(() => props.previousAnswer, (prev) => {
  if (prev && prev.answer && props.submitted) {
    const idx = letters.indexOf(prev.answer.toUpperCase())
    if (idx >= 0 && idx < props.options.length) answer.value = idx
  }
}, { immediate: true })

function renderOpt(text) { return text.replace(/\n/g, '<br>') }
function select(i) { if (props.submitted) return; answer.value = i; emit('answer', letters[i]) }
function getAnswer() { return answer.value >= 0 ? letters[answer.value] : '' }
function reset() { answer.value = -1 }

defineExpose({ getAnswer, reset })
</script>
