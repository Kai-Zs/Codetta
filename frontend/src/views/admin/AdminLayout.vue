<template>
  <div class="min-h-screen flex items-center justify-center overflow-hidden">
    <BackgroundLayer />
    <!-- 密码弹窗 -->
    <AdminLogin v-if="!authed" @ok="authed = true" />
    <!-- 主布局 -->
    <div v-if="authed" class="flex gap-4 z-10 items-start" style="max-height: 92vh; width: 94vw; max-width: 1500px;">
      <!-- 左侧边栏 -->
      <div class="admin-card w-48 flex-shrink-0 flex flex-col">
        <h1 class="text-lg font-[Georgia] text-purple tracking-widest mb-6 text-center">Codetta Admin</h1>
        <nav class="flex flex-col gap-1 flex-1">
          <router-link v-for="item in nav" :key="item.path" :to="item.path"
            class="px-3 py-2 rounded-lg text-sm transition hover:bg-purple/5 dark:hover:bg-purple/10"
            :class="$route.path.startsWith(item.path) && (item.path !== '/admin' || $route.path === '/admin')
              ? 'text-purple font-medium bg-purple/5 dark:bg-purple/10'
              : 'text-gray-500 dark:text-gray-400'">
            {{ item.label }}
          </router-link>
        </nav>
        <router-link to="/" class="block mt-4 text-xs text-gray-400 dark:text-gray-600 hover:text-gray-500 transition text-center py-2">
          &larr; 返回前台
        </router-link>
      </div>
      <!-- 右侧内容 -->
      <div class="admin-card flex-1 overflow-y-auto" style="max-height: 92vh;">
        <router-view />
      </div>
    </div>
    <!-- 备案 -->
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
import { ref } from 'vue'
import BackgroundLayer from '../../components/layout/BackgroundLayer.vue'
import AdminLogin from './AdminLogin.vue'
import beianIcon from '../../assets/beian.png'

const authed = ref(!!sessionStorage.getItem('admin_token'))

const nav = [
  { path: '/admin/questions', label: '题目管理' },
  { path: '/admin/users', label: '用户管理' },
  { path: '/admin/stats', label: '数据统计' },
  { path: '/admin/settings', label: '系统设置' },
]
</script>

<style scoped>
.admin-card {
  background: #fff;
  border-radius: 20px;
  padding: 24px;
  box-shadow:
    0 0 0 3px #d4c0f0,
    0 0 0 5px #b8a0e0,
    0 24px 80px rgba(100, 40, 180, 0.12);
}
.dark .admin-card {
  background: #1a1a2e;
  box-shadow:
    0 0 0 3px #2d2048,
    0 0 0 5px #1a1030,
    0 24px 80px rgba(0, 0, 0, 0.3);
}
</style>
