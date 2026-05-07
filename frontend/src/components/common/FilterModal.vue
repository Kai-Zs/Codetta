<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 bg-black/40 flex items-end md:items-center justify-center z-50" @click.self="$emit('close')">
      <div class="bg-white rounded-t-2xl md:rounded-2xl p-6 w-full md:max-w-sm shadow-xl">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">筛选条件</h3>
        <div class="space-y-4">
          <div>
            <p class="text-sm text-gray-500 mb-2">题型</p>
            <div class="flex flex-wrap gap-2">
              <label v-for="t in types" :key="t" class="flex items-center gap-1 text-sm">
                <input type="checkbox" :value="t" v-model="local.type" class="accent-purple" /> {{ t }}
              </label>
            </div>
          </div>
          <div>
            <p class="text-sm text-gray-500 mb-2">章节</p>
            <select v-model="local.chapter" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
              <option value="">全部章节</option>
              <option v-for="ch in chapters" :key="ch" :value="ch">第{{ ch }}章</option>
            </select>
          </div>
          <div>
            <p class="text-sm text-gray-500 mb-2">状态</p>
            <div class="flex gap-3">
              <label v-for="s in statuses" :key="s.value" class="flex items-center gap-1 text-sm">
                <input type="radio" :value="s.value" v-model="local.status" class="accent-purple" /> {{ s.label }}
              </label>
            </div>
          </div>
        </div>
        <button @click="$emit('confirm', local)" class="w-full mt-6 py-3 bg-purple text-white rounded-xl font-medium">开始刷题</button>
      </div>
    </div>
  </Teleport>
</template>
<script setup>
import { ref, watch } from 'vue'
const props = defineProps({ open: Boolean })
defineEmits(['close', 'confirm'])
const types = ['单选题', '判断题', '填空题', '编程题']
const chapters = Array.from({length:8}, (_,i)=>String(i+1))
const statuses = [{label:'未做',value:'undone'},{label:'已做',value:'done'},{label:'全部',value:'all'}]
const local = ref({ type: [], chapter: '', status: 'all' })
watch(() => props.open, (v) => { if (v) local.value = { type: [], chapter: '', status: 'all' } })
</script>
