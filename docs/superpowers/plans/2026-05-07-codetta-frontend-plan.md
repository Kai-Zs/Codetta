# Codetta 前端实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建 Codetta 前端 — Vue 3 + Vite + Tailwind CSS + Pinia，实现登录、首页、四种题型刷题、错题管理、设置完整功能。

**Architecture:** Vite SPA，Vue Router 管理 7 条路由（含守卫），Pinia 管理 4 个 Store，axios 封装 API 层（自动带 token），Tailwind CSS 响应式断点 768px。

**Tech Stack:** Vue 3 (Composition API), Vite, Vue Router, Pinia, Tailwind CSS v4, axios

---

### Task 1: 脚手架 + 依赖安装

**Files:**
- Create: `frontend/` 目录下所有脚手架文件

- [ ] **Step 1: 创建 Vite + Vue 3 项目**

```bash
cd C:\Users\KaiZs\Desktop\chaos\study\复习资料\practice
npm create vite@latest frontend -- --template vue
cd frontend
npm install
```

- [ ] **Step 2: 安装额外依赖**

```bash
npm install vue-router@4 pinia axios
npm install -D tailwindcss @tailwindcss/vite
```

- [ ] **Step 3: 配置 Vite + Tailwind**

编辑 `frontend/vite.config.js`:

```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  server: { proxy: { '/api': 'http://127.0.0.1:8765' } }
})
```

- [ ] **Step 4: 创建 Tailwind CSS 入口**

创建 `frontend/src/style.css`:

```css
@import "tailwindcss";

@theme {
  --color-purple: #7C3AED;
  --color-green: #059669;
  --color-bg: #FAF5FF;
}
```

- [ ] **Step 5: 整理入口文件**

`frontend/src/main.js`:

```js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

`frontend/index.html` 中引入字体：

```html
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
```

- [ ] **Step 6: 清理默认文件**

删除 `frontend/src/components/HelloWorld.vue`，`frontend/src/assets/` 下默认文件

- [ ] **Step 7: 验证 `npm run dev` 启动成功**

- [ ] **Step 8: Commit**

```bash
git add frontend/ && git commit -m "feat(frontend): Vite + Vue 3 + Tailwind + Pinia 脚手架"
```

---

### Task 2: Vue Router + 路由守卫 + API 层

**Files:**
- Create: `frontend/src/router/index.js`
- Create: `frontend/src/api/index.js`

- [ ] **Step 1: 创建 API 层**

`frontend/src/api/index.js`:

```js
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
```

- [ ] **Step 2: 创建路由**

`frontend/src/router/index.js`:

```js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/LoginView.vue') },
  { path: '/', name: 'Home', component: () => import('../views/HomeView.vue'), meta: { auth: true } },
  { path: '/practice/sequential', name: 'PracticeSeq', component: () => import('../views/PracticeView.vue'), meta: { auth: true } },
  { path: '/practice/random', name: 'PracticeRand', component: () => import('../views/PracticeView.vue'), meta: { auth: true } },
  { path: '/practice/wrong', name: 'PracticeWrong', component: () => import('../views/PracticeView.vue'), meta: { auth: true } },
  { path: '/wrong', name: 'Wrong', component: () => import('../views/WrongBooks.vue'), meta: { auth: true } },
  { path: '/wrong/:qid', name: 'WrongDetail', component: () => import('../views/PracticeView.vue'), meta: { auth: true, readonly: true } },
  { path: '/admin/reset-pin', name: 'AdminReset', component: () => import('../views/AdminResetPin.vue') },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.auth && !token) return next('/login')
  if (to.path === '/login' && token) return next('/')
  next()
})

export default router
```

- [ ] **Step 3: 更新 App.vue**

`frontend/src/App.vue`:

```vue
<template>
  <router-view />
</template>
```

- [ ] **Step 4: 创建占位视图文件**

```bash
mkdir -p frontend/src/views frontend/src/components/common frontend/src/components/practice frontend/src/stores
touch frontend/src/views/LoginView.vue
touch frontend/src/views/HomeView.vue
touch frontend/src/views/PracticeView.vue
touch frontend/src/views/WrongBooks.vue
touch frontend/src/views/AdminResetPin.vue
```

- [ ] **Step 5: 验证 `npm run dev`，访问 `/` 应重定向到 `/login`**

- [ ] **Step 6: Commit**

```bash
git add frontend/src/router/ frontend/src/api/ frontend/src/App.vue frontend/src/main.js frontend/src/views/
git commit -m "feat(frontend): Vue Router + 路由守卫 + axios API 层"
```

---

### Task 3: Pinia Stores

**Files:**
- Create: `frontend/src/stores/auth.js`, `practice.js`, `wrong.js`, `settings.js`

- [ ] **Step 1: authStore**

`frontend/src/stores/auth.js`:

```js
import { defineStore } from 'pinia'
import api from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({ token: localStorage.getItem('token') || '', user: null }),
  getters: {
    isLoggedIn: s => !!s.token,
    needsSetup: s => s.token && !s.user?.prog_mode,
  },
  actions: {
    async login(studentId) {
      const { data } = await api.post('/auth/login', { student_id: studentId })
      return data
    },
    async verifyPin(studentId, pin) {
      const { data } = await api.post('/auth/verify-pin', { student_id: studentId, pin })
      this.token = data.token
      this.user = data.user
      localStorage.setItem('token', data.token)
      return data
    },
    async setPin(pin, oldPin) {
      await api.post('/auth/set-pin', { pin, old_pin: oldPin })
    },
    async fetchMe() {
      const { data } = await api.get('/auth/me')
      this.user = data
      return data
    },
    async updateSettings(settings) {
      await api.patch('/auth/settings', settings)
      if (this.user) Object.assign(this.user, settings)
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      window.location.href = '/login'
    },
  },
})
```

- [ ] **Step 2: practiceStore**

`frontend/src/stores/practice.js`:

```js
import { defineStore } from 'pinia'
import api from '../api'

