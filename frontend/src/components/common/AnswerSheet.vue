<template>
  <Teleport to="body">
    <Transition enter-active-class="transition duration-200 ease-out" leave-active-class="transition duration-150 ease-in"
      enter-from-class="opacity-0 scale-90" leave-to-class="opacity-0 scale-95">
      <div v-if="open" class="fixed inset-0 z-[110] flex items-center justify-center bg-black/40" @click.self="$emit('close')">
        <div class="answer-sheet-scroll bg-white dark:bg-gray-800 rounded-2xl px-6 py-5 w-80 max-w-[92vw] shadow-xl overflow-y-auto" :style="{ maxHeight: modalMaxH, transition: 'opacity 0.2s ease-out, transform 0.2s ease-out' }">
        <h3 class="text-base font-semibold text-gray-800 dark:text-gray-200 mb-4 text-center">答题卡</h3>
        <div>
          <template v-for="(group, ch, idx) in groupedItems" :key="ch">
            <div v-if="idx > 0" class="border-t border-gray-100 dark:border-gray-700 my-3"></div>
            <p class="text-xs text-gray-400 dark:text-gray-500 mb-2">第{{ ch }}章</p>
            <div class="grid grid-cols-[repeat(auto-fill,minmax(24px,1fr))] gap-1.5 px-1 justify-items-center">
              <button v-for="item in group" :key="item.id" :ref="el => setBtnRef(item.id, el)" @click="$emit('jump', item.id)"
                :class="[
                  'w-6 h-6 rounded-full text-[10px] font-medium transition flex items-center justify-center',
                  item.id === currentId ? 'ring-2 ring-purple ring-offset-1 dark:ring-offset-gray-800' : '',
                  item.status === 'correct' ? 'bg-green text-white' :
                  item.status === 'incorrect' || item.status === 'partial' ? 'bg-red-400 text-white' :
                  'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
                ]"
                :title="item.label">
                <span class="leading-none">{{ item.label.split('.')[1] }}</span>
              </button>
            </div>
          </template>
        </div>
      </div>
    </div>
  </Transition>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch, nextTick } from 'vue'

const props = defineProps({ open: Boolean, items: Array, currentId: [Number, null] })
defineEmits(['close', 'jump'])

const modalMaxH = ref('88vh')
const btnRefs = {}

function setBtnRef(id, el) { if (el) btnRefs[id] = el }

watch(() => props.open, (val) => {
  if (val) {
    nextTick(() => {
      const phone = document.querySelector('.phone-shell')
      if (phone) modalMaxH.value = (phone.getBoundingClientRect().height - 32) + 'px'
      // 滚动到当前题目
      if (props.currentId && btnRefs[props.currentId]) {
        btnRefs[props.currentId].scrollIntoView({ block: 'center', behavior: 'instant' })
      }
    })
  }
})

const groupedItems = computed(() => {
  const groups = {}
  for (const item of props.items || []) {
    const ch = item.chapter || '?'
    if (!groups[ch]) groups[ch] = []
    groups[ch].push(item)
  }
  return groups
})
</script>
