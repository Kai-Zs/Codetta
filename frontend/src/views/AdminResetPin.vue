<template>
  <div class="min-h-screen bg-bg flex flex-col items-center justify-center px-4">
    <h1 class="text-2xl text-purple font-[Cormorant_Garamond] mb-8">重置 PIN</h1>
    <input v-model="sid" maxlength="10" placeholder="输入10位学号"
      class="w-full max-w-sm px-4 py-3 border border-gray-200 rounded-lg text-center text-lg tracking-widest mb-4 focus:outline-none focus:border-purple" />
    <button @click="doReset" :disabled="sid.length!==10"
      class="w-full max-w-sm py-3 bg-purple text-white rounded-lg disabled:opacity-40 font-medium">重置 PIN</button>
    <p v-if="msg" class="mt-4 text-sm" :class="msg==='PIN 已重置' ? 'text-green' : 'text-red-500'">{{ msg }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api'
const sid = ref(''), msg = ref('')
async function doReset() {
  try { await api.post('/admin/reset-pin', { student_id: sid.value }); msg.value = 'PIN 已重置' }
  catch { msg.value = '重置失败' }
}
</script>