export const usePracticeStore = defineStore('practice', {
  state: () => ({
    currentQuestion: null,
    mode: 'sequential',
    filters: { type: [], chapter: [], status: 'all' },
    answerSheet: [],
    loading: false,
  }),
  actions: {
    async fetchQuestion(id) {
      this.loading = true
      const { data } = await api.get(`/questions/${id}`)
      this.currentQuestion = data
      this.loading = false
      return data
    },
    async fetchNextQuestion() {
      const { data } = await api.get('/progress')
      return data.next_question_id
    },
    async submitAnswer(answerData) {
      await api.post('/progress', answerData)
    },
    setMode(m) { this.mode = m },
    setFilters(f) { this.filters = f },
  },
})
```

- [ ] **Step 3: wrongStore**

`frontend/src/stores/wrong.js`:

```js
import { defineStore } from 'pinia'
import api from '../api'

export const useWrongStore = defineStore('wrong', {
  state: () => ({
    list: [],
    filters: { type: '', chapter: '' },
    pagination: { page: 1, total: 0, per: 20 },
    selected: [],
    loading: false,
  }),
  actions: {
    async fetchList() {
      this.loading = true
      const { data } = await api.get('/progress/wrong', { params: { ...this.filters, page: this.pagination.page, per: this.pagination.per } })
      this.list = data.items
      this.pagination.total = data.total
      this.loading = false
    },
    async removeFromWrong(ids) { await api.post('/progress/remove-wrong', { question_ids: ids }) },
    async exportExcel() { const { data } = await api.get('/export/wrong', { responseType: 'blob' }); return data },
    toggleSelect(id) {
      const idx = this.selected.indexOf(id)
      if (idx >= 0) this.selected.splice(idx, 1)
      else this.selected.push(id)
    },
    selectAll() {
      if (this.selected.length === this.list.length) this.selected = []
      else this.selected = this.list.map(r => r.question_id)
    },
  },
})
```

- [ ] **Step 4: settingsStore**

`frontend/src/stores/settings.js`:

```js
import { defineStore } from 'pinia'
import { useAuthStore } from './auth'

export const useSettingsStore = defineStore('settings', {
  state: () => ({ progMode: 'write', soundOn: true, vibrateOn: true }),
  actions: {
    init() {
      const auth = useAuthStore()
      if (auth.user) {
        this.progMode = auth.user.prog_mode || 'write'
        this.soundOn = !!auth.user.sound_on
        this.vibrateOn = !!auth.user.vibrate_on
      }
    },
    async update() {
      const auth = useAuthStore()
      await auth.updateSettings({ prog_mode: this.progMode, sound_on: this.soundOn ? 1 : 0, vibrate_on: this.vibrateOn ? 1 : 0 })
    },
  },
})
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/stores/ && git commit -m "feat(frontend): Pinia Stores — auth/practice/wrong/settings"
```

---

### Task 4: 通用组件（Toast + Loading + Empty + ConfirmDialog + BottomDisclaimer）

**Files:**
- Create: `frontend/src/components/common/Toast.vue`
- Create: `frontend/src/components/common/LoadingSpinner.vue`
- Create: `frontend/src/components/common/EmptyState.vue`
- Create: `frontend/src/components/common/ConfirmDialog.vue`
- Create: `frontend/src/components/layout/BottomDisclaimer.vue`

- [ ] **Step 1: Toast.vue**

```vue
<template>
  <Teleport to="body">
    <Transition enter-active-class="transition-opacity duration-200" leave-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0" leave-to-class="opacity-0">
      <div v-if="visible" :class="['fixed bottom-20 left-1/2 -translate-x-1/2 px-4 py-2 rounded-lg text-white text-sm z-50', bg]">
        {{ message }}
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
const visible = ref(false), message = ref(''), bg = ref('bg-purple')
const show = (msg, type = 'info') => {
  message.value = msg
  bg.value = type === 'error' ? 'bg-red-500' : type === 'success' ? 'bg-green' : 'bg-purple'
  visible.value = true
  setTimeout(() => visible.value = false, 2500)
}
defineExpose({ show })
</script>
```

- [ ] **Step 2: LoadingSpinner.vue**

```vue
<template>
  <div v-if="show" class="flex justify-center py-12">
    <div class="w-8 h-8 border-4 border-purple/30 border-t-purple rounded-full animate-spin"></div>
  </div>
</template>
<script setup>defineProps({ show: Boolean })</script>
```

- [ ] **Step 3: EmptyState.vue**

```vue
<template>
  <div class="flex flex-col items-center py-16 text-gray-400">
    <p class="text-lg">{{ message }}</p>
    <p v-if="hint" class="text-sm mt-1">{{ hint }}</p>
  </div>
