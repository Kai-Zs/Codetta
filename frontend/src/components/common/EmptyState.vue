<template>
  <div class="flex flex-col items-center py-16 text-gray-400">
    <p class="text-lg">{{ message }}</p>
    <p v-if="hint" class="text-sm mt-1">{{ hint }}</p>
  </div>
</template>
<script setup>defineProps({ message: String, hint: String })</script>
