<template>
  <div class="min-h-screen bg-bg flex flex-col">
    <!-- 顶栏 -->
    <header class="flex justify-between items-center px-4 py-3">
      <div></div>
      <button @click="showMenu=!showMenu" class="text-sm text-gray-600">{{ auth.user?.name }}</button>
      <button @click="showSettings=true" class="text-gray-500">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
      </button>
    </header>

    <!-- 进度 -->
    <div class="text-center text-sm text-gray-500 space-x-4 mb-4">
      <span>进度 {{ progress.done }}/{{ progress.total }}</span>
      <span>正确率 {{ progress.accuracy }}%</span>
    </div>

    <!-- 主区域 -->
    <main class="flex-1 flex flex-col items-center justify-center px-4 -mt-16">
      <h1 class="text-4xl font-[Cormorant_Garamond] text-purple mb-12">练笔小筑</h1>
      <button @click="goSequential" class="w-48 py-4 bg-purple text-white rounded-xl text-lg font-medium mb-4 shadow-lg shadow-purple/30 hover:bg-purple/90 transition">顺序刷题</button>
      <button @click="showFilter=true" class="w-48 py-4 border-2 border-purple text-purple rounded-xl text-lg font-medium hover:bg-purple/5 transition">随机抽题</button>
    </main>

    <!-- 底部 -->
    <div class="flex justify-between items-center px-4 pb-6">
      <div class="flex items-center gap-2 text-xs text-gray-400">
        <span>Powered by 凯Z闪</span>
      </div>
    </div>

    <BottomDisclaimer />

    <!-- 用户菜单 -->
    <Teleport to="body">
      <Transition enter-active-class="transition-opacity" leave-active-class="transition-opacity" enter-from-class="opacity-0" leave-to-class="opacity-0">
        <div v-if="showMenu" class="fixed inset-0 z-40" @click="showMenu=false">
          <div class="absolute top-12 right-4 bg-white rounded-xl shadow-lg p-2 min-w-[160px]" @click.stop>
            <button @click="toWrong" class="w-full text-left px-4 py-2 rounded-lg text-sm hover:bg-gray-50">查看我的错题</button>
            <button @click="confirmClear=true;showMenu=false" class="w-full text-left px-4 py-2 rounded-lg text-sm hover:bg-gray-50 text-red-500">清空全部进度</button>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 设置 / 筛选 / 确认 弹窗 -->
    <SettingsPanel :open="showSettings" @close="showSettings=false" />
    <FilterModal :open="showFilter" @close="showFilter=false" @confirm="goRandom" />
    <ConfirmDialog :open="confirmClear" title="清空进度" message="确定要清空全部做题进度吗？此操作不可恢复。" danger @confirm="doClear" @cancel="confirmClear=false" />
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useSettingsStore } from '../stores/settings'
import api from '../api'
import BottomDisclaimer from '../components/layout/BottomDisclaimer.vue'
import SettingsPanel from '../components/common/SettingsPanel.vue'
import FilterModal from '../components/common/FilterModal.vue'
import ConfirmDialog from '../components/common/ConfirmDialog.vue'

const router = useRouter(), auth = useAuthStore(), settings = useSettingsStore()
const showMenu = ref(false), showSettings = ref(false), showFilter = ref(false), confirmClear = ref(false)
const progress = reactive({ done: 0, total: 618, accuracy: 0 })

onMounted(async () => {
  await auth.fetchMe()
  settings.init()
  try { const { data } = await api.get('/progress'); Object.assign(progress, data) } catch {}
})

function goSequential() { router.push('/practice/sequential') }
function goRandom(filters) { router.push({ path: '/practice/random', query: filters }) }
function toWrong() { router.push('/wrong'); showMenu.value = false }
async function doClear() { await api.delete('/progress'); progress.done = 0; progress.accuracy = 0; confirmClear.value = false }
</script>
