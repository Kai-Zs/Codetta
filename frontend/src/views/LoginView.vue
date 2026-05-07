<template>
  <div class="min-h-screen bg-bg flex flex-col items-center justify-center px-4">
    <h1 class="text-4xl font-[Cormorant_Garamond] text-purple mb-2">练笔小筑</h1>
    <p class="text-gray-400 text-sm mb-8">一题一阶，拾级而上</p>

    <!-- 阶段1：输入学号 -->
    <div v-if="stage==='id'" class="w-full max-w-sm">
      <input v-model="studentId" maxlength="10" placeholder="请输入10位学号"
        class="w-full px-4 py-3 border border-gray-200 rounded-lg text-center text-lg tracking-widest focus:outline-none focus:border-purple" />
      <button @click="doLogin" :disabled="studentId.length!==10"
        class="w-full mt-4 py-3 bg-purple text-white rounded-lg disabled:opacity-40 font-medium">确认</button>
    </div>

    <!-- 阶段2：验证 PIN -->
    <div v-else-if="stage==='pin'" class="w-full max-w-sm">
      <p class="text-center text-gray-600 mb-4">{{ userName }}</p>
      <input v-model="pin" type="password" maxlength="4" placeholder="请输入4位PIN"
        class="w-full px-4 py-3 border border-gray-200 rounded-lg text-center text-lg tracking-widest focus:outline-none focus:border-purple" />
      <button @click="doVerify" :disabled="pin.length!==4"
        class="w-full mt-4 py-3 bg-purple text-white rounded-lg disabled:opacity-40 font-medium">确认</button>
      <p class="text-center text-xs text-gray-400 mt-4">忘记PIN？请联系作者</p>
    </div>

    <!-- 阶段3：设置 PIN（首次） -->
    <div v-else class="w-full max-w-sm">
      <p class="text-center text-gray-600 mb-4">{{ userName }}，请设置PIN</p>
      <input v-model="newPin" type="password" maxlength="4" placeholder="4位数字PIN"
        class="w-full px-4 py-3 border border-gray-200 rounded-lg text-center text-lg tracking-widest focus:outline-none focus:border-purple mb-3" />
      <input v-model="newPin2" type="password" maxlength="4" placeholder="再次输入PIN"
        class="w-full px-4 py-3 border border-gray-200 rounded-lg text-center text-lg tracking-widest focus:outline-none focus:border-purple" />
      <button @click="doSetPin" :disabled="newPin.length!==4 || newPin!==newPin2"
        class="w-full mt-4 py-3 bg-purple text-white rounded-lg disabled:opacity-40 font-medium">设置</button>
    </div>

    <p v-if="error" class="text-red-500 text-sm mt-4">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const auth = useAuthStore()

const stage = ref('id'), studentId = ref(''), pin = ref('')
const userName = ref(''), newPin = ref(''), newPin2 = ref(''), error = ref('')

async function doLogin() {
  error.value = ''
  try {
    const d = await auth.login(studentId.value)
    userName.value = d.name
    if (d.status === 'need_pin') stage.value = 'pin'
    else stage.value = 'setup'
  } catch (e) { error.value = e.response?.data?.detail || '登录失败' }
}

async function doVerify() {
  error.value = ''
  try {
    await auth.verifyPin(studentId.value, pin.value)
    await auth.fetchMe()
    router.push('/')
  } catch (e) { error.value = e.response?.data?.detail || 'PIN 错误' }
}

async function doSetPin() {
  error.value = ''
  try {
    await api.post('/auth/set-pin', { pin: newPin.value })
    await auth.verifyPin(studentId.value, newPin.value)
    await auth.fetchMe()
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'PIN 设置失败，请重试'
  }
}
</script>
