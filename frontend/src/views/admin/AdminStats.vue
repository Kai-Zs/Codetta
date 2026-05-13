<template>
  <div>
    <!-- 总览卡片 -->
    <div class="grid grid-cols-4 gap-3 mb-6">
      <div v-for="card in overviewCards" :key="card.label"
        class="rounded-xl p-4 text-center" :class="card.bg">
        <p class="text-2xl font-bold" :class="card.color">{{ card.value }}</p>
        <p class="text-xs mt-1" :class="card.subColor">{{ card.label }}</p>
      </div>
    </div>

    <!-- 章节正确率 + 题型正确率 并排 -->
    <div class="grid grid-cols-2 gap-6 mb-6">
      <!-- 章节正确率柱状图 -->
      <div>
        <h4 class="text-sm font-medium text-gray-600 dark:text-gray-300 mb-3">章节正确率</h4>
        <div class="space-y-2">
          <div v-for="c in stats.chapter_stats" :key="c.chapter" class="flex items-center gap-2">
            <span class="text-xs text-gray-500 dark:text-gray-400 w-14 flex-shrink-0">第{{ c.chapter }}章</span>
            <div class="flex-1 h-5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden relative">
              <div class="h-full rounded-full transition-all duration-500"
                :class="barColor(c.accuracy)"
                :style="{ width: Math.max(c.accuracy, 4) + '%' }"></div>
            </div>
            <span class="text-xs font-medium w-16 text-right flex-shrink-0"
              :class="c.accuracy >= 60 ? 'text-green' : c.accuracy >= 30 ? 'text-yellow-500' : 'text-red-400'">
              {{ c.accuracy }}%
            </span>
          </div>
        </div>
      </div>

      <!-- 题型正确率 -->
      <div>
        <h4 class="text-sm font-medium text-gray-600 dark:text-gray-300 mb-3">题型正确率</h4>
        <div class="space-y-2">
          <div v-for="t in stats.type_accuracy" :key="t.type" class="flex items-center gap-2">
            <span class="text-xs text-gray-500 dark:text-gray-400 w-12 flex-shrink-0">{{ t.type }}</span>
            <div class="flex-1 h-5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden relative">
              <div class="h-full rounded-full transition-all duration-500"
                :class="barColor(t.accuracy)"
                :style="{ width: Math.max(t.accuracy, 4) + '%' }"></div>
            </div>
            <span class="text-xs font-medium w-14 text-right flex-shrink-0"
              :class="t.accuracy >= 60 ? 'text-green' : t.accuracy >= 30 ? 'text-yellow-500' : 'text-red-400'">
              {{ t.accuracy }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 题型分布 + 近14天活跃 -->
    <div class="grid grid-cols-2 gap-6 mb-6">
      <!-- 题型分布 -->
      <div>
        <h4 class="text-sm font-medium text-gray-600 dark:text-gray-300 mb-3">题型分布</h4>
        <div class="space-y-2">
          <div v-for="t in stats.type_distribution" :key="t.type" class="flex items-center gap-2">
            <span class="text-xs text-gray-500 dark:text-gray-400 w-12 flex-shrink-0">{{ t.type }}</span>
            <div class="flex-1 h-5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
              <div class="h-full bg-purple/60 rounded-full transition-all duration-500"
                :style="{ width: maxPercent(t.cnt, stats.type_distribution) + '%' }"></div>
            </div>
            <span class="text-xs text-gray-500 dark:text-gray-400 w-10 text-right flex-shrink-0">{{ t.cnt }}</span>
          </div>
        </div>
      </div>

      <!-- 近 14 天活跃 -->
      <div>
        <h4 class="text-sm font-medium text-gray-600 dark:text-gray-300 mb-3">近 14 天提交量</h4>
        <div v-if="stats.recent_daily && stats.recent_daily.length" class="flex items-end gap-0.5 h-24">
          <div v-for="(d, i) in stats.recent_daily" :key="i"
            class="flex-1 bg-purple/60 hover:bg-purple rounded-t transition-colors relative group"
            :style="{ height: dailyHeight(d.cnt) + '%' }"
            :title="d.day + ': ' + d.cnt + ' 次'">
            <span class="absolute -bottom-5 left-1/2 -translate-x-1/2 text-[9px] text-gray-400 opacity-0 group-hover:opacity-100 transition whitespace-nowrap">{{ d.day.slice(5) }}</span>
          </div>
        </div>
        <p v-else class="text-xs text-gray-400">暂无数据</p>
      </div>
    </div>

    <!-- 易错题 TOP10 + 活跃 TOP10 -->
    <div class="grid grid-cols-2 gap-6">
      <!-- 易错题 -->
      <div>
        <h4 class="text-sm font-medium text-gray-600 dark:text-gray-300 mb-3">易错题 TOP10</h4>
        <div class="overflow-auto max-h-80">
          <table class="w-full text-xs text-left">
            <thead><tr class="border-b border-gray-100 dark:border-gray-700 text-gray-500 dark:text-gray-400">
              <th class="py-1.5 pr-1 w-5">#</th><th class="py-1.5 pr-1">题号</th><th class="py-1.5 pr-1">题型</th><th class="py-1.5 w-10">错误</th>
            </tr></thead>
            <tbody>
              <tr v-for="(m, i) in stats.top_missed" :key="i"
                class="border-b border-gray-50 dark:border-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800">
                <td class="py-1.5 pr-1" :class="i < 3 ? 'text-red-400 font-bold' : 'text-gray-400'">{{ i+1 }}</td>
                <td class="py-1.5 pr-1">{{ m.q_number }}</td>
                <td class="py-1.5 pr-1 text-gray-400">{{ m.type }}</td>
                <td class="py-1.5 text-red-400">{{ m.wrong_cnt }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 活跃用户 -->
      <div>
        <h4 class="text-sm font-medium text-gray-600 dark:text-gray-300 mb-3">活跃 TOP10</h4>
        <div class="space-y-2">
          <div v-for="(u, i) in stats.top_users" :key="i" class="flex items-center gap-3">
            <span class="text-xs font-bold w-5" :class="i < 3 ? 'text-purple' : 'text-gray-400'">{{ i+1 }}</span>
            <span class="text-xs text-gray-700 dark:text-gray-300 flex-1 truncate">{{ u.name || u.student_id }}</span>
            <div class="flex-1 h-4 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
              <div class="h-full bg-purple/50 rounded-full transition-all duration-500"
                :style="{ width: userBarWidth(u.done, stats.top_users) + '%' }"></div>
            </div>
            <span class="text-xs text-gray-400 w-10 text-right">{{ u.done }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'

const stats = ref({
  total_users: 0, total_questions: 0, total_submissions: 0, overall_accuracy: 0,
  chapter_stats: [], type_distribution: [], type_accuracy: [],
  top_users: [], top_missed: [], recent_daily: [],
})

const overviewCards = computed(() => [
  { label: '总用户数', value: stats.value.total_users || 0, bg: 'bg-purple/5 dark:bg-purple/10', color: 'text-purple', subColor: 'text-purple/60' },
  { label: '总题数', value: stats.value.total_questions || 0, bg: 'bg-blue-50 dark:bg-blue-900/20', color: 'text-blue-500', subColor: 'text-blue-400' },
  { label: '总提交数', value: stats.value.total_submissions || 0, bg: 'bg-emerald-50 dark:bg-emerald-900/20', color: 'text-emerald-500', subColor: 'text-emerald-400' },
  { label: '整体正确率', value: (stats.value.overall_accuracy || 0) + '%', bg: 'bg-amber-50 dark:bg-amber-900/20', color: 'text-amber-500', subColor: 'text-amber-400' },
])

function barColor(acc) {
  if (acc >= 60) return 'bg-green'
  if (acc >= 30) return 'bg-yellow-400'
  return 'bg-red-400'
}

function maxPercent(cnt, arr) {
  const max = Math.max(...arr.map(t => t.cnt), 1)
  return (cnt / max) * 100
}

function userBarWidth(done, arr) {
  const max = Math.max(...arr.map(u => u.done), 1)
  return (done / max) * 100
}

function dailyHeight(cnt) {
  const max = Math.max(...(stats.value.recent_daily || []).map(d => d.cnt), 1)
  return Math.max((cnt / max) * 100, 4)
}

onMounted(async () => {
  try { const { data } = await api.get('/admin/stats'); stats.value = data } catch {}
})
</script>
