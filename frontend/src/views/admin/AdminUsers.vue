<template>
  <div>
    <div class="flex gap-2 mb-4">
      <input v-model="searchStr" placeholder="搜索学号/姓名" @keyup.enter="search"
        class="flex-1 px-3 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-lg text-sm dark:text-gray-200" />
      <button @click="search" class="px-4 py-2 bg-purple text-white rounded-lg text-sm">搜索</button>
    </div>

    <div class="overflow-auto">
      <table class="w-full text-sm text-left">
        <thead>
          <tr class="border-b border-gray-100 dark:border-gray-700 text-gray-500 dark:text-gray-400">
            <th class="py-2 pr-2">学号</th><th class="py-2 pr-2">姓名</th><th class="py-2 pr-2 w-14">做题数</th><th class="py-2 pr-2 w-14">正确率</th><th class="py-2 pr-2 w-20">AI知识点</th><th class="py-2 w-28">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in list" :key="u.id" class="border-b border-gray-50 dark:border-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800">
            <td class="py-2 pr-2 text-xs">{{ u.student_id }}</td>
            <td class="py-2 pr-2 text-xs">{{ u.name }}</td>
            <td class="py-2 pr-2 text-xs">{{ u.done_count || 0 }}</td>
            <td class="py-2 pr-2 text-xs">{{ u.accuracy }}%</td>
            <td class="py-2 pr-2 text-xs">
              <button
                @click="toggleKp(u)"
                :class="kpMap[u.student_id] ? 'bg-purple' : 'bg-gray-200 dark:bg-gray-600'"
                class="w-12 h-7 rounded-full transition-colors relative"
              >
                <span
                  :class="kpMap[u.student_id] ? 'translate-x-5' : 'translate-x-0'"
                  class="absolute top-0.5 left-0.5 w-6 h-6 bg-white rounded-full shadow transition-transform duration-200"
                ></span>
              </button>
            </td>
            <td class="py-2 text-xs flex gap-1">
              <button @click="$router.push({ path: `/admin/users/${u.id}`, query: { done: u.done_count, acc: u.accuracy } })" class="text-purple hover:underline">详情</button>
              <button @click="resetPin(u)" class="text-red-400 hover:underline">重置PIN</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="flex justify-between items-center mt-3 text-xs text-gray-400">
      <span>共 {{ total }} 条</span>
      <div class="flex gap-2">
        <button @click="goPage(page-1)" :disabled="page<=1" class="disabled:opacity-30">&larr;</button>
        <span>{{ page }}/{{ Math.ceil(total/per) || 1 }}</span>
        <button @click="goPage(page+1)" :disabled="page*per>=total" class="disabled:opacity-30">&rarr;</button>
      </div>
    </div>

    <!-- 确认弹窗 -->
    <ConfirmDialog :open="confirmOpen" :msg="confirmMsg" @confirm="doReset" @close="confirmOpen = false" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'
import ConfirmDialog from '../../components/common/ConfirmDialog.vue'

const searchStr = ref(''), list = ref([]), page = ref(1), total = ref(0), per = ref(20)
const confirmOpen = ref(false), confirmMsg = ref(''), resetTarget = ref(null)
const kpMap = ref({})

onMounted(() => { fetchList(); fetchKpMap() })
async function search() { page.value = 1; await fetchList() }

async function fetchKpMap() {
  try {
    const { data } = await api.get('/admin/kp-access')
    const map = {}
    data.items.forEach(i => { map[i.student_id] = i.kp_enabled })
    kpMap.value = map
  } catch { /* ignore */ }
}

async function toggleKp(u) {
  const newVal = !kpMap.value[u.student_id]
  kpMap.value[u.student_id] = newVal
  try {
    await api.post('/admin/kp-access', { student_id: u.student_id, enabled: newVal })
  } catch {
    kpMap.value[u.student_id] = !newVal
  }
}
async function fetchList() {
  const { data } = await api.get('/admin/users', { params: { search: searchStr.value, page: page.value, per: per.value } })
  list.value = data.items; total.value = data.total
}
function goPage(p) { page.value = p; fetchList() }
function resetPin(u) {
  resetTarget.value = u
  confirmMsg.value = `确定要重置 ${u.name}（${u.student_id}）的 PIN 吗？`
  confirmOpen.value = true
}
async function doReset() {
  await api.post(`/admin/users/${resetTarget.value.id}/reset-pin`)
  confirmOpen.value = false
}
</script>
