import api from './index'

export function checkKp() {
  return api.get('/kp/check').then(r => r.data)
}

export function analyzeKp(questionId, force = false) {
  return api.post('/kp/analyze', { question_id: questionId, force }).then(r => r.data)
}

export function chatKp(questionId, messages) {
  return api.post('/kp/chat', { question_id: questionId, messages }).then(r => r.data)
}