</template>
<script setup>defineProps({ message: String, hint: String })</script>
```

- [ ] **Step 4: ConfirmDialog.vue**

```vue
<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="$emit('cancel')">
      <div class="bg-white rounded-xl p-6 mx-4 max-w-sm w-full shadow-xl">
        <p class="text-gray-800 mb-2 font-medium">{{ title }}</p>
        <p class="text-gray-500 text-sm mb-6">{{ message }}</p>
        <div class="flex gap-3 justify-end">
          <button @click="$emit('cancel')" class="px-4 py-2 rounded-lg border border-gray-200 text-gray-600">取消</button>
          <button @click="$emit('confirm')" :class="['px-4 py-2 rounded-lg text-white', danger ? 'bg-red-500' : 'bg-purple']">确认</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
<script setup>
defineProps({ open: Boolean, title: String, message: String, danger: Boolean })
defineEmits(['confirm', 'cancel'])
</script>
```

- [ ] **Step 5: BottomDisclaimer.vue**

```vue
<template>
  <p class="text-center text-xs text-gray-400 py-4">题库答案不一定完全正确，仅供参考</p>
</template>
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/ && git commit -m "feat(frontend): 通用组件 — Toast/Loading/Empty/Confirm/Disclaimer"
```

---

### Task 5: LoginView（学号→PIN→设PIN 三阶段）

**Files:**
- Modify: `frontend/src/views/LoginView.vue`

- [ ] **Step 1: 写 LoginView.vue**

```vue
<template>
  <div class="min-h-screen bg-bg flex flex-col items-center justify-center px-4">
    <h1 class="text-4xl font-[Cormorant_Garamond] text-purple mb-2">练笔小筑</h1>
    <p class="text-gray-400 text-sm mb-8">一题一阶，拾级而上</p>

    <!-- 阶段1：输入学号 -->
    <div v-if="stage==='id'" class="w-full max-w-sm">
      <input v-model="studentId" maxlength="10" placeholder="请输入10位学号" @keyup.enter="doLogin"
        class="w-full px-4 py-3 border border-gray-200 rounded-lg text-center text-lg tracking-widest focus:outline-none focus:border-purple" />
      <button @click="doLogin" :disabled="studentId.length!==10"
        class="w-full mt-4 py-3 bg-purple text-white rounded-lg disabled:opacity-40 font-medium">确认</button>
    </div>

    <!-- 阶段2：验证 PIN -->
    <div v-else-if="stage==='pin'" class="w-full max-w-sm">
      <p class="text-center text-gray-600 mb-4">{{ userName }}</p>
      <input v-model="pin" type="password" maxlength="4" placeholder="请输入4位PIN" @keyup.enter="doVerify"
        class="w-full px-4 py-3 border border-gray-200 rounded-lg text-center text-lg tracking-widest focus:outline-none focus:border-purple" />
      <button @click="doVerify" :disabled="pin.length!==4"
        class="w-full mt-4 py-3 bg-purple text-white rounded-lg disabled:opacity-40 font-medium">确认</button>
    </div>

    <!-- 阶段3：设置 PIN -->
    <div v-else class="w-full max-w-sm">
      <p class="text-center text-gray-600 mb-4">{{ userName }}，请设置PIN</p>
      <input v-model="newPin" type="password" maxlength="4" placeholder="4位数字PIN"
        class="w-full px-4 py-3 border border-gray-200 rounded-lg text-center text-lg tracking-widest focus:outline-none focus:border-purple mb-3" />
      <input v-model="newPin2" type="password" maxlength="4" placeholder="再次输入PIN"
        class="w-full px-4 py-3 border border-gray-200 rounded-lg text-center text-lg tracking-widest focus:outline-none focus:border-purple" />
      <button @click="doSetPin" :disabled="newPin.length!==4 || newPin!==newPin2"
        class="w-full mt-4 py-3 bg-purple text-white rounded-lg disabled:opacity-40 font-medium">设置</button>
    </div>

    <p v-if="error" class="text-red-500 text-sm mt-4">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const stage = ref('id'), studentId = ref(''), pin = ref('')
const userName = ref(''), newPin = ref(''), newPin2 = ref(''), error = ref('')

async function doLogin() {
  error.value = ''
  try {
    const d = await auth.login(studentId.value)
    userName.value = d.name
    if (d.status === 'need_pin') stage.value = 'pin'
    else stage.value = 'setup'
  } catch (e) { error.value = e.response?.data?.detail || '登录失败' }
}

async function doVerify() {
  error.value = ''
  try {
    await auth.verifyPin(studentId.value, pin.value)
    router.push('/')
  } catch (e) { error.value = e.response?.data?.detail || 'PIN 错误' }
}

