<template>
  <div class="flex flex-col min-h-full relative">
    <!-- 顶栏 -->
    <header class="flex justify-center items-center px-4 py-3">
      <button @click="showMenu = !showMenu" class="text-sm text-gray-500">{{ auth.user?.name }}</button>
    </header>

    <!-- 进度 -->
    <div class="flex gap-6 justify-center px-4 pb-4">
      <span class="text-sm text-gray-400">已做 <strong class="text-gray-700">{{ progress.done }}</strong>/{{ progress.total }}</span>
      <span class="text-sm text-gray-400">正确率 <strong class="text-gray-700">{{ progress.accuracy }}%</strong></span>
    </div>

    <!-- 主区域 -->
    <main class="flex-1 flex flex-col items-center justify-center px-4">
      <h1 class="text-2xl font-[Georgia] text-purple tracking-widest mb-1">练笔小筑</h1>
      <p class="text-xs text-gray-400 tracking-widest mb-12">一题一阶 · 拾级而上</p>
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
      <button @click="showSettings = true" class="text-gray-300 hover:text-gray-500 ml-4 flex-shrink-0 w-5 h-5">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
        </svg>
      </button>
    </div>

    <!-- 用户名菜单 -->
    <Teleport to="body">
      <Transition enter-from-class="opacity-0 scale-95" enter-active-class="transition duration-150" leave-to-class="opacity-0 scale-95" leave-active-class="transition duration-100">
        <div v-if="showMenu" class="fixed inset-0 z-50" @click="showMenu = false">
          <div class="absolute top-12 right-4 bg-white rounded-xl shadow-lg border border-gray-100 py-2 w-40" @click.stop>
            <button @click="goWrong" class="w-full text-left px-4 py-2 text-sm hover:bg-gray-50">查看我的错题</button>
            <button @click="confirmClear = true" class="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-gray-50">清空全部进度</button>
          </div>
        </div>
      </Transition>
    </Teleport>

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
import api from '../api'
import BottomDisclaimer from '../components/layout/BottomDisclaimer.vue'
import FilterModal from '../components/common/FilterModal.vue'
import SettingsPanel from '../components/common/SettingsPanel.vue'
import ConfirmDialog from '../components/common/ConfirmDialog.vue'

const router = useRouter()
const auth = useAuthStore()

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
