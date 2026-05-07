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
      <span class="font-medium mr-2">{{ letters[i] }}.</span>{{ opt }}
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({ options: Array, submitted: Boolean })
const emit = defineEmits(['answer'])

const letters = 'ABCDEFGHIJ'.split('')
const answer = ref(-1)
const correctIdx = computed(() => -1)

function select(i) { if (props.submitted) return; answer.value = i; emit('answer', letters[i]) }
function getAnswer() { return answer.value >= 0 ? letters[answer.value] : '' }
function reset() { answer.value = -1 }

defineExpose({ getAnswer, reset })
</script>
