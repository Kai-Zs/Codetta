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
