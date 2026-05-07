<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 bg-black/40 flex items-end md:items-center justify-center z-50" @click.self="$emit('close')">
      <div class="bg-white rounded-t-2xl md:rounded-2xl p-6 w-full md:max-w-sm shadow-xl">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">设置</h3>
        <div class="space-y-4">
          <div>
            <p class="text-sm text-gray-500 mb-2">编程题模式</p>
            <div class="flex gap-2">
              <button @click="settings.progMode='write';save()" :class="['px-3 py-1 rounded-lg text-sm', settings.progMode==='write' ? 'bg-purple text-white' : 'bg-gray-100']">动手写</button>
              <button @click="settings.progMode='review';save()" :class="['px-3 py-1 rounded-lg text-sm', settings.progMode==='review' ? 'bg-purple text-white' : 'bg-gray-100']">看思路</button>
            </div>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-500">声音反馈</span>
            <button @click="settings.soundOn=!settings.soundOn;save()" :class="['w-11 h-6 rounded-full transition', settings.soundOn ? 'bg-purple' : 'bg-gray-300']">
              <div :class="['w-5 h-5 rounded-full bg-white shadow transition', settings.soundOn ? 'translate-x-6' : 'translate-x-0.5']" />
            </button>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-500">震动反馈</span>
            <button @click="settings.vibrateOn=!settings.vibrateOn;save()" :class="['w-11 h-6 rounded-full transition', settings.vibrateOn ? 'bg-purple' : 'bg-gray-300']">
              <div :class="['w-5 h-5 rounded-full bg-white shadow transition', settings.vibrateOn ? 'translate-x-6' : 'translate-x-0.5']" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
<script setup>
import { useSettingsStore } from '../../stores/settings'
const settings = useSettingsStore()
defineProps({ open: Boolean })
defineEmits(['close'])
async function save() { await settings.update() }
</script>