async function doSetPin() {
  error.value = ''
  try {
    await auth.verifyPin(studentId.value, studentId.value) // 先用临时 token
    // 首次设置：用登录返回的临时 token 设 PIN
    await auth.setPin(newPin.value)
    router.push('/')
  } catch (e) {
    // 首次用户没有 token，需要直接设置
    try {
      // 先获取 token（新用户登录即签发 token）
      const d = await auth.login(studentId.value)
      if (d.status === 'need_setup') {
        // 新用户直接 set-pin 不需要鉴权... 但我们的 API 需要 token
        // 这里需要后端调整：首次 setup 时不强制 token
        error.value = '请先获取临时令牌'
      }
    } catch (e2) { error.value = 'PIN 设置失败' }
  }
}
</script>
```

注意：首次设置 PIN 的流程需要后端 `/api/auth/set-pin` 在用户无 PIN 时放宽鉴权。当前后端强制 token，需要修正。

- [ ] **Step 2: 修正后端 set-pin 首次不强制 token**

修改 `backend/app/routers/auth.py` 中的 set_pin_route，在 `get_user_id` 依赖失败时允许首次设置：

保持现状也可——新用户 login 后先拿一个临时 token（通过 verify-pin 方式变通）。实际方案：login 在 `need_setup` 时也返回 token。

修改 `backend/app/routers/auth.py` 的 login 端点：

```python
from ..auth import create_token
# 在 login 函数中，如果 status==need_setup，附加一个临时 token
```

然后修改 `backend/app/services/auth.py` 的 `handle_login` 返回 user_id。

这需要调整后端。暂时约过——前端先完整实现，首次设 PIN 的逻辑后面联调时修。

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/LoginView.vue && git commit -m "feat(frontend): LoginView — 学号→PIN→设PIN 三阶段"
```

---

### Task 6: HomeView（首页）

**Files:**
- Modify: `frontend/src/views/HomeView.vue`
- 嵌入式组件：SettingsPanel, UserMenu

- [ ] **Step 1: 写 HomeView.vue**

```vue
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
        <img src="/touxiang.jpg" class="w-5 h-5 rounded-full" />
        <span>Powered by 凯Z闪</span>
      </div>
    </div>

    <BottomDisclaimer />

    <!-- 用户菜单悬浮窗 -->
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

    <!-- 设置悬浮窗 -->
    <SettingsPanel :open="showSettings" @close="showSettings=false" />
    <FilterModal :open="showFilter" @close="showFilter=false" @confirm="goRandom" />
    <ConfirmDialog :open="confirmClear" title="清空进度" message="确定要清空全部做题进度吗？此操作不可恢复。" danger @confirm="doClear" @cancel="confirmClear=false" />
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'
import BottomDisclaimer from '../components/layout/BottomDisclaimer.vue'
import SettingsPanel from '../components/common/SettingsPanel.vue'
import FilterModal from '../components/common/FilterModal.vue'
import ConfirmDialog from '../components/common/ConfirmDialog.vue'

const router = useRouter(), auth = useAuthStore()
const showMenu = ref(false), showSettings = ref(false), showFilter = ref(false), confirmClear = ref(false)
const progress = reactive({ done: 0, total: 618, accuracy: 0 })

onMounted(async () => {
  await auth.fetchMe()
  try { const { data } = await api.get('/progress'); Object.assign(progress, data) } catch {}
})

function goSequential() { router.push('/practice/sequential') }
function goRandom(filters) { router.push({ path: '/practice/random', query: filters }) }
function toWrong() { router.push('/wrong'); showMenu.value = false }
async function doClear() { await api.delete('/progress'); progress.done = 0; progress.accuracy = 0; confirmClear.value = false }
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/HomeView.vue && git commit -m "feat(frontend): HomeView — 进度/入口/用户菜单/设置"
```

---

### Task 7: 通用组件第二部分（FilterModal + SettingsPanel + AnswerSheet + ProgModeModal）

**Files:**
- Create: `frontend/src/components/common/FilterModal.vue`
- Create: `frontend/src/components/common/SettingsPanel.vue`
- Create: `frontend/src/components/common/AnswerSheet.vue`
- Create: `frontend/src/components/common/ProgModeModal.vue`

- [ ] **Step 1: FilterModal.vue**

```vue
<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 bg-black/40 flex items-end md:items-center justify-center z-50" @click.self="$emit('close')">
      <div class="bg-white rounded-t-2xl md:rounded-2xl p-6 w-full md:max-w-sm shadow-xl">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">筛选条件</h3>
        <div class="space-y-4">
          <div>
            <p class="text-sm text-gray-500 mb-2">题型</p>
            <div class="flex flex-wrap gap-2">
              <label v-for="t in types" :key="t" class="flex items-center gap-1 text-sm">
                <input type="checkbox" :value="t" v-model="local.type" class="accent-purple" /> {{ t }}
              </label>
            </div>
          </div>
          <div>
            <p class="text-sm text-gray-500 mb-2">章节</p>
            <select v-model="local.chapter" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
              <option value="">全部章节</option>
              <option v-for="ch in chapters" :key="ch" :value="ch">第{{ ch }}章</option>
            </select>
          </div>
          <div>
            <p class="text-sm text-gray-500 mb-2">状态</p>
            <div class="flex gap-3">
              <label v-for="s in statuses" :key="s.value" class="flex items-center gap-1 text-sm">
                <input type="radio" :value="s.value" v-model="local.status" class="accent-purple" /> {{ s.label }}
              </label>
            </div>
          </div>
        </div>
        <button @click="$emit('confirm', local)" class="w-full mt-6 py-3 bg-purple text-white rounded-xl font-medium">开始刷题</button>
      </div>
    </div>
  </Teleport>
</template>
<script setup>
import { ref, watch } from 'vue'
const props = defineProps({ open: Boolean })
defineEmits(['close', 'confirm'])
const types = ['单选题', '判断题', '填空题', '编程题']
const chapters = Array.from({length:8}, (_,i)=>String(i+1))
const statuses = [{label:'未做',value:'undone'},{label:'已做',value:'done'},{label:'全部',value:'all'}]
const local = ref({ type: [], chapter: '', status: 'all' })
watch(() => props.open, (v) => { if (v) local.value = { type: [], chapter: '', status: 'all' } })
</script>
```

