<template>
  <div class="min-h-screen flex items-center justify-center overflow-hidden">
    <BackgroundLayer />
    <div :class="['phone-wrapper', { 'phone-wrapper--editor': hasEditor }]">
      <PhoneShell>
        <router-view />
      </PhoneShell>
    </div>
    <!-- 备案信息 -->
    <div class="fixed bottom-0 left-0 right-0 z-0 pb-1.5 text-center pointer-events-none">
      <p class="text-[11px] text-gray-400 dark:text-gray-500 leading-relaxed">
        <a href="https://beian.miit.gov.cn/" target="_blank" class="pointer-events-auto hover:text-gray-500 dark:hover:text-gray-400 transition">晋ICP备2026004314号-1</a>
        &nbsp;
        <img :src="beianIcon" width="14" height="14" class="inline align-text-bottom opacity-60" />
        <a href="https://beian.mps.gov.cn/#/query/webSearch?code=14108102001175" rel="noreferrer" target="_blank" class="pointer-events-auto hover:text-gray-500 dark:hover:text-gray-400 transition">晋公网安备14108102001175号</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import beianIcon from './assets/beian.png'
import BackgroundLayer from './components/layout/BackgroundLayer.vue'
import PhoneShell from './components/layout/PhoneShell.vue'
import { useThemeStore } from './stores/theme'
import { usePracticeStore } from './stores/practice'

const theme = useThemeStore()
const practice = usePracticeStore()
const hasEditor = computed(() => practice.editorVisible)

onMounted(() => { theme.init() })
</script>
