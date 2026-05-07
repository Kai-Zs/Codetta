<template>
  <div>
    <p class="text-gray-700 mb-6 whitespace-pre-wrap">{{ question.content }}</p>
    <button v-if="!revealed" @click="reveal" class="w-full py-4 border-2 border-purple text-purple rounded-xl font-medium">我有思路了，看答案</button>
    <div v-else class="p-4 bg-gray-50 rounded-xl">
      <pre class="font-mono text-sm whitespace-pre-wrap">{{ question.answer_code || '暂无参考答案' }}</pre>
      <div class="flex gap-3 mt-4">
        <button @click="done(true)" class="flex-1 py-2 bg-green text-white rounded-lg">我做对了</button>
        <button @click="done(false)" class="flex-1 py-2 bg-red-500 text-white rounded-lg">我做错了</button>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'
defineProps({ question: Object })
const emit = defineEmits(['submit'])
const revealed = ref(false)
function reveal() { revealed.value = true }
function done(correct) { emit('submit', { answer: 'review', isCorrect: correct }) }
</script>
