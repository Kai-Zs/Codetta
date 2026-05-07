<template>
  <Teleport to="body">
    <Transition enter-active-class="transition-opacity duration-200" leave-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0" leave-to-class="opacity-0">
      <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="$emit('close')">
        <div class="bg-white rounded-2xl px-6 py-6 w-72 shadow-xl">
          <p class="text-sm text-gray-700 mb-6 text-center">{{ msg }}</p>
          <div class="flex gap-3">
            <button @click="$emit('close')" class="flex-1 py-2.5 border border-gray-200 rounded-lg text-sm text-gray-500">取消</button>
            <button @click="$emit('confirm')" class="flex-1 py-2.5 bg-red-500 text-white rounded-lg text-sm font-medium">确认</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({ open: Boolean, msg: String })
defineEmits(['confirm', 'close'])
</script>
