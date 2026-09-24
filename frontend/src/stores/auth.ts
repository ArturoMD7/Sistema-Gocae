import { defineStore } from 'pinia'
import api from '../api/axios'

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  ficha?: string;
  profile_picture?: string;
  groups?: string[];
}

interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('token'),
    refreshToken: localStorage.getItem('refreshToken'),
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.groups?.includes('Admin') || false,
  },
  actions: {
    async login(identifier: string, password: string) {
      const response = await api.post('token/', { username: identifier, password })
      this.token = response.data.access
      this.refreshToken = response.data.refresh
      
      localStorage.setItem('token', this.token!)
      localStorage.setItem('refreshToken', this.refreshToken!)

      try {
        const profileRes = await api.get('user/profile/')
        this.user = profileRes.data
        localStorage.setItem('user', JSON.stringify(this.user))
      } catch (e) {
        console.error('Error fetching profile', e)
        this.user = response.data.user
        localStorage.setItem('user', JSON.stringify(this.user))
      }
    },
    logout() {
      this.user = null
      this.token = null
      this.refreshToken = null
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
    }
  }
})
