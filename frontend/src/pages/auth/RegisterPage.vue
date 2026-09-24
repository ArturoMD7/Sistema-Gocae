<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api/axios'
import { ArrowLeft, Save } from 'lucide-vue-next'

const router = useRouter()
const form = ref({
  first_name: '',
  last_name: '',
  ficha: '',
  email: '',
  password: '',
  password_confirm: '',
  groups: [] as string[]
})

const roles = ref<any[]>([])
const loading = ref(false)
const error = ref('')
const success = ref(false)

const fetchRoles = async () => {
  try {
    const response = await api.get('groups/')
    roles.value = response.data
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  fetchRoles()
})

const handleSubmit = async () => {
  if (form.value.password !== form.value.password_confirm) {
    error.value = 'Las contraseñas no coinciden'
    return
  }
  
  loading.value = true
  error.value = ''
  success.value = false

  try {
    await api.post('register/', {
      first_name: form.value.first_name,
      last_name: form.value.last_name,
      ficha: form.value.ficha,
      email: form.value.email,
      password: form.value.password,
      password2: form.value.password_confirm,
      groups: form.value.groups
    })
    success.value = true
    setTimeout(() => {
      router.push({ name: 'users' })
    }, 1500)
  } catch (e: any) {
    if (e.response?.data) {
      const msgs = Object.values(e.response.data).flat()
      error.value = msgs.join(' ')
    } else {
      error.value = 'Error al registrar usuario'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="p-8 max-w-3xl mx-auto">
    <div class="flex items-center gap-4 mb-6">
      <button @click="router.back()" class="p-2 text-gray-500 hover:text-[#1e5b4f] hover:bg-gray-200 rounded-full transition-colors">
        <ArrowLeft class="w-6 h-6" />
      </button>
      <h1 class="text-3xl font-bold text-[#1e5b4f]">Registrar Usuario</h1>
    </div>

    <div v-if="error" class="bg-red-50 text-red-700 p-4 rounded-lg mb-6 border border-red-200">
      {{ error }}
    </div>
    
    <div v-if="success" class="bg-green-50 text-green-700 p-4 rounded-lg mb-6 border border-green-200">
      Usuario registrado exitosamente. Redirigiendo...
    </div>

    <div class="bg-white rounded-xl shadow-[0_2px_10px_rgba(0,0,0,0.05)] border border-[#e0e0e0] p-8">
      <form @submit.prevent="handleSubmit" class="space-y-6">
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

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
            <input v-model="form.password" type="password" required minlength="8" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none transition-all" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Confirmar Contraseña</label>
            <input v-model="form.password_confirm" type="password" required minlength="8" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none transition-all" />
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

        <div class="flex justify-end pt-4">
          <button type="submit" :disabled="loading" class="bg-[#1e5b4f] hover:bg-[#024e47] text-white px-6 py-2.5 rounded-lg flex items-center gap-2 font-medium transition-colors shadow-sm disabled:opacity-70">
            <Save class="w-5 h-5" />
            {{ loading ? 'Guardando...' : 'Guardar Usuario' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