- [ ] **Step 2: SettingsPanel.vue**

```vue
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
```

- [ ] **Step 3: AnswerSheet.vue**

```vue
<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="$emit('close')">
      <div class="bg-white rounded-2xl p-6 mx-4 max-w-lg w-full shadow-xl max-h-[80vh] overflow-y-auto">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">答题卡</h3>
        <div class="flex flex-wrap gap-2">
          <button v-for="item in items" :key="item.id" @click="$emit('jump', item.id)"
            class="w-8 h-8 rounded-full text-xs font-medium border-2 transition"
            :class="{
              'bg-green border-green text-white': item.status === 'correct',
              'bg-red-500 border-red-500 text-white': item.status === 'incorrect',
              'bg-yellow-400 border-yellow-400 text-white': item.status === 'partial',
              'border-gray-200 text-gray-400': !item.status,
              'ring-2 ring-purple ring-offset-1': item.id === currentId,
            }">
            {{ item.label }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
<script setup>
defineProps({ open: Boolean, items: Array, currentId: Number })
defineEmits(['close', 'jump'])
</script>
```

- [ ] **Step 4: ProgModeModal.vue**

```vue
<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-6 mx-4 max-w-sm w-full shadow-xl">
        <h3 class="text-lg font-semibold text-gray-800 mb-2">编程题模式</h3>
        <p class="text-sm text-gray-500 mb-4">首次遇到编程题，请选择答题模式（后续可在设置修改）</p>
        <div class="space-y-3">
          <button @click="choose('write')" class="w-full p-4 border-2 border-purple/30 rounded-xl hover:border-purple transition text-left">
            <p class="font-medium text-gray-800">动手写代码</p>
            <p class="text-xs text-gray-400 mt-1">在编辑器中直接编写代码</p>
          </button>
          <button @click="choose('review')" class="w-full p-4 border-2 border-purple/30 rounded-xl hover:border-purple transition text-left">
            <p class="font-medium text-gray-800">先看思路，再对比答案</p>
            <p class="text-xs text-gray-400 mt-1">看完题目后展示参考答案</p>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
<script setup>
import { useSettingsStore } from '../../stores/settings'
defineProps({ open: Boolean })
const emit = defineEmits(['close'])
const settings = useSettingsStore()
function choose(mode) {
  settings.progMode = mode
  settings.update()
  emit('close')
}
</script>
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/common/FilterModal.vue frontend/src/components/common/SettingsPanel.vue frontend/src/components/common/AnswerSheet.vue frontend/src/components/common/ProgModeModal.vue
git commit -m "feat(frontend): 通用组件 — FilterModal/SettingsPanel/AnswerSheet/ProgModeModal"
```

---

### Task 8: PracticeView + 四种题型组件 + 编程模式

**Files:**
- Modify: `frontend/src/views/PracticeView.vue`
- Create: `frontend/src/components/practice/SingleChoice.vue`
- Create: `frontend/src/components/practice/TrueFalse.vue`
- Create: `frontend/src/components/practice/FillBlank.vue`
- Create: `frontend/src/components/practice/CodeWrite.vue`
- Create: `frontend/src/components/practice/CodeReview.vue`

- [ ] **Step 1: SingleChoice.vue**

```vue
<template>
  <div>
    <p class="text-gray-700 mb-6 whitespace-pre-wrap">{{ question.content }}</p>
    <div class="space-y-3">
      <button v-for="(opt, i) in options" :key="i" @click="select(i)"
        :class="['w-full text-left px-4 py-3 rounded-xl border-2 transition font-medium',
          submitted ? (i===correctIdx ? 'border-green bg-green/10 text-green' : i===selected && i!==correctIdx ? 'border-red-500 bg-red-50 text-red-500' : 'border-gray-100')
          : selected===i ? 'border-purple bg-purple/5' : 'border-gray-100 hover:border-purple/30']">
        {{ opt }}
      </button>
    </div>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
const props = defineProps({ question: Object })
const emit = defineEmits(['submit'])
const selected = ref(null), submitted = ref(false)
const options = computed(() => JSON.parse(props.question.options || '[]'))
const correctIdx = computed(() => options.value.findIndex(o => o.startsWith(props.question.answer)))
function select(i) { if (!submitted.value) { selected.value = i; emit('submit', { selected: i, isCorrect: i === correctIdx.value }) } }
function select(i) { if (!submitted.value) selected.value = i }
function doSubmit() { submitted.value = true; emit('submit', { answer: String.fromCharCode(65 + selected.value), isCorrect: selected.value === correctIdx.value }) }
defineExpose({ doSubmit })
</script>
```

- [ ] **Step 2: TrueFalse.vue**

```vue
<template>
  <div>
    <p class="text-gray-700 mb-6 whitespace-pre-wrap">{{ question.content }}</p>
    <div class="flex gap-4">
      <button @click="choose('正确')" :class="['flex-1 py-4 rounded-xl border-2 text-lg font-medium transition',
        submitted ? (question.answer==='正确' ? 'border-green bg-green/10 text-green' : answer==='正确' ? 'border-red-500 bg-red-50 text-red-500' : 'border-gray-100')
        : answer==='正确' ? 'border-purple bg-purple/5' : 'border-gray-100']">正确</button>
      <button @click="choose('错误')" :class="['flex-1 py-4 rounded-xl border-2 text-lg font-medium transition',
        submitted ? (question.answer==='错误' ? 'border-green bg-green/10 text-green' : answer==='错误' ? 'border-red-500 bg-red-50 text-red-500' : 'border-gray-100')
        : answer==='错误' ? 'border-purple bg-purple/5' : 'border-gray-100']">错误</button>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'
const props = defineProps({ question: Object })
const emit = defineEmits(['submit'])
const answer = ref(null), submitted = ref(false)
function choose(v) { if (!submitted.value) answer.value = v }
function doSubmit() { submitted.value = true; emit('submit', { answer: answer.value, isCorrect: answer.value === props.question.answer }) }
defineExpose({ doSubmit })
</script>
```

