import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
})

api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const authStore = useAuthStore()
    // Auto logout if 401 response returned from api
    if (error.response && error.response.status === 401) {
      authStore.logout()
    }
    return Promise.reject(error)
  }
)

export default api
