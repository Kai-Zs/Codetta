<template>
  <Teleport to="body">
    <Transition enter-active-class="transition-opacity duration-200" leave-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0" leave-to-class="opacity-0">
      <div v-if="visible" :class="['fixed bottom-20 left-1/2 -translate-x-1/2 px-4 py-2 rounded-lg text-white text-sm z-50', bg]">
        {{ message }}
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
const visible = ref(false), message = ref(''), bg = ref('bg-purple')
const show = (msg, type = 'info') => {
  message.value = msg
  bg.value = type === 'error' ? 'bg-red-500' : type === 'success' ? 'bg-green' : 'bg-purple'
  visible.value = true
  setTimeout(() => visible.value = false, 2500)
}
defineExpose({ show })
</script>
