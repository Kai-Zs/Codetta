<template>
  <Teleport to="body">
    <Transition enter-active-class="transition-opacity duration-200" leave-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0" leave-to-class="opacity-0">
      <div v-if="open" class="fixed inset-0 z-50 flex items-end justify-center bg-black/40" @click.self="$emit('close')">
        <div class="bg-white dark:bg-gray-800 rounded-t-2xl px-6 py-6 w-full max-w-sm">
          <h3 class="text-base font-semibold text-gray-800 dark:text-gray-200 mb-4">答题卡</h3>
          <div class="flex flex-wrap gap-2 max-h-64 overflow-y-auto">
            <button v-for="item in items" :key="item.id" @click="$emit('jump', item.id)"
              :class="[
                'w-8 h-8 rounded-full text-xs font-medium transition',
                item.id === currentId ? 'ring-2 ring-purple ring-offset-1 dark:ring-offset-gray-800' : '',
                item.status === 'correct' ? 'bg-green text-white' :
                item.status === 'incorrect' || item.status === 'partial' ? 'bg-red-400 text-white' :
                'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
              ]">
              {{ item.label }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({ open: Boolean, items: Array, currentId: [Number, null] })
defineEmits(['close', 'jump'])
</script>
