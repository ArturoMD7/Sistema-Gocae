import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import MainLayout from '../layouts/MainLayout.vue'
import LoginPage from '../pages/auth/LoginPage.vue'
import ContratosDashboard from '../pages/dashboard/ContratosDashboard.vue'
import ContractsPage from '../pages/contracts/ContractsPage.vue'
import ContractEditPage from '../pages/contracts/ContractEditPage.vue'

// Nuevas vistas
import UserPage from '../pages/auth/UserPage.vue'
import RegisterPage from '../pages/auth/RegisterPage.vue'
import EditUserPage from '../pages/auth/EditUserPage.vue'
import UserInfoPage from '../pages/auth/UserInfoPage.vue'
import SettingsPage from '../pages/auth/SettingsPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: { requiresGuest: true }
    },
    {
      path: '/',
      component: MainLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'home',
          component: ContratosDashboard
        },
        {
          path: 'contracts',
          name: 'contracts',
          component: ContractsPage
        },
        {
          path: 'contracts/:id/edit',
          name: 'contract-edit',
          component: ContractEditPage,
          meta: { requiresAdmin: true }
        },
        {
          path: 'users',
          name: 'users',
          component: UserPage,
          meta: { requiresAdmin: true }
        },
        {
          path: 'register',
          name: 'register',
          component: RegisterPage,
          meta: { requiresAdmin: true }
        },
        {
          path: 'edit-user/:id',
          name: 'edit-user',
          component: EditUserPage,
          meta: { requiresAdmin: true }
        },
        {
          path: 'user-info/:id',
          name: 'user-info',
          component: UserInfoPage
        },
        {
          path: 'settings',
          name: 'settings',
          component: SettingsPage
        }
      ]
    }
  ]
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login' })
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: 'home' })
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'home' }) // Bloquear acceso si no es admin
  } else {
    next()
  }
})

export default router
