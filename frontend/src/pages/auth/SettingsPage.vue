<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../../api/axios'
import { useAuthStore } from '../../stores/auth'
import { Save, KeyRound } from 'lucide-vue-next'

const authStore = useAuthStore()

const profileForm = ref({
  first_name: '',
  last_name: '',
  ficha: '',
  email: ''
})

const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const loading = ref(false)
const error = ref('')
const success = ref('')
const passwordSuccess = ref('')
const passwordError = ref('')

onMounted(async () => {
  try {
    const response = await api.get('user/profile/')
    const data = response.data
    profileForm.value = {
      first_name: data.first_name,
      last_name: data.last_name,
      ficha: data.ficha,
      email: data.email
    }
  } catch (e) {
    error.value = 'Error al cargar el perfil'
  }
})

const handleProfileUpdate = async () => {
  loading.value = true
  error.value = ''
  success.value = ''

  try {
    await api.put('user/profile/', {
      first_name: profileForm.value.first_name,
      last_name: profileForm.value.last_name,
      email: profileForm.value.email,
      profile: { ficha: profileForm.value.ficha }
    })
    success.value = 'Perfil actualizado exitosamente'
    
    // Refresh user data in store
    const newProfile = await api.get('user/profile/')
    authStore.user = newProfile.data
    localStorage.setItem('user', JSON.stringify(newProfile.data))
  } catch (e) {
    error.value = 'Error al actualizar el perfil'
  } finally {
    loading.value = false
  }
}

const handlePasswordChange = async () => {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    passwordError.value = 'Las contraseñas nuevas no coinciden'
    return
  }

  loading.value = true
  passwordError.value = ''
  passwordSuccess.value = ''

  try {
    await api.post('user/change-password/', passwordForm.value)
    passwordSuccess.value = 'Contraseña actualizada exitosamente'
    passwordForm.value.old_password = ''
    passwordForm.value.new_password = ''
    passwordForm.value.confirm_password = ''
  } catch (e: any) {
    passwordError.value = e.response?.data?.old_password?.[0] || 'Error al cambiar la contraseña'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="p-8 max-w-4xl mx-auto space-y-6">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-[#1e5b4f]">Ajustes de Perfil</h1>
    </div>

    <!-- Update Profile Form -->
    <div class="bg-white rounded-xl shadow-[0_2px_10px_rgba(0,0,0,0.05)] border border-[#e0e0e0] p-8">
      <h2 class="text-xl font-semibold mb-6 text-gray-800">Mi Información</h2>
      
      <div v-if="error" class="bg-red-50 text-red-700 p-4 rounded-lg mb-4 border border-red-200">
        {{ error }}
      </div>
      <div v-if="success" class="bg-green-50 text-green-700 p-4 rounded-lg mb-4 border border-green-200">
        {{ success }}
      </div>

      <form @submit.prevent="handleProfileUpdate" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
            <input v-model="profileForm.first_name" type="text" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none transition-all" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Apellidos</label>
            <input v-model="profileForm.last_name" type="text" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none transition-all" />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Ficha</label>
            <input v-model="profileForm.ficha" type="text" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none transition-all" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Correo Electrónico</label>
            <input v-model="profileForm.email" type="email" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none transition-all" />
          </div>
        </div>

        <div class="flex justify-end pt-4 border-t border-gray-100 mt-6">
          <button type="submit" :disabled="loading" class="bg-[#1e5b4f] hover:bg-[#024e47] text-white px-6 py-2.5 rounded-lg flex items-center gap-2 font-medium transition-colors shadow-sm disabled:opacity-70">
            <Save class="w-5 h-5" />
            {{ loading ? 'Guardando...' : 'Actualizar Información' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Password Reset Form -->
    <div class="bg-white rounded-xl shadow-[0_2px_10px_rgba(0,0,0,0.05)] border border-[#e0e0e0] p-8">
      <h2 class="text-xl font-semibold mb-6 text-gray-800">Cambiar Contraseña</h2>
      
      <div v-if="passwordError" class="bg-red-50 text-red-700 p-4 rounded-lg mb-4 border border-red-200">
        {{ passwordError }}
      </div>
      <div v-if="passwordSuccess" class="bg-green-50 text-green-700 p-4 rounded-lg mb-4 border border-green-200">
        {{ passwordSuccess }}
      </div>

      <form @submit.prevent="handlePasswordChange" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Contraseña Actual</label>
          <input v-model="passwordForm.old_password" type="password" required class="w-full md:w-1/2 px-4 py-2 border border-gray-300 rounded-lg focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none transition-all" />
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nueva Contraseña</label>
            <input v-model="passwordForm.new_password" type="password" required minlength="8" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none transition-all" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Confirmar Contraseña</label>
            <input v-model="passwordForm.confirm_password" type="password" required minlength="8" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none transition-all" />
          </div>
        </div>
        <div class="flex justify-end pt-4 border-t border-gray-100 mt-6">
          <button type="submit" :disabled="loading" class="bg-gray-800 hover:bg-gray-900 text-white px-6 py-2.5 rounded-lg flex items-center gap-2 font-medium transition-colors shadow-sm disabled:opacity-70">
            <KeyRound class="w-5 h-5" />
            Cambiar Contraseña
          </button>
        </div>
      </form>
    </div>

  </div>
</template>
