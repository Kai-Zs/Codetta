import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/LoginView.vue') },
  { path: '/maintenance', name: 'Maintenance', component: () => import('../views/MaintenanceView.vue') },
  { path: '/', name: 'Home', component: () => import('../views/HomeView.vue'), meta: { auth: true } },
  { path: '/practice/sequential', name: 'PracticeSeq', component: () => import('../views/PracticeView.vue'), meta: { auth: true } },
  { path: '/practice/filter', name: 'PracticeFilter', component: () => import('../views/PracticeView.vue'), meta: { auth: true } },
  { path: '/practice/wrong', name: 'PracticeWrong', component: () => import('../views/PracticeView.vue'), meta: { auth: true } },
  { path: '/wrong', name: 'Wrong', component: () => import('../views/WrongBooks.vue'), meta: { auth: true } },
  { path: '/wrong/:qid', name: 'WrongDetail', component: () => import('../views/PracticeView.vue'), meta: { auth: true, readonly: true } },
  {
    path: '/admin',
    component: () => import('../views/admin/AdminLayout.vue'),
    children: [
      { path: '', redirect: '/admin/questions' },
      { path: 'questions', name: 'AdminQuestions', component: () => import('../views/admin/AdminQuestions.vue') },
      { path: 'users', name: 'AdminUsers', component: () => import('../views/admin/AdminUsers.vue') },
      { path: 'users/:id', name: 'AdminUserDetail', component: () => import('../views/admin/AdminUserDetail.vue') },
      { path: 'stats', name: 'AdminStats', component: () => import('../views/admin/AdminStats.vue') },
      { path: 'settings', name: 'AdminSettings', component: () => import('../views/admin/AdminSettings.vue') },
    ],
  },
]

const router = createRouter({ history: createWebHistory('/codetta/'), routes })

let authVerified = false
let inMaintenance = false

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  const isAdmin = to.path.startsWith('/admin')

  // 管理员页面：不检查用户 token
  if (isAdmin) return next()

  // 维护模式检查（非 Admin 页面，非 login/维护页面本身）
  if (!isAdmin && to.path !== '/login' && to.path !== '/maintenance') {
    try {
      const api = (await import('../api')).default
      const { data } = await api.get('/maintenance')
      inMaintenance = data.maintenance
    } catch {}
    if (inMaintenance) return next('/maintenance')
  }

  // 需要登录但无 token → 去登录页
  if (to.meta.auth && !token) return next('/login')

  // 已登录访问登录页 → 回首页
  if (to.path === '/login' && token) return next('/')

  // 有 token 但未验证过 → 调接口确认有效性
  if (token && to.meta.auth && !authVerified) {
    try {
      const api = (await import('../api')).default
      await api.get('/auth/me')
      authVerified = true
    } catch {
      localStorage.removeItem('token')
      authVerified = false
      return next('/login')
    }
  }

  next()
})

export default router
