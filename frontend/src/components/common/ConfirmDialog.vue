<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="$emit('cancel')">
      <div class="bg-white rounded-xl p-6 mx-4 max-w-sm w-full shadow-xl">
        <p class="text-gray-800 mb-2 font-medium">{{ title }}</p>
        <p class="text-gray-500 text-sm mb-6">{{ message }}</p>
        <div class="flex gap-3 justify-end">
          <button @click="$emit('cancel')" class="px-4 py-2 rounded-lg border border-gray-200 text-gray-600">取消</button>
          <button @click="$emit('confirm')" :class="['px-4 py-2 rounded-lg text-white', danger ? 'bg-red-500' : 'bg-purple']">确认</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
<script setup>
defineProps({ open: Boolean, title: String, message: String, danger: Boolean })
defineEmits(['confirm', 'cancel'])
</script>
