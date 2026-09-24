<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../api/axios'
import { ArrowLeft, Save, Trash2, KeyRound } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const userId = route.params.id

const form = ref({
  first_name: '',
  last_name: '',
  ficha: '',
  email: '',
  groups: [] as string[]
})

const passwordForm = ref({
  new_password: '',
  confirm_password: ''
})

const roles = ref<any[]>([])
const loading = ref(false)
const error = ref('')
const success = ref('')

const fetchRoles = async () => {
  try {
    const response = await api.get('groups/')
    roles.value = response.data
  } catch (e) {
    console.error(e)
  }
}

const fetchUser = async () => {
  try {
    const response = await api.get(`user/${userId}/`)
    const data = response.data
    form.value = {
      first_name: data.first_name,
      last_name: data.last_name,
      ficha: data.ficha,
      email: data.email,
      groups: data.groups || []
    }
  } catch (e) {
    error.value = 'Error al cargar datos del usuario'
  }
}

onMounted(() => {
  fetchRoles()
  fetchUser()
})

const handleUpdate = async () => {
  loading.value = true
  error.value = ''
  success.value = ''

  try {
    await api.put(`user/${userId}/`, {
      first_name: form.value.first_name,
      last_name: form.value.last_name,
      email: form.value.email,
      groups: form.value.groups,
      profile: { ficha: form.value.ficha }
    })
    success.value = 'Usuario actualizado exitosamente'
  } catch (e: any) {
    error.value = 'Error al actualizar usuario'
  } finally {
    loading.value = false
  }
}

const handlePasswordReset = async () => {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    error.value = 'Las contraseñas no coinciden'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    await api.post(`users/${userId}/reset-password/`, passwordForm.value)
    success.value = 'Contraseña restablecida exitosamente'
    passwordForm.value.new_password = ''
    passwordForm.value.confirm_password = ''
  } catch (e) {
    error.value = 'Error al restablecer contraseña'
  } finally {
    loading.value = false
  }
}

const handleDelete = async () => {
  if (!confirm('¿Estás seguro de que deseas eliminar este usuario?')) return

  try {
    await api.delete(`user/${userId}/`)
    router.push({ name: 'users' })
  } catch (e: any) {
    error.value = e.response?.data?.error || 'Error al eliminar usuario'
  }
}
</script>

<template>
  <div class="p-8 max-w-4xl mx-auto space-y-6">
    <div class="flex items-center gap-4 mb-2">
      <button @click="router.back()" class="p-2 text-gray-500 hover:text-[#1e5b4f] hover:bg-gray-200 rounded-full transition-colors">
        <ArrowLeft class="w-6 h-6" />
      </button>
      <h1 class="text-3xl font-bold text-[#1e5b4f]">Editar Usuario</h1>
    </div>

    <div v-if="error" class="bg-red-50 text-red-700 p-4 rounded-lg border border-red-200">
      {{ error }}
    </div>
    
    <div v-if="success" class="bg-green-50 text-green-700 p-4 rounded-lg border border-green-200">
      {{ success }}
    </div>

    <!-- Basic Info Form -->
    <div class="bg-white rounded-xl shadow-[0_2px_10px_rgba(0,0,0,0.05)] border border-[#e0e0e0] p-8">
      <h2 class="text-xl font-semibold mb-6 text-gray-800">Información General</h2>
      <form @submit.prevent="handleUpdate" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
            <input v-model="form.first_name" type="text" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none transition-all" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Apellidos</label>
            <input v-model="form.last_name" type="text" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none transition-all" />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Ficha</label>
            <input v-model="form.ficha" type="text" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none transition-all" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Correo Electrónico</label>
            <input v-model="form.email" type="email" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none transition-all" />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Roles</label>
          <div class="flex gap-4">
            <label v-for="role in roles" :key="role.id" class="flex items-center gap-2 cursor-pointer bg-gray-50 p-2 border border-gray-200 rounded-lg hover:bg-gray-100">
              <input type="checkbox" :value="role.name" v-model="form.groups" class="rounded text-[#1e5b4f] focus:ring-[#1e5b4f]" />
              <span class="text-gray-700 font-medium">{{ role.name }}</span>
            </label>
          </div>
        </div>

        <div class="flex justify-between pt-4 border-t border-gray-100 mt-6">
          <button type="button" @click="handleDelete" class="text-red-600 hover:bg-red-50 px-4 py-2 rounded-lg flex items-center gap-2 font-medium transition-colors">
            <Trash2 class="w-5 h-5" />
            Eliminar
          </button>
          
          <button type="submit" :disabled="loading" class="bg-[#1e5b4f] hover:bg-[#024e47] text-white px-6 py-2.5 rounded-lg flex items-center gap-2 font-medium transition-colors shadow-sm disabled:opacity-70">
            <Save class="w-5 h-5" />
            {{ loading ? 'Guardando...' : 'Actualizar Usuario' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Password Reset Form -->
    <div class="bg-white rounded-xl shadow-[0_2px_10px_rgba(0,0,0,0.05)] border border-[#e0e0e0] p-8">
      <h2 class="text-xl font-semibold mb-6 text-gray-800">Restablecer Contraseña</h2>
      <form @submit.prevent="handlePasswordReset" class="space-y-6">
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
        <div class="flex justify-end pt-2">
          <button type="submit" :disabled="loading" class="bg-gray-800 hover:bg-gray-900 text-white px-6 py-2.5 rounded-lg flex items-center gap-2 font-medium transition-colors shadow-sm disabled:opacity-70">
            <KeyRound class="w-5 h-5" />
            Restablecer Contraseña
          </button>
        </div>
      </form>
    </div>

  </div>
</template>
