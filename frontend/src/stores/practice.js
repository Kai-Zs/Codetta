import { defineStore } from 'pinia'
import api from '../api'

export const usePracticeStore = defineStore('practice', {
  state: () => ({
    currentQuestion: null,
    mode: 'sequential',
    filters: { type: [], chapter: '', status: 'all' },
    answerSheet: [],
    loading: false,
    showEditor: false,
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
