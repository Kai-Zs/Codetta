import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  const adminPwd = sessionStorage.getItem('admin_token')
  if (adminPwd) config.headers['X-Admin-Password'] = adminPwd
  return config
})

api.interceptors.response.use(
  res => res,
  async err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      const { default: router } = await import('../router')
      router.push('/login')
    }
    return Promise.reject(err)
  }
)

export default api
