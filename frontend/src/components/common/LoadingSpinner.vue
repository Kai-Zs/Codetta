<template>
  <div v-if="show" class="flex justify-center py-12">
    <div class="w-8 h-8 border-4 border-purple/30 border-t-purple rounded-full animate-spin"></div>
  </div>
</template>
<script setup>defineProps({ show: Boolean })</script>
