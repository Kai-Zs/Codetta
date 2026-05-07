<template>
  <Teleport to="body">
    <Transition enter-active-class="transition-opacity duration-200" leave-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0" leave-to-class="opacity-0">
      <div v-if="open" class="fixed inset-0 z-50 flex items-end justify-center bg-black/40" @click.self="$emit('close')">
        <div class="bg-white dark:bg-gray-800 rounded-t-2xl px-6 py-6 w-full max-w-sm">
          <h3 class="text-base font-semibold text-gray-800 dark:text-gray-200 mb-6">设置</h3>
          <div class="mb-6">
            <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">编程题模式</p>
            <div class="flex gap-3">
              <button @click="settings.progMode = 'write'; save()"
                :class="settings.progMode === 'write' ? 'bg-purple text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'"
                class="flex-1 py-2.5 rounded-xl text-sm transition">动手写</button>
              <button @click="settings.progMode = 'review'; save()"
                :class="settings.progMode === 'review' ? 'bg-purple text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'"
                class="flex-1 py-2.5 rounded-xl text-sm transition">看思路</button>
            </div>
          </div>
          <div class="flex items-center justify-between mb-4">
            <span class="text-sm text-gray-600 dark:text-gray-300">声音反馈</span>
            <button @click="settings.soundOn = !settings.soundOn; save()"
              :class="settings.soundOn ? 'bg-purple' : 'bg-gray-200 dark:bg-gray-600'"
              class="w-12 h-7 rounded-full transition relative">
              <span :class="settings.soundOn ? 'translate-x-6' : 'translate-x-1'"
                class="absolute top-0.5 w-6 h-6 bg-white rounded-full shadow transition-transform"></span>
            </button>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">震动反馈</span>
            <button @click="settings.vibrateOn = !settings.vibrateOn; save()"
              :class="settings.vibrateOn ? 'bg-purple' : 'bg-gray-200 dark:bg-gray-600'"
              class="w-12 h-7 rounded-full transition relative">
              <span :class="settings.vibrateOn ? 'translate-x-6' : 'translate-x-1'"
                class="absolute top-0.5 w-6 h-6 bg-white rounded-full shadow transition-transform"></span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { useSettingsStore } from '../../stores/settings'

defineProps({ open: Boolean })
defineEmits(['close'])

const settings = useSettingsStore()

async function save() {
  try { await settings.update() } catch {}
}
</script>