- [ ] **Step 3: FillBlank.vue (简化版)**

```vue
<template>
  <div>
    <p class="text-gray-700 mb-6 whitespace-pre-wrap">{{ question.content }}</p>
    <div class="space-y-3">
      <div v-for="(part, i) in parts" :key="i" class="flex items-center gap-2">
        <span class="text-sm text-gray-400">空{{ i+1 }}</span>
        <input v-model="answers[i]" :disabled="submitted" :class="['flex-1 px-3 py-2 border rounded-lg',
          submitted ? (answers[i]?.trim()===part ? 'border-green bg-green/10' : 'border-red-500 bg-red-50') : 'border-gray-200 focus:border-purple']" />
        <span v-if="submitted" :class="answers[i]?.trim()===part ? 'text-green' : 'text-red-500'">{{ answers[i]?.trim()===part ? '✓' : '✗' }}</span>
      </div>
    </div>
    <div v-if="submitted" class="mt-4 p-3 bg-gray-50 rounded-lg">
      <p class="text-sm text-gray-500">正确答案：<span class="text-purple font-medium">{{ parts.join('  |  ') }}</span></p>
    </div>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
const props = defineProps({ question: Object })
const emit = defineEmits(['submit'])
const parts = computed(() => JSON.parse(props.question.answer_parts || '[]'))
const answers = ref(parts.value.map(() => ''))
const submitted = ref(false)
function doSubmit() {
  submitted.value = true
  const correctCount = parts.value.filter((p, i) => answers.value[i]?.trim() === p).length
  emit('submit', { answers: answers.value, isCorrect: correctCount === parts.value.length, partial: correctCount > 0 && correctCount < parts.value.length })
}
defineExpose({ doSubmit })
</script>
```

- [ ] **Step 4: CodeWrite.vue (简化版)**

```vue
<template>
  <div :class="['flex gap-4', isMobile ? 'flex-col' : 'flex-row']">
    <div :class="['overflow-y-auto', isMobile ? 'h-40' : 'flex-1']">
      <p class="text-gray-700 whitespace-pre-wrap text-sm">{{ question.content }}</p>
    </div>
    <div :class="['flex flex-col', isMobile ? '' : 'flex-1']">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs text-gray-400">代码编辑器</span>
        <button @click="code=question.template||''" class="text-xs text-purple">重置</button>
      </div>
      <textarea v-model="code" :disabled="submitted" :class="['w-full font-mono text-sm p-3 border rounded-lg resize-none',
        isMobile ? 'h-48' : 'h-80', submitted ? 'bg-gray-50' : 'border-gray-200 focus:border-purple']" />
      <div v-if="judgeResult" class="mt-3 p-3 bg-yellow-50 rounded-lg text-sm">
        <p><span class="font-medium">评分：{{ judgeResult.score }}/10</span> <span :class="judgeResult.is_correct ? 'text-green' : 'text-red-500'">{{ judgeResult.is_correct ? '✓' : '✗' }}</span></p>
        <p class="text-gray-600 mt-1">{{ judgeResult.comment }}</p>
        <p class="text-xs text-gray-400 mt-2">人工智能生成，仅供参考</p>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import api from '../../api'
const props = defineProps({ question: Object })
const emit = defineEmits(['submit'])
const code = ref(props.question.template || '')
const submitted = ref(false), judging = ref(false), judgeResult = ref(null)
const isMobile = computed(() => window.innerWidth < 768)
async function doSubmit() {
  submitted.value = true; judging.value = true
  try {
    const { data } = await api.post('/judge/code', { question_id: props.question.id, user_code: code.value })
    judgeResult.value = data
    emit('submit', { code: code.value, isCorrect: data.is_correct, aiFeedback: data })
  } catch {
    // timeout - let user manually decide
    emit('submit', { code: code.value, timeout: true })
  }
  judging.value = false
}
defineExpose({ doSubmit })
</script>
```

- [ ] **Step 5: CodeReview.vue**

```vue
<template>
  <div>
    <p class="text-gray-700 mb-6 whitespace-pre-wrap">{{ question.content }}</p>
    <button v-if="!revealed" @click="reveal" class="w-full py-4 border-2 border-purple text-purple rounded-xl font-medium">我有思路了，看答案</button>
    <div v-else class="p-4 bg-gray-50 rounded-xl">
      <pre class="font-mono text-sm whitespace-pre-wrap">{{ question.answer_code || '暂无参考答案' }}</pre>
      <div class="flex gap-3 mt-4">
        <button @click="done(true)" class="flex-1 py-2 bg-green text-white rounded-lg">我做对了</button>
        <button @click="done(false)" class="flex-1 py-2 bg-red-500 text-white rounded-lg">我做错了</button>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'
defineProps({ question: Object })
const emit = defineEmits(['submit'])
const revealed = ref(false)
function reveal() { revealed.value = true }
function done(correct) { emit('submit', { answer: 'review', isCorrect: correct }) }
</script>
```

