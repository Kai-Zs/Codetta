import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/LoginView.vue') },
  { path: '/', name: 'Home', component: () => import('../views/HomeView.vue'), meta: { auth: true } },
  { path: '/practice/sequential', name: 'PracticeSeq', component: () => import('../views/PracticeView.vue'), meta: { auth: true } },
  { path: '/practice/filter', name: 'PracticeFilter', component: () => import('../views/PracticeView.vue'), meta: { auth: true } },
  { path: '/practice/wrong', name: 'PracticeWrong', component: () => import('../views/PracticeView.vue'), meta: { auth: true } },
  { path: '/wrong', name: 'Wrong', component: () => import('../views/WrongBooks.vue'), meta: { auth: true } },
  { path: '/wrong/:qid', name: 'WrongDetail', component: () => import('../views/PracticeView.vue'), meta: { auth: true, readonly: true } },
  { path: '/admin/reset-pin', name: 'AdminReset', component: () => import('../views/AdminResetPin.vue'), meta: { auth: true } },
]

const router = createRouter({ history: createWebHistory('/codetta/'), routes })

let authVerified = false

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')

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
