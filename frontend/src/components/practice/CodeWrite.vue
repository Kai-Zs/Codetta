<template>
  <div>
    <div v-if="loading" class="flex flex-col items-center py-12">
      <div class="w-8 h-8 border-2 border-purple/20 border-t-purple rounded-full animate-spin mb-4"></div>
      <p class="text-sm text-gray-400">AI 正在评判你的代码...</p>
    </div>
    <div v-else-if="result" class="flex flex-col gap-3">
      <div class="flex items-center gap-3">
        <span class="text-2xl font-bold" :class="result.is_correct ? 'text-green' : 'text-red-400'">{{ result.score }}/10</span>
        <span class="text-sm" :class="result.is_correct ? 'text-green' : 'text-red-400'">{{ result.is_correct ? '正确' : '有误' }}</span>
      </div>
      <p class="text-sm text-gray-600 bg-gray-50 rounded-lg p-3">{{ result.comment }}</p>
      <p class="text-xs text-gray-400">人工智能生成，仅供参考</p>
    </div>
    <div v-else class="text-sm text-gray-400 text-center py-8">代码将在右侧编辑器中编写</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({ question: Object, submitted: Boolean })

const loading = ref(false)
const result = ref(null)

async function doSubmit(code) {
  if (!code) return { isCorrect: false }
  loading.value = true
  try {
    const api = (await import('../../api')).default
    const { data } = await api.post('/judge/code', {
      question_id: props.question.id,
      user_code: code,
    })
    result.value = data
    loading.value = false
    return { isCorrect: data.is_correct, aiFeedback: data }
  } catch {
    loading.value = false
    return { isCorrect: false, timeout: true }
  }
}

function reset() { result.value = null; loading.value = false }

defineExpose({ doSubmit, reset })
</script>
