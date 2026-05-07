<template>
  <div class="flex flex-col min-h-full relative">
    <!-- 顶栏 -->
    <header class="flex justify-end items-center px-4 py-3">
      <div class="relative">
        <button @click="showMenu = !showMenu"
          class="flex items-center gap-2 pl-1 pr-4 py-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full shadow-sm hover:shadow transition">
          <div class="w-7 h-7 rounded-full bg-purple/10 dark:bg-purple/20 flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 text-purple dark:text-purple/80" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
          </div>
          <span class="text-sm text-gray-600 dark:text-gray-300">{{ auth.user?.name || '未登录' }}</span>
        </button>
        <Transition enter-from-class="opacity-0 scale-95" enter-active-class="transition duration-150" leave-to-class="opacity-0 scale-95" leave-active-class="transition duration-100">
          <div v-if="showMenu" @click.stop class="absolute top-full mt-2 left-1/2 -translate-x-1/2 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-100 dark:border-gray-700 py-2 w-40 z-50">
            <button @click="goWrong" class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700">查看我的错题</button>
            <button @click="showMenu = false; confirmClear = true" class="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-gray-50 dark:hover:bg-gray-700">清空全部进度</button>
          </div>
        </Transition>
      </div>
    </header>

    <!-- 菜单遮罩 -->
    <div v-if="showMenu" class="absolute inset-0 z-40" @click="showMenu = false"></div>

    <!-- 进度 -->
    <div class="flex gap-6 justify-center px-4 pb-4">
      <span class="text-sm text-gray-400 dark:text-gray-500">已做 <strong class="text-gray-700 dark:text-gray-200">{{ progress.done }}</strong>/{{ progress.total }}</span>
      <span class="text-sm text-gray-400 dark:text-gray-500">正确率 <strong class="text-gray-700 dark:text-gray-200">{{ progress.accuracy }}%</strong></span>
    </div>

    <!-- 主区域 -->
    <main class="flex-1 flex flex-col items-center justify-center px-4">
      <h1 class="text-2xl font-[Georgia] text-purple tracking-widest mb-1">练笔小筑</h1>
      <p class="text-xs text-gray-400 dark:text-gray-500 tracking-widest mb-1">一题一阶 · 拾级而上</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 tracking-widest mb-12">练习Python · 备战考试</p>
      <button @click="goSequential"
        class="w-48 py-4 bg-purple text-white rounded-xl text-base font-medium mb-3 shadow-lg shadow-purple/25 hover:bg-purple/90 transition">
        顺序刷题
      </button>
      <button @click="showFilter = true"
        class="w-48 py-4 border-2 border-purple text-purple rounded-xl text-base font-medium hover:bg-purple/5 transition">
        随机抽题
      </button>
    </main>

    <!-- 底部 -->
    <div class="flex items-center justify-between px-4 pb-8 pt-4">
      <BottomDisclaimer />
      <div class="flex items-center gap-3 ml-4 flex-shrink-0">
        <!-- 暗黑模式切换 -->
        <button @click="theme.toggle()" class="w-5 h-5 text-gray-300 dark:text-gray-500 hover:text-gray-500 dark:hover:text-gray-400">
          <svg v-if="theme.isDark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
        </button>
        <!-- 设置 -->
        <button @click="showSettings = true" class="w-5 h-5 text-gray-300 hover:text-gray-500">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3"/><circle cx="4" cy="10" r="2"/><circle cx="12" cy="8" r="2"/><circle cx="20" cy="12" r="2"/></svg>
        </button>
      </div>
    </div>

    <!-- 筛选弹窗 -->
    <FilterModal :open="showFilter" @close="showFilter = false" />

    <!-- 设置面板 -->
    <SettingsPanel :open="showSettings" @close="showSettings = false" />

    <!-- 清空进度确认 -->
    <ConfirmDialog :open="confirmClear" msg="确定要清空全部做题进度吗？此操作不可恢复。" @confirm="doClear" @close="confirmClear = false" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useThemeStore } from '../stores/theme'
import api from '../api'
import BottomDisclaimer from '../components/layout/BottomDisclaimer.vue'
import FilterModal from '../components/common/FilterModal.vue'
import SettingsPanel from '../components/common/SettingsPanel.vue'
import ConfirmDialog from '../components/common/ConfirmDialog.vue'

const router = useRouter()
const auth = useAuthStore()
const theme = useThemeStore()

const showMenu = ref(false)
const showFilter = ref(false)
const showSettings = ref(false)
const confirmClear = ref(false)
const progress = reactive({ done: 0, total: 618, accuracy: 0 })

onMounted(async () => {
  await auth.fetchMe()
  try { const { data } = await api.get('/progress'); Object.assign(progress, data) } catch {}
})

function goSequential() { router.push('/practice/sequential') }
function goWrong() { showMenu.value = false; router.push('/wrong') }

async function doClear() {
  confirmClear.value = false
  await api.delete('/progress')
  progress.done = 0
  progress.accuracy = 0
}
</script>
