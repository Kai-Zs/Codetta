<template>
  <div class="flex flex-col items-center justify-center min-h-full px-6 py-12">
    <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">管理员重置 PIN</h2>
    <p class="text-sm text-gray-400 dark:text-gray-500 mb-8">输入学号以重置该用户的 PIN</p>
    <input v-model="sid" maxlength="10" placeholder="学号"
      class="w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-center text-lg dark:text-gray-200 tracking-widest focus:outline-none focus:border-purple mb-4" />
    <button @click="doReset" :disabled="sid.length !== 10"
      class="w-full py-3 bg-red-500 text-white rounded-lg disabled:opacity-40 font-medium mb-4">重置 PIN</button>
    <p v-if="msg" class="text-sm" :class="msg.includes('成功') ? 'text-green' : 'text-red-400'">{{ msg }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api'

const sid = ref('')
const msg = ref('')

async function doReset() {
  try {
    await api.post('/auth/admin/reset-pin', { student_id: sid.value })
    msg.value = '重置成功'
  } catch { msg.value = '重置失败' }
}
</script>
