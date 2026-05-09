<template>
  <div>
    <!-- 维护模式 -->
    <div class="mb-6">
      <h4 class="text-sm font-medium text-gray-600 dark:text-gray-300 mb-3">维护模式</h4>
      <div class="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-xl p-3">
        <span class="text-sm text-gray-700 dark:text-gray-300">暂停网站访问</span>
        <button @click="toggleMaintenance"
          :class="['w-11 h-6 rounded-full transition', maintenance ? 'bg-purple' : 'bg-gray-300']">
          <div :class="['w-5 h-5 rounded-full bg-white shadow transition', maintenance ? 'translate-x-6' : 'translate-x-0.5']" />
        </button>
      </div>
    </div>

    <!-- 改密码 -->
    <div class="mb-6">
      <h4 class="text-sm font-medium text-gray-600 dark:text-gray-300 mb-3">修改管理员密码</h4>
      <div class="space-y-2">
        <input v-model="oldPwd" type="password" placeholder="旧密码" class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-lg text-sm dark:text-gray-200" />
        <input v-model="newPwd" type="password" placeholder="新密码" class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-lg text-sm dark:text-gray-200" />
        <input v-model="newPwd2" type="password" placeholder="确认新密码" class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-lg text-sm dark:text-gray-200" />
        <button @click="changePwd" :disabled="!oldPwd || !newPwd || newPwd !== newPwd2"
          class="px-4 py-2 bg-purple text-white rounded-lg text-sm disabled:opacity-40">修改密码</button>
      </div>
      <p v-if="pwdMsg" class="text-xs mt-2" :class="pwdOk ? 'text-green' : 'text-red-400'">{{ pwdMsg }}</p>
    </div>

    <!-- 题库重载 -->
    <div>
      <h4 class="text-sm font-medium text-gray-600 dark:text-gray-300 mb-3">题库重载（危险操作）</h4>
      <button @click="confirmReload = true" class="px-4 py-2 bg-red-500 text-white rounded-lg text-sm">重载题库</button>
      <ConfirmDialog :open="confirmReload"
        msg="将从 Excel/HTML 重新导入题目，此操作不可恢复！确定继续？"
        @confirm="doReload" @close="confirmReload = false" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'
import ConfirmDialog from '../../components/common/ConfirmDialog.vue'

const maintenance = ref(false)
const oldPwd = ref(''), newPwd = ref(''), newPwd2 = ref('')
const pwdMsg = ref(''), pwdOk = ref(false)
const confirmReload = ref(false)

onMounted(async () => {
  try {
    const { data } = await api.get('/admin/settings')
    maintenance.value = data.maintenance
  } catch {}
})

async function toggleMaintenance() {
  const newVal = !maintenance.value
  await api.post('/admin/maintenance', null, { params: { enable: newVal ? 1 : 0 } })
  maintenance.value = newVal
}

async function changePwd() {
  pwdMsg.value = ''; pwdOk.value = false
  try {
    await api.put('/admin/password', { old_password: oldPwd.value, new_password: newPwd.value })
    pwdMsg.value = '密码已修改，下次登录生效'
    pwdOk.value = true
    oldPwd.value = ''; newPwd.value = ''; newPwd2.value = ''
  } catch (e) {
    pwdMsg.value = e.response?.status === 400 ? '旧密码错误' : '修改失败'
  }
}

async function doReload() {
  confirmReload.value = false
  try {
    await api.post('/admin/reload-seed')
    pwdMsg.value = '题库重载完成'; pwdOk.value = true
  } catch {
    pwdMsg.value = '重载失败'; pwdOk.value = false
  }
}
</script>
