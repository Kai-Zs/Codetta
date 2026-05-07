import { defineStore } from 'pinia'

const KEY = 'theme-preference'

function systemPrefersDark() {
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

function applyTheme(dark) {
  document.documentElement.classList.toggle('dark', dark)
}

export const useThemeStore = defineStore('theme', {
  state: () => {
    const saved = localStorage.getItem(KEY)
    return {
      preference: saved || 'system', // 'system' | 'light' | 'dark'
    }
  },

  getters: {
    isDark: (s) => s.preference === 'dark' || (s.preference === 'system' && systemPrefersDark()),
  },

  actions: {
    init() {
      applyTheme(this.isDark)
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        if (this.preference === 'system') applyTheme(this.isDark)
      })
    },

    toggle() {
      const dark = this.isDark
      this.preference = dark ? 'light' : 'dark'
      localStorage.setItem(KEY, this.preference)
      applyTheme(this.isDark)
    },

    setPreference(val) {
      this.preference = val
      localStorage.setItem(KEY, val)
      applyTheme(this.isDark)
    },
  },
})
