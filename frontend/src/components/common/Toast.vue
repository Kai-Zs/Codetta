<template>
  <Teleport to="body">
    <Transition enter-active-class="transition-opacity duration-200" leave-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0" leave-to-class="opacity-0">
      <div v-if="visible" class="fixed bottom-20 left-1/2 -translate-x-1/2 px-4 py-2 rounded-xl text-white text-sm z-50 bg-purple shadow-lg">
        {{ msg }}
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({ visible: Boolean, msg: String })
</script>
