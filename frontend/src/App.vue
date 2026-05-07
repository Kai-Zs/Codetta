<template>
  <div class="min-h-screen flex items-center justify-center overflow-hidden">
    <BackgroundLayer />
    <PhoneShell>
      <router-view />
    </PhoneShell>
  </div>
</template>

<script setup>
import BackgroundLayer from './components/layout/BackgroundLayer.vue'
import PhoneShell from './components/layout/PhoneShell.vue'
</script>
