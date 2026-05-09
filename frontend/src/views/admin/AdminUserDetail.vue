<template>
  <div>
    <div class="flex items-center gap-3 mb-4">
      <button @click="$router.back()" class="text-gray-400 hover:text-purple transition">&larr; 返回</button>
      <h3 class="text-base font-semibold text-gray-800 dark:text-gray-200">{{ user.name }}</h3>
    </div>

    <div class="grid grid-cols-2 gap-3 mb-6">
      <div class="bg-gray-50 dark:bg-gray-800 rounded-xl p-3"><p class="text-xs text-gray-400">学号</p><p class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ user.student_id }}</p></div>
      <div class="bg-gray-50 dark:bg-gray-800 rounded-xl p-3"><p class="text-xs text-gray-400">做题数</p><p class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ doneCount }}</p></div>
      <div class="bg-gray-50 dark:bg-gray-800 rounded-xl p-3"><p class="text-xs text-gray-400">正确率</p><p class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ accuracy }}%</p></div>
      <div class="bg-gray-50 dark:bg-gray-800 rounded-xl p-3"><p class="text-xs text-gray-400">错题数</p><p class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ wrongCount }}</p></div>
    </div>

    <h4 class="text-sm font-medium text-gray-600 dark:text-gray-300 mb-2">最近答题记录</h4>
    <div class="overflow-auto max-h-80">
      <table class="w-full text-sm text-left">
        <thead><tr class="border-b border-gray-100 dark:border-gray-700 text-gray-500 dark:text-gray-400"><th class="py-2 pr-2">题号</th><th class="py-2 pr-2">题型</th><th class="py-2 pr-2 max-w-48">标题</th><th class="py-2 pr-2 w-12">结果</th><th class="py-2 w-32">时间</th></tr></thead>
        <tbody>
          <tr v-for="r in user.records" :key="r.answered_at" class="border-b border-gray-50 dark:border-gray-800 text-gray-700 dark:text-gray-300">
            <td class="py-2 pr-2 text-xs">{{ r.q_number }}</td>
            <td class="py-2 pr-2 text-xs">{{ r.type }}</td>
            <td class="py-2 pr-2 text-xs truncate max-w-48">{{ r.title }}</td>
            <td class="py-2 pr-2"><span :class="r.answer_status === 'correct' ? 'text-green' : 'text-red-400'" class="text-xs">{{ r.answer_status === 'correct' ? '✓' : '✗' }}</span></td>
            <td class="py-2 text-xs text-gray-400">{{ r.answered_at?.slice(0,16) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api'

const route = useRoute()
const user = ref({ records: [] })
const doneCount = computed(() => user.value.records?.length || 0)
const wrongCount = computed(() => user.value.records?.filter(r => r.answer_status !== 'correct').length || 0)
const accuracy = computed(() => {
  const d = doneCount.value
  if (!d) return 0
  return Math.round((d - wrongCount.value) / d * 100 * 10) / 10
})

onMounted(async () => {
  const { data } = await api.get(`/admin/users/${route.params.id}`)
  user.value = data
})
</script>
