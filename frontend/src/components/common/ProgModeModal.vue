<template>
  <Teleport to="body">
    <Transition enter-active-class="transition-opacity duration-200" leave-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0" leave-to-class="opacity-0">
      <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
        <div class="bg-white rounded-2xl px-6 py-8 w-72 shadow-xl text-center">
          <h3 class="text-base font-semibold text-gray-800 mb-2">编程题模式</h3>
          <p class="text-sm text-gray-500 mb-6">请选择编程题的练习方式</p>
          <button @click="$emit('close', 'write')"
            class="w-full py-3 bg-purple text-white rounded-xl font-medium mb-3">动手写代码</button>
          <button @click="$emit('close', 'review')"
            class="w-full py-3 border border-gray-200 text-gray-600 rounded-xl text-sm">先看思路，再对比答案</button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({ open: Boolean })
defineEmits(['close'])
</script>