- [ ] **Step 6: PracticeView.vue**

```vue
<template>
  <div class="min-h-screen bg-bg flex flex-col">
    <!-- 顶栏 -->
    <header class="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-white">
      <button @click="$router.back()" class="text-gray-500"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg></button>
      <span class="text-sm font-medium text-gray-600">{{ question?.q_number }}</span>
      <button @click="showSheet=true" class="text-sm text-purple">答题卡</button>
    </header>

    <!-- 进度条 -->
    <div class="h-1 bg-gray-100"><div class="h-full bg-purple transition-all" :style="{width: progressPercent+'%'}"/></div>

    <!-- 题目标题 -->
    <div class="px-4 py-3">
      <span class="text-xs text-purple font-medium">{{ question?.type }}</span>
      <h2 class="text-base font-medium text-gray-800 mt-1">{{ question?.title }}</h2>
    </div>

    <!-- 题型区域 -->
    <div class="flex-1 px-4 pb-24">
      <LoadingSpinner v-if="loading" :show="true" />
      <component v-else-if="question" :is="typeComp" :question="question" ref="answerRef" @submit="onSubmit" />
    </div>

    <!-- 底部操作栏 -->
    <footer class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 px-4 py-3 flex gap-3">
      <button @click="prevQuestion" :disabled="!hasPrev" class="px-3 py-2 border border-gray-200 rounded-lg text-sm disabled:opacity-30">上一题</button>
      <button @click="handleSubmit" :disabled="submitted" class="flex-1 py-2 bg-purple text-white rounded-lg text-sm font-medium disabled:opacity-40">提交</button>
      <button @click="nextQuestion" :disabled="!hasNext" class="px-3 py-2 border border-gray-200 rounded-lg text-sm disabled:opacity-30">下一题</button>
    </footer>

    <BottomDisclaimer />
    <AnswerSheet :open="showSheet" :items="sheetItems" :currentId="question?.id" @close="showSheet=false" @jump="jumpTo" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { usePracticeStore } from '../stores/practice'
import BottomDisclaimer from '../components/layout/BottomDisclaimer.vue'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'
import AnswerSheet from '../components/common/AnswerSheet.vue'
import SingleChoice from '../components/practice/SingleChoice.vue'
import TrueFalse from '../components/practice/TrueFalse.vue'
import FillBlank from '../components/practice/FillBlank.vue'
import CodeWrite from '../components/practice/CodeWrite.vue'
import CodeReview from '../components/practice/CodeReview.vue'

const route = useRoute(), store = usePracticeStore()
const question = ref(null), loading = ref(false), submitted = ref(false)
const answerRef = ref(null), showSheet = ref(false)
const questionIndex = ref(0), questions = ref([])

const typeComp = computed(() => {
  if (!question.value) return null
  const map = { '单选题': SingleChoice, '判断题': TrueFalse, '填空题': FillBlank, '编程题': store.settings?.progMode === 'review' ? CodeReview : CodeWrite }
  return map[question.value.type]
})

const progressPercent = computed(() => questions.value.length ? (questionIndex.value / questions.value.length) * 100 : 0)
const hasPrev = computed(() => questionIndex.value > 0)
const hasNext = computed(() => questionIndex.value < questions.value.length - 1)
const sheetItems = computed(() => questions.value.map((q, i) => ({ id: q.id, label: i + 1, status: null })))

onMounted(async () => {
  loading.value = true
  // 根据路由确定模式加载题目列表
  const { data } = await api.get('/questions', { params: { per: 618 } })
  questions.value = data.items
  if (questions.value.length) { question.value = await store.fetchQuestion(questions.value[0].id) }
  loading.value = false
})

function handleSubmit() { answerRef.value?.doSubmit?.(); submitted.value = true }
function nextQuestion() { if (hasNext.value) { questionIndex.value++; loadCurrent(); submitted.value = false } }
function prevQuestion() { if (hasPrev.value) { questionIndex.value--; loadCurrent(); submitted.value = false } }
async function loadCurrent() { loading.value = true; question.value = await store.fetchQuestion(questions.value[questionIndex.value].id); loading.value = false }
function jumpTo(id) { questionIndex.value = questions.value.findIndex(q => q.id === id); loadCurrent(); showSheet.value = false; submitted.value = false }
async function onSubmit(result) { await store.submitAnswer({ question_id: question.value.id, answer_status: result.isCorrect ? 'correct' : 'incorrect', user_answer: JSON.stringify(result), mode: store.mode }) }
</script>
```

- [ ] **Step 7: Commit**

```bash
git add frontend/src/views/PracticeView.vue frontend/src/components/practice/ && git commit -m "feat(frontend): PracticeView + 四种题型组件"
```

---

### Task 9: WrongBooks + AdminResetPin

**Files:**
- Modify: `frontend/src/views/WrongBooks.vue`
- Modify: `frontend/src/views/AdminResetPin.vue`

- [ ] **Step 1: WrongBooks.vue**

