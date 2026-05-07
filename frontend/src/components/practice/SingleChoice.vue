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
            ? answer === correctIdx ? 'border-green bg-green/5 text-green' : 'border-red-400 bg-red-50 text-red-400'
            : i === correctIdx ? 'border-green bg-green/5 text-green' : 'border-gray-100 bg-gray-50 text-gray-400'
          : answer === i ? 'border-purple bg-purple/5 text-purple' : 'border-gray-100 text-gray-600 hover:border-gray-200'
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

// 从 options 文本推断正确选项索引
const correctIdx = computed(() => {
  if (!props.options?.length) return -1
  return -1  // 正确答案由父组件通过 question.answer 提供
})

function select(i) {
  if (props.submitted) return
  answer.value = i
  emit('answer', letters[i])
}

function getAnswer() { return answer.value >= 0 ? letters[answer.value] : '' }
function reset() { answer.value = -1 }

defineExpose({ getAnswer, reset })
</script>
