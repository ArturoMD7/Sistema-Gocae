<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import api from '../../api/axios'
import { ArrowLeft, User, Edit } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const userId = route.params.id
const userProfile = ref<any>(null)
const loading = ref(true)
const error = ref('')

const fetchUser = async () => {
  try {
    // If it's the current user, we can use the profile endpoint or the specific ID if admin
    const isCurrentUser = userId === authStore.user?.id?.toString()
    
    let response;
    if (isCurrentUser) {
      response = await api.get('user/profile/')
    } else {
      // Admin viewing someone else
      response = await api.get(`user/${userId}/`)
    }
    
    userProfile.value = response.data
  } catch (e) {
    error.value = 'Error al cargar el perfil'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchUser()
})
</script>

<template>
  <div class="p-8 max-w-3xl mx-auto">
    <div class="flex items-center gap-4 mb-6">
      <button @click="router.back()" class="p-2 text-gray-500 hover:text-[#1e5b4f] hover:bg-gray-200 rounded-full transition-colors">
        <ArrowLeft class="w-6 h-6" />
      </button>
      <h1 class="text-3xl font-bold text-[#1e5b4f]">Perfil de Usuario</h1>
    </div>

    <div v-if="error" class="bg-red-50 text-red-700 p-4 rounded-lg mb-6 border border-red-200">
      {{ error }}
    </div>

    <div v-if="loading" class="text-center text-gray-500 py-12">
      Cargando perfil...
    </div>

    <div v-else-if="userProfile" class="bg-white rounded-xl shadow-[0_2px_10px_rgba(0,0,0,0.05)] border border-[#e0e0e0] overflow-hidden">
      <!-- Cover and Avatar -->
      <div class="h-32 bg-gradient-to-r from-[#1e5b4f] to-[#024e47]"></div>
      <div class="px-8 pb-8 relative">
        <div class="absolute -top-16 left-8">
          <div class="w-32 h-32 bg-white rounded-full p-1 shadow-lg">
            <div class="w-full h-full bg-gray-100 rounded-full flex items-center justify-center overflow-hidden">
              <User v-if="!userProfile.profile_picture" class="w-16 h-16 text-gray-400" />
              <img v-else :src="userProfile.profile_picture" class="w-full h-full object-cover" />
            </div>
          </div>
        </div>

        <div class="flex justify-end pt-4 h-16">
          <router-link v-if="authStore.isAdmin" :to="`/edit-user/${userProfile.id}`" class="text-[#1e5b4f] hover:bg-[#1e5b4f]/10 px-4 py-2 rounded-lg flex items-center gap-2 font-medium transition-colors border border-[#1e5b4f]">
            <Edit class="w-4 h-4" />
            Editar Usuario
          </router-link>
        </div>

        <div class="mt-4">
          <h2 class="text-2xl font-bold text-gray-900">{{ userProfile.first_name }} {{ userProfile.last_name }}</h2>
          <p class="text-gray-500">{{ userProfile.email }}</p>
          
          <div class="mt-4 flex gap-2">
            <span v-if="userProfile.groups && userProfile.groups.length > 0" class="inline-block bg-[#1e5b4f]/10 text-[#1e5b4f] px-3 py-1 rounded-md text-sm font-semibold">
              {{ userProfile.groups.join(', ') }}
            </span>
            <span v-else class="text-gray-400 text-sm">Sin rol</span>
          </div>
        </div>

        <div class="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6 pt-6 border-t border-gray-100">
          <div>
            <h3 class="text-sm font-medium text-gray-500 mb-1">Ficha</h3>
            <p class="text-gray-900 font-medium">{{ userProfile.ficha || 'N/A' }}</p>
          </div>
          <div>
            <h3 class="text-sm font-medium text-gray-500 mb-1">Estado</h3>
            <p class="text-gray-900 font-medium">
              <span class="inline-flex items-center gap-1 text-green-700 bg-green-50 px-2 py-1 rounded-md text-sm">
                <span class="w-2 h-2 rounded-full bg-green-500"></span> Activo
              </span>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
