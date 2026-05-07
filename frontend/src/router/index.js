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
