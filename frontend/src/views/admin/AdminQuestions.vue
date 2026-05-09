<template>
  <div>
    <!-- 搜索栏 -->
    <div class="flex gap-2 mb-4">
      <input v-model="q_number" placeholder="题号" @keyup.enter="search"
        class="w-28 px-3 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-lg text-sm dark:text-gray-200" />
      <select v-model="type" @change="search" class="px-3 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-lg text-sm dark:text-gray-200">
        <option value="">全部题型</option>
        <option v-for="t in types" :key="t" :value="t">{{ t }}</option>
      </select>
      <select v-model="chapter" @change="search" class="px-3 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-lg text-sm dark:text-gray-200">
        <option value="">全部章节</option>
        <option v-for="c in chapters" :key="c" :value="c">第{{ c }}章</option>
      </select>
      <button @click="search" class="px-4 py-2 bg-purple text-white rounded-lg text-sm">搜索</button>
    </div>

    <!-- 表格 -->
    <div class="overflow-auto">
      <table class="w-full text-sm text-left">
        <thead>
          <tr class="border-b border-gray-100 dark:border-gray-700 text-gray-500 dark:text-gray-400">
            <th class="py-2 pr-2 w-16">题号</th><th class="py-2 pr-2 w-16">题型</th><th class="py-2 pr-2">标题</th><th class="py-2 pr-2 w-14">状态</th><th class="py-2 w-24">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="q in list" :key="q.id" class="border-b border-gray-50 dark:border-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800">
            <td class="py-2 pr-2 text-xs">{{ q.q_number }}</td>
            <td class="py-2 pr-2 text-xs">{{ q.type }}</td>
            <td class="py-2 pr-2 text-xs truncate max-w-48">{{ q.title || '(无标题)' }}</td>
            <td class="py-2 pr-2"><span :class="q.is_active ? 'text-green' : 'text-red-400'" class="text-xs">{{ q.is_active ? '启用' : '停用' }}</span></td>
            <td class="py-2 text-xs flex gap-1">
              <button @click="edit(q)" class="text-purple hover:underline">编辑</button>
              <button @click="toggle(q)" class="text-red-400 hover:underline">{{ q.is_active ? '停用' : '启用' }}</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="flex justify-between items-center mt-3 text-xs text-gray-400">
      <span>共 {{ total }} 条</span>
      <div class="flex gap-2">
        <button @click="goPage(page-1)" :disabled="page<=1" class="disabled:opacity-30">&larr;</button>
        <span>{{ page }}/{{ Math.ceil(total/per) || 1 }}</span>
        <button @click="goPage(page+1)" :disabled="page*per>=total" class="disabled:opacity-30">&rarr;</button>
      </div>
    </div>

    <!-- 新增按钮 -->
    <button @click="edit(null)" class="mt-4 px-4 py-2 border border-purple text-purple rounded-lg text-sm">+ 新增题目</button>

    <!-- 编辑弹窗 -->
    <QuestionEditModal v-if="editQ !== undefined" :question="editQ" @close="editQ = undefined; search()" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'
import QuestionEditModal from './QuestionEditModal.vue'

const types = ['单选题', '判断题', '填空题', '编程题']
const chapters = ['1','2','3','4','5','6','7','8']

const q_number = ref(''), type = ref(''), chapter = ref('')
const list = ref([]), page = ref(1), total = ref(0), per = ref(20)
const editQ = ref(undefined)

onMounted(() => search())
async function search() { page.value = 1; await fetchList() }
async function fetchList() {
  const { data } = await api.get('/admin/questions', { params: { q_number: q_number.value, type: type.value, chapter: chapter.value, page: page.value, per: per.value } })
  list.value = data.items; total.value = data.total
}
function goPage(p) { page.value = p; fetchList() }
function edit(q) { editQ.value = q || {} }
async function toggle(q) {
  const newVal = q.is_active ? 0 : 1
  await api.put(`/admin/questions/${q.id}/active?active=${newVal}`)
  q.is_active = newVal
}
</script>
