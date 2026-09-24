<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../../api/axios'
import { Edit, UserPlus, Eye } from 'lucide-vue-next'

const users = ref<any[]>([])
const loading = ref(true)
const error = ref('')

const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await api.get('users/')
    users.value = response.data
  } catch (e: any) {
    error.value = 'Error al cargar usuarios'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <div class="p-8 max-w-7xl mx-auto">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-[#1e5b4f]">Usuarios</h1>
      <router-link :to="{ name: 'register' }" class="bg-[#1e5b4f] hover:bg-[#024e47] text-white px-4 py-2 rounded-lg flex items-center gap-2 font-medium transition-colors shadow-sm">
        <UserPlus class="w-5 h-5" />
        Nuevo Usuario
      </router-link>
    </div>

    <div v-if="error" class="bg-red-50 text-red-700 p-4 rounded-lg mb-6 border border-red-200">
      {{ error }}
    </div>

    <div class="bg-white rounded-lg border border-[#e0e0e0] overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-500">
        Cargando usuarios...
      </div>
      <table v-else class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-white border-b border-[#e0e0e0] text-[#1e5b4f]">
            <th class="p-3 font-semibold text-sm">Ficha</th>
            <th class="p-3 font-semibold text-sm">Nombre</th>
            <th class="p-3 font-semibold text-sm">Email</th>
            <th class="p-3 font-semibold text-sm">Rol</th>
            <th class="p-3 font-semibold text-sm text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id" class="border-b border-[#e0e0e0] hover:bg-gray-50/50 transition-colors">
            <td class="p-3 text-sm text-gray-600">{{ user.ficha || 'N/A' }}</td>
            <td class="p-3 text-sm text-gray-700">{{ user.first_name }} {{ user.last_name }}</td>
            <td class="p-3 text-sm text-gray-700">{{ user.email }}</td>
            <td class="p-3 text-sm text-[#1e5b4f]">
              <span v-if="user.groups && user.groups.length > 0">
                {{ user.groups.join(', ') }}
              </span>
              <span v-else class="text-gray-400">Sin rol</span>
            </td>
            <td class="p-3 flex justify-center gap-3">
              <router-link :to="`/user-info/${user.id}`" class="text-gray-700 hover:text-[#1e5b4f] transition-colors" title="Ver Detalles">
                <Eye class="w-[18px] h-[18px]" />
              </router-link>
              <router-link :to="`/edit-user/${user.id}`" class="text-gray-700 hover:text-[#1e5b4f] transition-colors" title="Editar">
                <Edit class="w-[18px] h-[18px]" />
              </router-link>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="5" class="p-8 text-center text-gray-500">No se encontraron usuarios.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
