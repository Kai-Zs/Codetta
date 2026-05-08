<template>
  <div class="flex flex-col flex-1">
    <header class="flex items-center px-3 py-3">
      <button @click="$router.back()" class="text-gray-400 dark:text-gray-500 p-1 mr-3">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <h2 class="text-base font-semibold text-gray-800 dark:text-gray-200">错题本</h2>
    </header>

    <div class="flex gap-2 px-3 mb-3">
      <select v-model="store.filters.type" @change="store.fetchList()" class="flex-1 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 rounded-lg px-2 py-1.5 text-xs">
        <option value="">全部题型</option>
        <option value="单选题">单选题</option><option value="判断题">判断题</option><option value="填空题">填空题</option><option value="编程题">编程题</option>
      </select>
      <select v-model="store.filters.chapter" @change="store.fetchList()" class="flex-1 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 rounded-lg px-2 py-1.5 text-xs">
        <option value="">全部章节</option>
        <option v-for="ch in 8" :key="ch" :value="String(ch)">第{{ ch }}章</option>
      </select>
    </div>

    <div class="flex gap-2 px-3 mb-3">
      <button @click="store.selectAll()" class="text-xs text-purple">全选</button>
      <button @click="doPractice" class="text-xs text-purple">练习重做</button>
      <button @click="doRemove" class="text-xs text-red-400">移出错题本</button>
      <button @click="doExport" class="text-xs text-purple ml-auto">导出</button>
    </div>

    <div class="flex-1 overflow-y-auto px-3">
      <LoadingSpinner v-if="store.loading" />
      <EmptyState v-else-if="!store.list.length" msg="暂无错题" />
      <div v-else class="flex flex-col gap-1">
        <div v-for="row in store.list" :key="row.question_id"
          class="flex items-center gap-3 py-2.5 border-b border-gray-50 dark:border-gray-800">
          <input type="checkbox" :checked="store.selected.includes(row.question_id)"
            @change="store.toggleSelect(row.question_id)" class="w-4 h-4 accent-purple" />
          <span class="text-xs text-gray-400 dark:text-gray-500 w-10">{{ row.q_number }}</span>
          <span class="text-xs text-gray-400 dark:text-gray-500 w-10">{{ row.type }}</span>
          <span class="text-sm text-gray-700 dark:text-gray-300 truncate flex-1">{{ row.title }}</span>
        </div>
      </div>
    </div>

    <div class="flex justify-center gap-4 py-3" v-if="store.pagination.total > store.pagination.per">
      <button @click="store.pagination.page--; store.fetchList()" :disabled="store.pagination.page <= 1"
        class="text-sm text-purple disabled:opacity-30">上一页</button>
      <span class="text-sm text-gray-400 dark:text-gray-500">{{ store.pagination.page }}/{{ Math.ceil(store.pagination.total / store.pagination.per) }}</span>
      <button @click="store.pagination.page++; store.fetchList()"
        :disabled="store.pagination.page >= Math.ceil(store.pagination.total / store.pagination.per)"
        class="text-sm text-purple disabled:opacity-30">下一页</button>
    </div>

    <div class="px-3 pb-2"><BottomDisclaimer /></div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWrongStore } from '../stores/wrong'
import BottomDisclaimer from '../components/layout/BottomDisclaimer.vue'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'
import EmptyState from '../components/common/EmptyState.vue'

const router = useRouter()
const store = useWrongStore()
onMounted(() => { store.fetchList() })

function doPractice() {
  if (!store.selected.length) return
  router.push(`/practice/wrong?ids=${store.selected.join(',')}`)
}
async function doRemove() {
  if (!store.selected.length) return
  await store.removeFromWrong(store.selected)
  store.selected = []
  store.fetchList()
}
async function doExport() {
  const blob = await store.exportExcel()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href = url; a.download = '错题.docx'; a.click()
  URL.revokeObjectURL(url)
}
</script>
