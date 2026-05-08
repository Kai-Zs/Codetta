<template>
  <div class="min-h-screen flex items-center justify-center overflow-hidden">
    <BackgroundLayer />
    <div :class="['phone-wrapper', { 'phone-wrapper--editor': hasEditor }]">
      <PhoneShell>
        <router-view />
      </PhoneShell>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import BackgroundLayer from './components/layout/BackgroundLayer.vue'
import PhoneShell from './components/layout/PhoneShell.vue'
import { useThemeStore } from './stores/theme'
import { usePracticeStore } from './stores/practice'

const theme = useThemeStore()
const practice = usePracticeStore()
const hasEditor = computed(() => practice.editorVisible)

onMounted(() => { theme.init() })
</script>
