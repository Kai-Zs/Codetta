<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-6 mx-4 max-w-sm w-full shadow-xl">
        <h3 class="text-lg font-semibold text-gray-800 mb-2">编程题模式</h3>
        <p class="text-sm text-gray-500 mb-4">首次遇到编程题，请选择答题模式（后续可在设置修改）</p>
        <div class="space-y-3">
          <button @click="choose('write')" class="w-full p-4 border-2 border-purple/30 rounded-xl hover:border-purple transition text-left">
            <p class="font-medium text-gray-800">动手写代码</p>
            <p class="text-xs text-gray-400 mt-1">在编辑器中直接编写代码</p>
          </button>
          <button @click="choose('review')" class="w-full p-4 border-2 border-purple/30 rounded-xl hover:border-purple transition text-left">
            <p class="font-medium text-gray-800">先看思路，再对比答案</p>
            <p class="text-xs text-gray-400 mt-1">看完题目后展示参考答案</p>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
<script setup>
import { useSettingsStore } from '../../stores/settings'
defineProps({ open: Boolean })
const emit = defineEmits(['close'])
const settings = useSettingsStore()
function choose(mode) {
  settings.progMode = mode
  settings.update()
  emit('close')
}
</script>
