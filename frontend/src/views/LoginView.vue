<template>
  <div class="flex flex-col items-center justify-center min-h-full px-6 py-12">
    <!-- 标题 -->
    <h1 class="text-2xl font-[Georgia] text-purple tracking-widest mb-1">练笔小筑</h1>
    <p class="text-xs text-gray-400 tracking-widest mb-12">一题一阶 · 拾级而上</p>

    <!-- 阶段1：输入学号 -->
    <template v-if="stage===1">
      <p class="text-sm text-gray-500 mb-4">输入学号以继续</p>
      <input
        v-model="sid"
        maxlength="10"
        placeholder="学号"
        class="w-full px-4 py-3 border border-gray-200 rounded-lg text-center text-lg tracking-widest focus:outline-none focus:border-purple" />
      <button @click="doLogin" :disabled="sid.length!==10"
        class="w-full mt-4 py-3 bg-purple text-white rounded-lg disabled:opacity-40 font-medium">确认</button>
    </template>

    <!-- 阶段2：输入 PIN -->
    <template v-if="stage===2">
      <p class="text-sm text-gray-500 mb-4">你好，{{ userName }}</p>
      <input
        v-model="pin"
        type="password"
        maxlength="4"
        placeholder="PIN"
        class="w-full px-4 py-3 border border-gray-200 rounded-lg text-center text-lg tracking-widest focus:outline-none focus:border-purple" />
      <button @click="doVerify" :disabled="pin.length!==4"
        class="w-full mt-4 py-3 bg-purple text-white rounded-lg disabled:opacity-40 font-medium">确认</button>
      <p class="text-center text-xs text-gray-400 mt-4">忘记PIN？请联系作者</p>
    </template>

    <!-- 阶段3：设置 PIN -->
    <template v-if="stage===3">
      <p class="text-sm text-gray-500 mb-4">首次登录，请设置 PIN</p>
      <input
        v-model="pin"
        type="password"
        maxlength="4"
        placeholder="设置4位PIN"
        class="w-full px-4 py-3 border border-gray-200 rounded-lg text-center text-lg tracking-widest focus:outline-none focus:border-purple mb-3" />
      <input
        v-model="pin2"
        type="password"
        maxlength="4"
        placeholder="再次输入PIN"
        class="w-full px-4 py-3 border border-gray-200 rounded-lg text-center text-lg tracking-widest focus:outline-none focus:border-purple" />
      <p v-if="error" class="text-red-500 text-xs text-center mt-2">{{ error }}</p>
      <button @click="doSetPin" :disabled="pin.length!==4 || pin2.length!==4 || pin!==pin2"
        class="w-full mt-4 py-3 bg-purple text-white rounded-lg disabled:opacity-40 font-medium">设置 PIN</button>
    </template>

    <!-- 底部 -->
    <p class="text-xs text-gray-300 mt-16">Powered by 凯Z闪</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const stage = ref(1)
const sid = ref('')
const userName = ref('')
const pin = ref('')
const pin2 = ref('')
const error = ref('')

async function doLogin() {
  try {
    const data = await auth.login(sid.value)
    if (data.status === 'need_setup') {
      userName.value = data.name
      stage.value = 3
    } else if (data.status === 'need_pin') {
      userName.value = data.name
      stage.value = 2
    } else {
      router.push('/')
    }
  } catch {
    error.value = '登录失败，请检查学号'
  }
}

async function doVerify() {
  try {
    await auth.verifyPin(sid.value, pin.value)
    router.push('/')
  } catch {
    error.value = 'PIN 错误'
    pin.value = ''
  }
}

async function doSetPin() {
  try {
    await auth.setPin(pin.value)
    await auth.verifyPin(sid.value, pin.value)
    router.push('/')
  } catch {
    error.value = '设置失败，请重试'
  }
}
</script>
