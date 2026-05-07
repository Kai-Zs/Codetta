<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="$emit('close')">
      <div class="bg-white rounded-2xl p-6 mx-4 max-w-lg w-full shadow-xl max-h-[80vh] overflow-y-auto">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">答题卡</h3>
        <div class="flex flex-wrap gap-2">
          <button v-for="item in items" :key="item.id" @click="$emit('jump', item.id)"
            class="w-8 h-8 rounded-full text-xs font-medium border-2 transition"
            :class="{
              'bg-green border-green text-white': item.status === 'correct',
              'bg-red-500 border-red-500 text-white': item.status === 'incorrect',
              'bg-yellow-400 border-yellow-400 text-white': item.status === 'partial',
              'border-gray-200 text-gray-400': !item.status,
              'ring-2 ring-purple ring-offset-1': item.id === currentId,
            }">
            {{ item.label }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
<script setup>
defineProps({ open: Boolean, items: Array, currentId: Number })
defineEmits(['close', 'jump'])
</script>