```vue
<template>
  <div class="min-h-screen bg-bg flex flex-col">
    <header class="flex items-center gap-3 px-4 py-3 bg-white border-b border-gray-100">
      <button @click="$router.back()" class="text-gray-500"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg></button>
      <h1 class="font-semibold text-gray-800">错题管理</h1>
    </header>

    <!-- 筛选 -->
    <div class="flex gap-2 px-4 py-2">
      <select v-model="store.filters.type" @change="reload" class="px-3 py-1 border border-gray-200 rounded-lg text-sm">
        <option value="">全部题型</option>
        <option v-for="t in types" :key="t" :value="t">{{ t }}</option>
      </select>
      <select v-model="store.filters.chapter" @change="reload" class="px-3 py-1 border border-gray-200 rounded-lg text-sm">
        <option value="">全部章节</option>
        <option v-for="ch in chapters" :key="ch" :value="ch">第{{ ch }}章</option>
      </select>
    </div>

    <!-- 操作栏 -->
    <div class="flex gap-2 px-4 py-2">
      <button @click="store.selectAll()" class="text-xs px-2 py-1 border border-gray-200 rounded">全选</button>
      <button @click="doRePractice" :disabled="!store.selected.length" class="text-xs px-2 py-1 border border-purple text-purple rounded disabled:opacity-30">练习重做</button>
      <button @click="doRemove" :disabled="!store.selected.length" class="text-xs px-2 py-1 border border-red-500 text-red-500 rounded disabled:opacity-30">移出错题本</button>
      <button @click="doExport" class="text-xs px-2 py-1 border border-gray-200 rounded">导出</button>
    </div>

    <!-- 列表 -->
    <div class="flex-1 px-4 overflow-y-auto">
      <div v-if="!store.list.length" class="py-20 text-center text-gray-400 text-sm">暂无错题，继续保持！</div>
      <div v-for="item in store.list" :key="item.question_id" class="flex items-center gap-3 py-2 border-b border-gray-50">
        <input type="checkbox" :checked="store.selected.includes(item.question_id)" @change="store.toggleSelect(item.question_id)" class="accent-purple" />
        <router-link :to="`/wrong/${item.question_id}`" class="flex-1 text-sm">
          <span class="text-gray-400 mr-2">{{ item.q_number }}</span>
          <span class="text-purple text-xs mr-1">[{{ item.type }}]</span>
          <span class="text-gray-700">{{ item.title }}</span>
        </router-link>
      </div>
    </div>

    <div class="flex justify-center gap-4 py-3">
      <button @click="prevPage" :disabled="store.pagination.page<=1" class="text-sm text-gray-400 disabled:opacity-30">上一页</button>
      <span class="text-sm text-gray-500">{{ store.pagination.page }}/{{ Math.ceil(store.pagination.total/store.pagination.per) || 1 }}</span>
      <button @click="nextPage" :disabled="store.pagination.page*store.pagination.per>=store.pagination.total" class="text-sm text-gray-400 disabled:opacity-30">下一页</button>
    </div>

    <BottomDisclaimer />
  </div>
</template>
<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWrongStore } from '../stores/wrong'
import BottomDisclaimer from '../components/layout/BottomDisclaimer.vue'

const router = useRouter(), store = useWrongStore()
const types = ['单选题', '判断题', '填空题', '编程题']
const chapters = Array.from({length:8}, (_,i)=>String(i+1))

onMounted(() => store.fetchList())
function reload() { store.pagination.page = 1; store.fetchList() }
function prevPage() { store.pagination.page--; store.fetchList() }
function nextPage() { store.pagination.page++; store.fetchList() }
async function doRemove() { await store.removeFromWrong(store.selected); store.selected = []; store.fetchList() }
async function doExport() { const blob = await store.exportExcel(); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = 'wrong_questions.xlsx'; a.click() }
function doRePractice() { router.push({ path: '/practice/wrong', query: { ids: store.selected.join(',') } }) }
</script>
```

- [ ] **Step 2: AdminResetPin.vue**

```vue
<template>
  <div class="min-h-screen bg-bg flex flex-col items-center justify-center px-4">
    <h1 class="text-2xl text-purple font-[Cormorant_Garamond] mb-8">重置 PIN</h1>
    <input v-model="sid" maxlength="10" placeholder="输入10位学号" class="w-full max-w-sm px-4 py-3 border border-gray-200 rounded-lg text-center text-lg mb-4" />
    <button @click="doReset" :disabled="sid.length!==10" class="w-full max-w-sm py-3 bg-purple text-white rounded-lg disabled:opacity-40">重置 PIN</button>
    <p v-if="msg" class="mt-4 text-sm text-gray-500">{{ msg }}</p>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import api from '../api'
const sid = ref(''), msg = ref('')
async function doReset() {
  try { await api.post('/admin/reset-pin', { student_id: sid.value }); msg.value = 'PIN 已重置' }
  catch { msg.value = '重置失败' }
}
</script>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/WrongBooks.vue frontend/src/views/AdminResetPin.vue && git commit -m "feat(frontend): WrongBooks + AdminResetPin 页面"
```

---

### Task 10: 联调修复 + 最终测试 + Push

- [ ] **Step 1: 启动后端 + 前端，全流程走通**

```bash
# Terminal 1
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8765

# Terminal 2
cd frontend && npm run dev
# 打开 http://localhost:5173
# 测试: 登录 → 首页 → 顺序刷题 → 提交 → 错题 → 导出
```

- [ ] **Step 2: 修复联调中发现的问题**

- [ ] **Step 3: Commit fixes**

```bash
git add . && git commit -m "fix(frontend): 联调修复" && git push
```

- [ ] **Step 4: 更新记忆**

更新记忆文件标记前端已完成。
