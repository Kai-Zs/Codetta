<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div class="bg-white dark:bg-gray-800 rounded-2xl px-6 py-6 w-72 shadow-xl">
        <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4 text-center">管理员登录</h2>
        <input v-model="pwd" type="password" placeholder="请输入管理员密码"
          @keyup.enter="doLogin"
          class="w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-center dark:text-gray-200 focus:outline-none focus:border-purple mb-3" />
        <button @click="doLogin" class="w-full py-2.5 bg-purple text-white rounded-lg text-sm font-medium">确认</button>
        <p v-if="error" class="text-red-400 text-xs mt-2 text-center">{{ error }}</p>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import api from '../../api'

const emit = defineEmits(['ok'])
const pwd = ref('')
const error = ref('')

async function doLogin() {
  error.value = ''
  try {
    await api.post('/admin/verify', null, { headers: { 'X-Admin-Password': pwd.value } })
    sessionStorage.setItem('admin_token', pwd.value)
    emit('ok')
  } catch {
    error.value = '密码错误'
  }
}
</script>
