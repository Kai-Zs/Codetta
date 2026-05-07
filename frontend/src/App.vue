<template>
  <div class="min-h-screen flex items-center justify-center overflow-hidden">
    <BackgroundLayer />
    <PhoneShell>
      <router-view />
    </PhoneShell>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import BackgroundLayer from './components/layout/BackgroundLayer.vue'
import PhoneShell from './components/layout/PhoneShell.vue'
import { useThemeStore } from './stores/theme'

onMounted(() => { useThemeStore().init() })
</script>
