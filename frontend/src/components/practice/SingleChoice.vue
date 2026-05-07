<template>
  <div>
    <p class="text-gray-700 mb-6 whitespace-pre-wrap">{{ question.content }}</p>
    <div class="space-y-3">
      <button v-for="(opt, i) in options" :key="i" @click="select(i)"
        :class="['w-full text-left px-4 py-3 rounded-xl border-2 transition font-medium',
          submitted ? (i===correctIdx ? 'border-green bg-green/10 text-green' : i===selected && i!==correctIdx ? 'border-red-500 bg-red-50 text-red-500' : 'border-gray-100')
          : selected===i ? 'border-purple bg-purple/5' : 'border-gray-100 hover:border-purple/30']">
        {{ opt }}
      </button>
    </div>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
const props = defineProps({ question: Object })
const emit = defineEmits(['submit'])
const selected = ref(null), submitted = ref(false)
const options = computed(() => JSON.parse(props.question.options || '[]'))
const correctIdx = computed(() => options.value.findIndex(o => o.startsWith(props.question.answer)))
function select(i) { if (!submitted.value) selected.value = i }
function doSubmit() {
  if (selected.value === null) return
  submitted.value = true
  emit('submit', { answer: String.fromCharCode(65 + selected.value), isCorrect: selected.value === correctIdx.value })
}
defineExpose({ doSubmit })
</script>
