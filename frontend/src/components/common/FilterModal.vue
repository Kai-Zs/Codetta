<template>
  <Teleport to="body">
    <Transition enter-active-class="transition duration-200 ease-out" leave-active-class="transition duration-150 ease-in"
      enter-from-class="opacity-0 scale-90" leave-to-class="opacity-0 scale-95">
      <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="$emit('close')">
        <div class="bg-white dark:bg-gray-800 rounded-2xl px-6 py-6 w-72 shadow-xl">
          <h3 class="text-base font-semibold text-gray-800 dark:text-gray-200 mb-4">筛选刷题</h3>
          <div class="mb-4">
            <p class="text-sm text-gray-500 dark:text-gray-400 mb-2">题型</p>
            <div class="flex flex-wrap gap-2">
              <button v-for="t in types" :key="t" @click="toggleType(t)"
                :class="filters.type.includes(t) ? 'bg-purple text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'"
                class="px-3 py-1.5 rounded-lg text-sm transition">{{ t }}</button>
            </div>
          </div>
          <div class="mb-4">
            <p class="text-sm text-gray-500 dark:text-gray-400 mb-2">章节</p>
            <select v-model="filters.chapter" class="w-full border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="">全部章节</option>
              <option v-for="ch in chapters" :key="ch" :value="ch">第{{ ch }}章</option>
            </select>
          </div>
          <div class="mb-6">
            <p class="text-sm text-gray-500 dark:text-gray-400 mb-2">状态</p>
            <div class="flex gap-2">
              <button v-for="s in statuses" :key="s.value" @click="filters.status = s.value"
                :class="filters.status === s.value ? 'bg-purple text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'"
                class="px-3 py-1.5 rounded-lg text-sm transition">{{ s.label }}</button>
            </div>
          </div>
          <button @click="start" class="w-full py-3 bg-purple text-white rounded-xl font-medium">开始刷题</button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { usePracticeStore } from '../../stores/practice'

defineProps({ open: Boolean })
defineEmits(['close'])

const router = useRouter()
const store = usePracticeStore()

const types = ['单选题', '判断题', '填空题', '编程题']
const chapters = ['1', '2', '3', '4', '5', '6', '7', '8']
const statuses = [
  { label: '全部', value: 'all' },
  { label: '未做', value: 'undone' },
  { label: '已做', value: 'done' },
]

const filters = ref({ type: [], chapter: '', status: 'all' })

function toggleType(t) {
  const idx = filters.value.type.indexOf(t)
  if (idx >= 0) filters.value.type.splice(idx, 1)
  else filters.value.type.push(t)
}

function start() {
  store.setFilters({ ...filters.value })
  router.push('/practice/filter')
}
</script>
