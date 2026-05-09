<template>
  <div>
    <!-- 总览卡片 -->
    <div class="grid grid-cols-2 gap-3 mb-6">
      <div class="bg-gray-50 dark:bg-gray-800 rounded-xl p-4 text-center">
        <p class="text-2xl font-bold text-purple">{{ stats.total_users || 0 }}</p>
        <p class="text-xs text-gray-400 mt-1">总用户数</p>
      </div>
      <div class="bg-gray-50 dark:bg-gray-800 rounded-xl p-4 text-center">
        <p class="text-2xl font-bold text-purple">{{ stats.total_questions || 0 }}</p>
        <p class="text-xs text-gray-400 mt-1">总题数</p>
      </div>
      <div class="bg-gray-50 dark:bg-gray-800 rounded-xl p-4 text-center">
        <p class="text-2xl font-bold text-purple">{{ stats.total_submissions || 0 }}</p>
        <p class="text-xs text-gray-400 mt-1">总提交数</p>
      </div>
      <div class="bg-gray-50 dark:bg-gray-800 rounded-xl p-4 text-center">
        <p class="text-2xl font-bold text-purple">{{ stats.overall_accuracy || 0 }}%</p>
        <p class="text-xs text-gray-400 mt-1">整体正确率</p>
      </div>
    </div>

    <!-- 章节正确率 -->
    <h4 class="text-sm font-medium text-gray-600 dark:text-gray-300 mb-2">章节正确率</h4>
    <div class="overflow-auto mb-6">
      <table class="w-full text-sm text-left">
        <thead><tr class="border-b border-gray-100 dark:border-gray-700 text-gray-500 dark:text-gray-400"><th class="py-2 pr-2">章节</th><th class="py-2 pr-2 w-16">题数</th><th class="py-2 pr-2 w-16">提交数</th><th class="py-2 pr-2 w-16">正确率</th></tr></thead>
        <tbody>
          <tr v-for="c in stats.chapter_stats" :key="c.chapter" class="border-b border-gray-50 dark:border-gray-800 text-gray-700 dark:text-gray-300">
            <td class="py-2 pr-2 text-xs">第{{ c.chapter }}章</td>
            <td class="py-2 pr-2 text-xs">{{ c.q_cnt }}</td>
            <td class="py-2 pr-2 text-xs">{{ c.done_cnt }}</td>
            <td class="py-2 pr-2 text-xs">{{ c.accuracy }}%</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 题型分布 + TOP10 -->
    <div class="grid grid-cols-2 gap-6">
      <div>
        <h4 class="text-sm font-medium text-gray-600 dark:text-gray-300 mb-2">题型分布</h4>
        <div v-for="t in stats.type_distribution" :key="t.type" class="flex justify-between text-xs py-1 border-b border-gray-50 dark:border-gray-800 text-gray-600 dark:text-gray-400">
          <span>{{ t.type }}</span><span>{{ t.cnt }} 题</span>
        </div>
      </div>
      <div>
        <h4 class="text-sm font-medium text-gray-600 dark:text-gray-300 mb-2">活跃 TOP10</h4>
        <div v-for="(u, i) in stats.top_users" :key="i" class="flex justify-between text-xs py-1 border-b border-gray-50 dark:border-gray-800 text-gray-600 dark:text-gray-400">
          <span>#{{ i+1 }} {{ u.student_id }}</span><span>{{ u.done }} 题</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const stats = ref({
  total_users: 0, total_questions: 0, total_submissions: 0, overall_accuracy: 0,
  chapter_stats: [], type_distribution: [], top_users: [],
})

onMounted(async () => {
  try { const { data } = await api.get('/admin/stats'); stats.value = data } catch {}
})
</script>
