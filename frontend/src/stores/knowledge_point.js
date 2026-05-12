import { defineStore } from 'pinia'
import { checkKp, analyzeKp, chatKp } from '../api/knowledge_point'

export const useKpStore = defineStore('kp', {
  state: () => ({
    kpEnabled: false,
    aiOpen: false,
    aiLoading: false,
    aiContent: '',
    aiError: '',
    questionId: null,
    question: null,
  }),

  actions: {
    async check() {
      try {
        const r = await checkKp()
        this.kpEnabled = r.kp_enabled
      } catch { this.kpEnabled = false }
    },

    open(questionId, question) {
      this.aiOpen = true
      this.questionId = questionId
      this.question = question
      this.aiError = ''
      this.aiContent = ''
      this._loadAnalysis()
    },

    async _loadAnalysis() {
      if (!this.questionId) return
      this.aiLoading = true
      this.aiError = ''
      const qid = this.questionId
      try {
        const r = await analyzeKp(qid)
        if (this.questionId !== qid) return
        this.aiContent = r.analysis_md
      } catch (e) {
        if (this.questionId !== qid) return
        this.aiError = e.response?.data?.detail || e.message || '解析失败'
      } finally {
        if (this.questionId === qid) this.aiLoading = false
      }
    },

    async reanalyze() {
      if (!this.questionId) return
      this.aiLoading = true
      this.aiError = ''
      const qid = this.questionId
      try {
        const r = await analyzeKp(qid, true)
        if (this.questionId !== qid) return
        this.aiContent = r.analysis_md
      } catch (e) {
        if (this.questionId !== qid) return
        this.aiError = e.response?.data?.detail || e.message || '重新解析失败'
      } finally {
        if (this.questionId === qid) this.aiLoading = false
      }
    },

    close() {
      this.aiOpen = false
      this.aiContent = ''
      this.aiError = ''
      this.questionId = null
      this.question = null
    },

    async chat(messages) {
      if (!this.questionId) throw new Error('No question')
      const r = await chatKp(this.questionId, messages)
      return r.reply
    },
  },
})
