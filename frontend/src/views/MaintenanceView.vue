<template>
  <div class="min-h-screen flex items-center justify-center overflow-hidden">
    <BackgroundLayer />
    <div class="phone-wrapper z-10">
      <div class="phone-shell flex items-center justify-center">
        <div class="text-center px-8">
          <h1 class="text-2xl font-[Georgia] text-purple tracking-widest mb-3">练笔小筑</h1>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">系统维护中</p>
          <p class="text-xs text-gray-400 dark:text-gray-500">请稍后再试</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import BackgroundLayer from '../components/layout/BackgroundLayer.vue'
</script>
