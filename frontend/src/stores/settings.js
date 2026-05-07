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
