<template>
  <div class="min-h-screen bg-bg flex flex-col">
    <header class="flex items-center gap-3 px-4 py-3 bg-white border-b border-gray-100">
      <button @click="$router.back()" class="text-gray-500">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <h1 class="font-semibold text-gray-800">错题管理</h1>
    </header>

    <div class="flex gap-2 px-4 py-2">
      <select v-model="store.filters.type" @change="reload" class="px-3 py-1 border border-gray-200 rounded-lg text-sm">
        <option value="">全部题型</option>
        <option v-for="t in types" :key="t" :value="t">{{ t }}</option>
      </select>
      <select v-model="store.filters.chapter" @change="reload" class="px-3 py-1 border border-gray-200 rounded-lg text-sm">
        <option value="">全部章节</option>
        <option v-for="ch in chapters" :key="ch" :value="ch">第{{ ch }}章</option>
      </select>
    </div>

    <div class="flex gap-2 px-4 py-2">
      <button @click="store.selectAll()" class="text-xs px-2 py-1 border border-gray-200 rounded">全选</button>
      <button @click="doRePractice" :disabled="!store.selected.length" class="text-xs px-2 py-1 border border-purple text-purple rounded disabled:opacity-30">练习重做</button>
      <button @click="doRemove" :disabled="!store.selected.length" class="text-xs px-2 py-1 border border-red-500 text-red-500 rounded disabled:opacity-30">移出错题本</button>
      <button @click="doExport" class="text-xs px-2 py-1 border border-gray-200 rounded">导出</button>
    </div>

    <div class="flex-1 px-4 overflow-y-auto">
      <EmptyState v-if="!store.loading && !store.list.length" message="暂无错题，继续保持！" />
      <div v-for="item in store.list" :key="item.question_id" class="flex items-center gap-3 py-2 border-b border-gray-50">
        <input type="checkbox" :checked="store.selected.includes(item.question_id)" @change="store.toggleSelect(item.question_id)" class="accent-purple" />
        <router-link :to="`/wrong/${item.question_id}`" class="flex-1 text-sm">
          <span class="text-gray-400 mr-2">{{ item.q_number }}</span>
          <span class="text-purple text-xs mr-1">[{{ item.type }}]</span>
          <span class="text-gray-700">{{ item.title }}</span>
        </router-link>
      </div>
    </div>

    <div class="flex justify-center gap-4 py-3">
      <button @click="prevPage" :disabled="store.pagination.page<=1" class="text-sm text-gray-400 disabled:opacity-30">上一页</button>
      <span class="text-sm text-gray-500">{{ store.pagination.page }}/{{ Math.ceil(store.pagination.total/store.pagination.per) || 1 }}</span>
      <button @click="nextPage" :disabled="store.pagination.page*store.pagination.per>=store.pagination.total" class="text-sm text-gray-400 disabled:opacity-30">下一页</button>
    </div>

    <BottomDisclaimer />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWrongStore } from '../stores/wrong'
import BottomDisclaimer from '../components/layout/BottomDisclaimer.vue'
import EmptyState from '../components/common/EmptyState.vue'

const router = useRouter()
const store = useWrongStore()
const types = ['单选题', '判断题', '填空题', '编程题']
const chapters = Array.from({length:8}, (_,i)=>String(i+1))

onMounted(() => store.fetchList())
function reload() { store.pagination.page = 1; store.fetchList() }
function prevPage() { store.pagination.page--; store.fetchList() }
function nextPage() { store.pagination.page++; store.fetchList() }
async function doRemove() { await store.removeFromWrong(store.selected); store.selected = []; store.fetchList() }
async function doExport() { const blob = await store.exportExcel(); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = 'wrong_questions.xlsx'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 100) }
function doRePractice() { router.push({ path: '/practice/wrong', query: { ids: store.selected.join(',') } }) }
</script>
