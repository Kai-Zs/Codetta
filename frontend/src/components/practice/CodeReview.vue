<template>
  <div class="flex flex-col gap-4">
    <template v-if="!revealed">
      <p class="text-sm text-gray-500 dark:text-gray-400 text-center py-8">仔细阅读题目，思考解题思路</p>
      <button @click="revealed = true" class="w-full py-3 bg-purple text-white rounded-xl font-medium">我有思路了，看答案</button>
    </template>
    <template v-else>
      <div class="bg-gray-900 rounded-xl p-4 overflow-auto">
        <pre class="text-sm text-green-400 font-mono whitespace-pre-wrap">{{ question.answer_code || '(暂无答案)' }}</pre>
      </div>
      <p class="text-xs text-gray-400 dark:text-gray-600 text-center">人工智能生成，仅供参考</p>
      <div class="flex gap-3 mt-2">
        <button @click="selfEval = 'correct'" :class="selfEval === 'correct' ? 'bg-green text-white' : 'border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300'"
          class="flex-1 py-3 rounded-xl text-sm font-medium transition">做对了</button>
        <button @click="selfEval = 'wrong'" :class="selfEval === 'wrong' ? 'bg-red-400 text-white' : 'border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300'"
          class="flex-1 py-3 rounded-xl text-sm font-medium transition">做错了</button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({ question: Object })
const revealed = ref(false)
const selfEval = ref(null)

function doSubmit() {
  if (!selfEval.value) return null
  return { isCorrect: selfEval.value === 'correct', progSubmitType: 'review' }
}
function reset() { revealed.value = false; selfEval.value = null }
defineExpose({ doSubmit, reset })
</script>
