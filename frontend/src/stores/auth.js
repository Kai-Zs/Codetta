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
